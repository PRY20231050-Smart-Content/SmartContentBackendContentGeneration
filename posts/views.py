from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.db import connection
from django.core.paginator import Paginator, Page
from rest_framework.decorators import api_view


class PostsView(APIView):
    # def post(self, request):
    #     try:
    #         first_name = request.data.get('first_name')
    #         last_name = request.data.get('last_name')
    #         address_id = request.data.get('address_id')
    #         email = request.data.get('email')
    #         phone = request.data.get('phone')
    #         profile_picture = request.data.get('profile_picture')
    #         user_id = request.data.get('user_id')

    #         with connection.cursor() as cursor:
    #              cursor.execute("CALL insert_client(%s, %s, %s, %s, %s, %s, %s)", [first_name, last_name, address_id, email, phone, profile_picture, user_id])

    #         return Response({'message': 'Client created.'}, status=status.HTTP_201_CREATED)

    #     except Exception as e:
    #         # Puedes registrar la excepción aquí para depurarla posteriormente
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def put(self, request):
    #     try:
    #         client_id = request.data.get('client_id')
    #         first_name = request.data.get('first_name')
    #         last_name = request.data.get('last_name')
    #         address_id = request.data.get('address_id')
    #         email = request.data.get('email')
    #         phone = request.data.get('phone')
    #         profile_picture = request.data.get('profile_picture')
    #         user_id = request.data.get('user_id')

    #         with connection.cursor() as cursor:
    #              cursor.execute("CALL update_client(%s, %s, %s, %s, %s, %s, %s, %s)", [client_id, first_name, last_name, address_id, email, phone, profile_picture, user_id])
            
    #         return Response({'message': 'Client updated.'}, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         # Puedes registrar la excepción aquí para depurarla posteriormente
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        page = request.data.get('npage', 1)
        perpage = request.data.get('perPage', 10)
        sortby = request.data.get('sortBy', 'created_at')
        sortOrder = request.data.get('sortOrder', 'ASC')
        filterDateFrom = request.data.get('date_from')
        filterDateTo = request.data.get('date_to')
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
                    'cc': row[6]
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

    # def getClientById(self, request, client_id):
    #     try:
    #         with connection.cursor() as cursor:
    #             cursor.execute("SELECT * FROM clients WHERE id = %s", [client_id])
    #             data = cursor.fetchone()

    #         if data:
    #             client_details = {
    #                 'id': data[0],
    #                 'first_name': data[1],
    #                 'last_name': data[2],
    #                 'address_id': data[3],
    #                 'email': data[4],
    #                 'phone': data[5],
    #                 'profile_picture': data[6],
    #                 'user_id': data[7],
    #                 # Include other fields as needed
    #             }

    #             return Response(client_details, status=status.HTTP_200_OK)

    #         return Response({'message': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)

    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)