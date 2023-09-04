from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.db import connection
from django.core.paginator import Paginator, Page
from rest_framework.decorators import api_view
from datetime import datetime
from posts.models import Posts, PostDetail
from posts.helpers.create_post_fn import create_post


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
            content = request.data.get('content')
            published_at = request.data.get('published_at')
            image_url = request.data.get('image_url')
            status_id = request.data.get('status')
            business_id = 1

            # Create a new Posts instance and set its attributes
            new_post = Posts(
                content=content,
                published_at=published_at,
                image_url=image_url,
                status=status_id,
                business_id=business_id
            )
            
            # Save the new instance to the database
            new_post.save()

            return Response(new_post, status=status.HTTP_200_OK)

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

            return Response({'message': 'Post created.', 'post': post_data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Puedes registrar la excepción aquí para depurarla posteriormente
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)