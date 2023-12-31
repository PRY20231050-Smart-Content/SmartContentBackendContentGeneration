from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.db import connection, transaction
from django.core.paginator import Paginator, Page
from rest_framework.decorators import api_view
from datetime import datetime
from posts.models import Posts, PostDetail, Messages, SurveyQuestion, PostSurvey, PostSurveyAnswer
from posts.helpers.create_post_fn import create_post
from posts.helpers.create_post_fn import devuelve_las_mejores_coincidencias
from posts.helpers.create_post_fn import creador_de_mensajes
from posts.helpers.upload_file import upload_file, get_file_url
from django.utils import timezone
# from botocore.exceptions import NoCredentialsError, PartialCredentialsError, S3UploadFailedError

import json
import boto3
from rest_framework.parsers import FileUploadParser
from django.conf import settings  # Importa la configuración de settings.py
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
class PostsView(APIView):

     def post(self, request):
         #prueba8
        page = request.data.get('npage', 1)
        perpage = request.data.get('perPage', 10)
        sortby = request.data.get('sortBy', 'created_at')
        sortOrder = request.data.get('sortOrder', 'ASC')
        filterDateFrom = request.data.get('dateFrom')
        if filterDateFrom:
            # Parse the date string to a datetime object
            filterDateFrom = datetime.strptime(filterDateFrom, '%m/%d/%Y')

            # Format the datetime object to a different format
            filterDateFrom = filterDateFrom.strftime('%Y-%m-%d')  # Format as 'day-month-year'

            # Now 'formatted_date' contains the date in the desired format
        else:
            filterDateFrom = None  # If 'filterDateFrom' is not provided

        filterDateTo = request.data.get('dateTo')
        if filterDateTo:
            # Parse the date string to a datetime object
            filterDateTo = datetime.strptime(filterDateTo, '%m/%d/%Y')

            # Format the datetime object to a different format
            filterDateTo = filterDateTo.strftime('%Y-%m-%d')   # Format as 'day-month-year'

            # Now 'formatted_date' contains the date in the desired format
        else:
            filterDateTo = None  # If 'filterDateTo' is not provided

        text = request.data.get('text', None)
        businessId = request.data.get('businessId', None)
        clientId = request.data.get('clientId', None)
        userId = request.data.get('userId', None)
        statusId = request.data.get('statusId', None)

        params = [
            
            text,
            filterDateFrom,
            filterDateTo,
            perpage,
            page,
            sortby,
            sortOrder,
            businessId,
            clientId,
            userId,
            statusId
        ]
        print('params', params)
      
        try:
            with connection.cursor() as cursor:
                cursor.callproc('sp_get_posts', params)
                data = cursor.fetchall()
                

            if data:
                paginator = Paginator(data, perpage)
                data_page = paginator.get_page(page)
                print('paginator', paginator)
                print('data_page', data_page)


                formatted_data = [
                 {
                    'id': row[0],
                    'content': json.loads(row[1]),
                    'created_at': row[2],
                    'published_at': row[3],
                    'image_url': get_file_url(row[4]),
                    'status': row[5],
                    'business_name': row[6],
                    'cc': row[7],
                    'business_image': get_file_url(row[8]),
                    'last_survey_id': row[9],
                 } for row in data_page
                ]


                result = {
                    'current_page': data_page.number,
                    'data': formatted_data,
                    'first_page_url': request.build_absolute_uri(f'?page=1'),
                    'from': data_page.start_index(),
                    'last_page': data_page.paginator.num_pages,
                    'last_page_url': request.build_absolute_uri(f'?page={data_page.paginator.num_pages}'),
                    'next_page_url': request.build_absolute_uri(data_page.next_page_number()) if data_page.has_next() else None,
                    'path': request.path,
                    'per_page': perpage,
                    'prev_page_url': request.build_absolute_uri(data_page.previous_page_number()) if data_page.has_previous() else None,
                    'to': data_page.end_index(),
                    'total': data[0][-3]  # as the total count is the last element of each row
                }

                return Response(result, status=status.HTTP_200_OK)

            result = {
                    'current_page': page,
                    'data': [],
                    'first_page_url': '',
                    'from': 0,
                    'last_page': 0,
                    'last_page_url': '',
                    'next_page_url': '',
                    'path': '',
                    'per_page': perpage,
                    'prev_page_url': '',
                    'to': 0,
                    'total': 0  # as the total count is the last element of each row
                }
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     def delete(self, request, post_id):
        try:
            # Busca el post existente en la base de datos por su ID
            try:
                existing_post = Posts.objects.get(id=post_id)
            except Posts.DoesNotExist:
                return Response({'error': 'El post que intentas actualizar no existe.'}, status=status.HTTP_404_NOT_FOUND)

            # Actualiza los campos del post existente
            existing_post.deleted_at = timezone.now()
            # Guarda los cambios en el post existente
            existing_post.save()

            return Response({'message': 'Post eliminado.'}, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log the exception here for debugging purposes
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SavePostView(APIView):
    def post(self, request):
        try:
            post_id = request.data.get('postId')
            content = request.data.get('content')
            print('content', content)
            content_with_quotes = f'"{content}"'
            published_at = request.data.get('published_at')
            file_obj = request.data.get('image')
            status_id = request.data.get('status')

            # Busca el post existente en la base de datos por su ID
            try:
                existing_post = Posts.objects.get(id=post_id)
            except Posts.DoesNotExist:
                return Response({'error': 'El post que intentas actualizar no existe.'}, status=status.HTTP_404_NOT_FOUND)

            # Actualiza los campos del post existente
            existing_post.content = json.dumps(content)
            existing_post.published_at = published_at
            existing_post.status = status_id
            
            if file_obj is not None:
                file_name = upload_file(file_obj)
                existing_post.image_url = file_name
            
            # Guarda los cambios en el post existente
            existing_post.save()

            return Response({'message': 'Post actualizado.'}, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log the exception here for debugging purposes
            print('str(e) ', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostChatView(APIView):
    def get(self, request, post_id):
        try:
            post_id = post_id

            # Create a new Posts instance and set its attributes
            with connection.cursor() as cursor:
                cursor.execute("CALL get_post_chat(%s)", [post_id])
                data = cursor.fetchall()
                formatted_data= []
                
                if data:
                    formatted_data = [
                        {
                            'message': json.loads(row[0]),
                            'chosen': row[1],
                            'senderId': row[2],
                            'time': row[3],
                            'selectable': row[4],
                            'id': row[5],
                        } for row in data
                    ]

            return Response(formatted_data, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log the exception here for debugging purposes
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PostTemplateView(APIView):
    def post(self, request):
        try:
            # POST
            status_id = 'draft' # default when creating a post
            business_id = request.data.get('businessId')            
            post_data = {
                'content': '""',
                'published_at': None,
                'image_url': None,
                'status': status_id,
                'business_id': business_id
            }
            
            post_object, post_data, error = create_post(post_data)

            # POST DETAIL
            
            post_ocassion = request.data.get('ocassion')
            post_promo = request.data.get('promo')
            post_objective = request.data.get('objective')
            post_language = request.data.get('language')
            post_use_emojis = request.data.get('useEmojisAnswer')
            post_keywords = request.data.get('keywords')
            post_creativity = request.data.get('creativityLevel')
            post_copy_size = request.data.get('copySize')
            post_include_business_info = request.data.get('includeBusinessInfo')
            post_products_to_include = request.data.get('productsToInclude')
            post_products_to_include_names = request.data.get('productsToIncludeNames')

            post_detail = PostDetail(
                post=post_object,  # Asocia esta instancia de PostDetail con el post que creaste en el paso 1
                post_ocassion= post_ocassion,
                post_promo=post_promo,
                post_objective=post_objective,
                post_language=post_language,  # Ejemplo de elección de idioma
                post_copy_size=post_copy_size,  # Ejemplo de tamaño de copia
                post_use_emojis=post_use_emojis,  # Ejemplo de elección de emojis
                post_creativity=post_creativity,  # Ejemplo de creatividad
                post_keywords=post_keywords,  # Ejemplo de palabras clave como una lista JSON
                post_include_business_info=post_include_business_info,  # Ejemplo de inclusión de información de negocios
                products_to_include=post_products_to_include,
                products_to_include_names=post_products_to_include_names,
            )
            post_detail.save()  # Guarda el detalle del post en la base de datos
            
            ##traer todos los copies por negocio
            with connection.cursor() as cursor:
              cursor.execute(""" SELECT c.id,c.copy, c.likes, c.shared  FROM copies c WHERE c.business_id = %s  """, [business_id])
              data = cursor.fetchall()
              print(data)
              lista_de_copies = [{'id': row[0],'copy': row[1], 'likes': row[2], 'shared': row[3]} for row in data]

              print('lista_de_copies',lista_de_copies)
              
              
            with connection.cursor() as cursor:
              cursor.execute(""" SELECT pp.id,pp.post_ocassion,pp.post_promo,pp.post_objective,pp.post_language,pp.post_use_emojis,pp.post_keywords,pp.post_creativity,
                             pp.post_copy_size,pp.post_include_business_info,pp.post_id,pp.products_to_include,pp.products_to_include_names,
                             b.name,b.target_audience,b.facebook_page,b.phone,b.website,b.mail,b.schedule,b.mission,b.vision,b.logo_carpet,	i.name industry_name
                             FROM posts_postdetail pp join posts_posts ppp on ppp.id= pp.post_id
                                 join businesses b on ppp.business_id = b.id join industries i on i.id=b.industry_id WHERE pp.post_id = %s  """, [post_object.id])
              data_post_detalle = cursor.fetchall()
              datos_post_detalle = [{'id': row[0],'post_ocassion': row[1], 'post_promo': row[2], 'post_objective': row[3], 'post_language': row[4], 'post_use_emojis': row[5], 'post_keywords': row[6], 'post_creativity': row[7], 'post_copy_size': row[8], 'post_include_business_info': row[9], 'post_id': row[10], 'products_to_include': row[11], 'products_to_include_names':row[12],
                             'name': row[13], 'target_audience': row[14], 'facebook_page': row[15], 'phone': row[16], 'website': row[17], 'mail': row[18], 'schedule': row[19], 'mission': row[20], 'vision': row[21], 'logo_carpet': row[22], 'industry_name': row[23]} for row in data_post_detalle]
              
              print('datos_post_detalle', datos_post_detalle)

                
            mejores_textos=  devuelve_las_mejores_coincidencias(lista_de_copies,datos_post_detalle,3, 3)
              
            mensaje_predeterminado = 'Bienvenido! Escoge entre estas opciones'
            
            with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO posts_messages (content, created_at, `role`, chosen, post_id,selectable)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        [json.dumps(mensaje_predeterminado), datetime.now(), 'system', 0, post_object.id, 'no']
                    )
            
            for choice in mejores_textos:
                
                content = choice['message']['content']
                
               
                # print('content', message['role'])

                # Realiza la inserción en la tabla posts_messages
                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO posts_messages (content, created_at, `role`, chosen, post_id,selectable)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        [json.dumps(content), datetime.now(), 'system', 0, post_object.id, 'yes']
                    )
                               
            

            return Response({'message': 'Post created.', 'post': post_data,'mejores_textos':mejores_textos}, status=status.HTTP_200_OK)

        except Exception as e:
            # Puedes registrar la excepción aquí para depurarla posteriormente
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PostDetailView(APIView):
    def get(self, request, post_id):
        try:
            post_id = post_id

            with connection.cursor() as cursor:
                cursor.execute("CALL get_post_detail(%s)", [post_id])
                data = cursor.fetchall()
                print('post detail', data)
                print('post detail', data[0][0])

                post_data = {
                    'ocassion': data[0][0],
                    'promo': data[0][1],
                    'objective': data[0][2],
                    'language': data[0][3],
                    'useEmojisAnswer': data[0][4],
                    'creativityLevel': data[0][5],
                    'keywords': data[0][6],
                    'productsToInclude': data[0][7],
                    'includeBusinessInfo': data[0][8],
                    'copySize': data[0][9],
                    'businessId': data[0][10],
                    'clientId': data[0][11],
                    'postStatus': data[0][12],
                    'productsToInclude': data[0][13],
                }

            return Response(post_data, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log the exception here for debugging purposes
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MessageTemplateView(APIView):
    def post(self, request):
        try:
            print('post')
            # POST
            post_id = request.data.get('postId')
            message_content = request.data.get('messageContent')
            message_content_with_quotes = f'"{message_content}"'
            role_name = request.data.get('roleName')
            
            try:
                existing_post = Posts.objects.get(id=post_id)
            except Posts.DoesNotExist:
                return Response({'error': 'El post que intentas actualizar no existe.'}, status=status.HTTP_404_NOT_FOUND)
                        
            new_message = Messages(
                content=message_content_with_quotes,  
                post= existing_post,
                role=role_name,
                created_at=timezone.now()
            )
            new_message.save()  # Guarda el detalle del post en la base de datos
            
            mensaje_predeterminado = 'Nuevo copy mejorado! en base a las indicaciones'
            
            with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO posts_messages (content, created_at, `role`, chosen, post_id,selectable)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        [json.dumps(mensaje_predeterminado), datetime.now(), 'system', 0, post_id, 'no']
                    )
            
            with connection.cursor() as cursor:
                        cursor.execute(""" SELECT id,content,role FROM posts_messages pm   WHERE post_id = %s AND chosen = 1;
                                        """, [post_id])
                        data_posts_messages_chosen = cursor.fetchall()
                        datos_posts_messages_choseen = [{'id': row[0],'content': row[1], 'role': row[2]} for row in data_posts_messages_chosen]
                        
            with connection.cursor() as cursor:
                        cursor.execute(""" SELECT id,content,role FROM posts_messages pm
                                            WHERE post_id = %s AND chosen <> 1;  
                                        """, [post_id])
                        data_posts_messages = cursor.fetchall()
                        datos_posts_messages = [{'id': row[0],'content': row[1], 'role': row[2]} for row in data_posts_messages]
             
            with connection.cursor() as cursor:
              cursor.execute(""" SELECT pp.id,pp.post_ocassion,pp.post_promo,pp.post_objective,pp.post_language,pp.post_use_emojis,pp.post_keywords,pp.post_creativity,
                             pp.post_copy_size,pp.post_include_business_info,pp.post_id,pp.products_to_include,pp.products_to_include_names,
                             b.name,b.target_audience,b.facebook_page,b.phone,b.website,b.mail,b.schedule,b.mission,b.vision,b.logo_carpet,	i.name industry_name
                             FROM posts_postdetail pp join posts_posts ppp on ppp.id= pp.post_id
                                 join businesses b on ppp.business_id = b.id join industries i on i.id=b.industry_id WHERE pp.post_id = %s  """, [post_id])
              data_post_detalle = cursor.fetchall()
              datos_post_detalle = [{'id': row[0],'post_ocassion': row[1], 'post_promo': row[2], 'post_objective': row[3], 'post_language': row[4], 'post_use_emojis': row[5], 'post_keywords': row[6], 'post_creativity': row[7], 'post_copy_size': row[8], 'post_include_business_info': row[9], 'post_id': row[10], 'products_to_include': row[11], 'products_to_include_names':row[12],
                             'name': row[13], 'target_audience': row[14], 'facebook_page': row[15], 'phone': row[16], 'website': row[17], 'mail': row[18], 'schedule': row[19], 'mission': row[20], 'vision': row[21], 'logo_carpet': row[22], 'industry_name': row[23]} for row in data_post_detalle]
              
              print('datos_post_detalle', datos_post_detalle)  
                        
            contenido_a_insertar = creador_de_mensajes(datos_posts_messages_choseen,datos_posts_messages,datos_post_detalle)
            
            
            for choice in contenido_a_insertar:
                
                content = choice['message']['content']
                # Realiza la inserción en la tabla posts_messages
                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO posts_messages (content, created_at, `role`, chosen, post_id,selectable)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        [json.dumps(content), datetime.now(), 'system', 0, post_id, 'yes']
                    )
            return Response({'message': 'Message created.'}, status=status.HTTP_200_OK)

        except Exception as e:
            # Puedes registrar la excepción aquí para depurarla posteriormente
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def put(self, request):
        print('put')
        try:
            # POST
            message_id = request.data.get('id')
            chosen = request.data.get('chosen')
            post_id = request.data.get('postId')

            with transaction.atomic():  # Use a transaction to ensure data consistency

                try:
                    # Find the post that corresponds to the selected message
                    selected_message = Messages.objects.get(id=message_id)
                except Messages.DoesNotExist:
                    return Response({'error': 'El mensaje que intentas actualizar no existe.'}, status=status.HTTP_404_NOT_FOUND)
                
                # Update the chosen field for the selected message
                selected_message.chosen = chosen
                selected_message.save()

                # Get all messages belonging to the same post
                other_messages = Messages.objects.filter(post_id=post_id).exclude(id=message_id)

                # Update the chosen field for all other messages to 0
                other_messages.update(chosen=0)

            return Response({'message': 'Message updated.'}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle exceptions here
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SurveyQuestionsTemplateView(APIView):
    def get(self, request):
        questions = SurveyQuestion.objects.all().values('id', 'name')
        questions_list = list(questions)
        # Rename 'text' to 'name' and add 'answer' field (set to None) in each question
        for question in questions_list:
            question['text'] = question.pop('name')
            question['answer'] = None  # Set answer to None
        return JsonResponse(questions_list, safe=False)

    def post(self, request):
        try:
            # Assuming you have the post_id and answers array in your request data
            post_id = request.data.get('postId')
            answers = request.data.get('answers')

            # Create the PostSurvey object
            post_survey = PostSurvey.objects.create(name="Survey Name", post_id=post_id)

            # Loop through the answers and create PostSurveyAnswer objects
            for answer in answers:
                answer_id = answer.get('id')
                answer_number = answer.get('answer')
                try:
                    # Find the post that corresponds to the selected message
                    selected_question = SurveyQuestion.objects.get(id=answer_id)
                except Messages.DoesNotExist:
                    return Response({'error': 'La pregunta que intentas buscar no existe.'}, status=status.HTTP_404_NOT_FOUND)
                # Create a PostSurveyAnswer associated with the PostSurvey
                PostSurveyAnswer.objects.create(post_survey=post_survey, survey_question=selected_question, answer = answer_number)

            return Response({'message': 'Survey created successfully', 'post_survey_id': post_survey.id}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle exceptions
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SurveyAnswersTemplateView(APIView):
    def get(self, request, post_survey_id):
        try:
            # Get PostSurveyAnswer objects based on post_survey_id
            post_survey_answers = PostSurveyAnswer.objects.filter(post_survey_id=post_survey_id)
            
            # Create a list to store the results
            questions_list = []

            # Loop through PostSurveyAnswer objects
            for post_survey_answer in post_survey_answers:
                # Retrieve the related SurveyQuestion
                survey_question = SurveyQuestion.objects.get(id=post_survey_answer.survey_question_id)
                
                # Create a dictionary with the required fields
                question_data = {
                    'id': survey_question.id,
                    'text': survey_question.name,
                    'answer': post_survey_answer.answer
                }

                questions_list.append(question_data)

            return JsonResponse(questions_list, safe=False)

        except Exception as e:
            # Handle exceptions
            return JsonResponse({'error': str(e)}, status=500)
        

class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file_obj = request.data['file']
        try:
            file_url = upload_file(file_obj)
            return Response({'file_url': file_url})
        except Exception as e:
            return Response({'error': 'Error al subir el archivo a S3: ' + {str(e)}}, status=500)
        
        
class FileUploadThunder(APIView):
    def post(self, request, *args, **kwargs):
        try:
            file_name = request.data['file_name']
            file_url = default_storage.url(file_name)
            return Response({'file_url': file_url})
        except Exception as e:
            return Response({'error': 'Error al subir el archivo a S3: ' + {str(e)}}, status=500)