from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.db import connection
from django.core.paginator import Paginator, Page
from rest_framework.decorators import api_view
from datetime import datetime
from posts.models import Posts, PostDetail, Messages
from posts.helpers.create_post_fn import create_post
from posts.helpers.create_post_fn import devuelve_las_mejores_coincidencias


class PostsView(APIView):

     def post(self, request):
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
                    'content': row[1],
                    'created_at': row[2],
                    'published_at': row[3],
                    'image_url': row[4],
                    'status': row[5],
                    'business_name': row[6],
                    'cc': row[7]
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
                    'total': data[0][-1]  # as the total count is the last element of each row
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



class SavePostView(APIView):
    def post(self, request):
        try:
            post_id = request.data.get('postId')
            content = request.data.get('content')
            published_at = request.data.get('published_at')
            image_url = request.data.get('image_url')
            status_id = request.data.get('status')

            # Busca el post existente en la base de datos por su ID
            try:
                existing_post = Posts.objects.get(id=post_id)
            except Posts.DoesNotExist:
                return Response({'error': 'El post que intentas actualizar no existe.'}, status=status.HTTP_404_NOT_FOUND)

            # Actualiza los campos del post existente
            existing_post.content = content
            existing_post.published_at = published_at
            existing_post.image_url = image_url
            existing_post.status = status_id

            # Guarda los cambios en el post existente
            existing_post.save()

            return Response({'message': 'Post actualizado.'}, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log the exception here for debugging purposes
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostChatView(APIView):
    def get(self, request, post_id):
        try:
            post_id = post_id

            # Create a new Posts instance and set its attributes
            with connection.cursor() as cursor:
                cursor.execute("CALL get_post_chat(%s)", [post_id])
                data = cursor.fetchall()
                
                if data:
                    formatted_data = [
                        {
                            'message': row[0],
                            'chosen': row[1],
                            'senderId': row[2],
                            'time': row[3],
                        } for row in data
                    ]
                    
                    post_history_chat = {
                        "id": 'user',
                        "userId": 'user',
                        "chat": formatted_data
                    }


            return Response(data, status=status.HTTP_200_OK)

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
                'content': '',
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
            )
            post_detail.save()  # Guarda el detalle del post en la base de datos
            
            ##traer todos los copies por negocio
            with connection.cursor() as cursor:
              cursor.execute(""" SELECT c.id,c.copy, c.likes, c.shared  FROM copies c WHERE c.business_id = %s  """, [business_id])
              data = cursor.fetchall()
              data_list = [{'id': row[0],'copy': row[1], 'likes': row[2], 'shared': row[3]} for row in data]

                
              mejores_textos=  devuelve_las_mejores_coincidencias(data_list,post_keywords, 3)
            

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
                }

            return Response(post_data, status=status.HTTP_200_OK)

        except Exception as e:
            # You can log the exception here for debugging purposes
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MessageTemplateView(APIView):
    def post(self, request):
        try:
            # POST
            post_id = request.data.get('postId')
            message_content = request.data.get('messageContent')
            role_name = request.data.get('roleName')
                        
            new_message = Messages(
                content=message_content,  
                post= post_id,
                role=role_name,
            )
            new_message.save()  # Guarda el detalle del post en la base de datos

            return Response({'message': 'Message created.'}, status=status.HTTP_200_OK)

        except Exception as e:
            # Puedes registrar la excepción aquí para depurarla posteriormente
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)