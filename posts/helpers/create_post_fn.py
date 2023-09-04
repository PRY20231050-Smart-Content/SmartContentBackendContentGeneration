from posts.models import Posts

def create_post(post_data):
    print('create post')
    try:
        # Create a new Posts instance and set its attributes
        new_post = Posts(
            content=post_data['content'],  # Usa corchetes para acceder a las claves del diccionario
            published_at=post_data['published_at'],
            image_url=post_data['image_url'],
            status=post_data['status'],
            business_id=post_data['business_id']
        )
        
        print('create post 1')

        # Save the new instance to the database
        new_post.save()
        
        print('New post created!', new_post)

        # Convert the new_post instance to a dictionary
        post_data = {
            'id': new_post.id,
            'content': new_post.content,
            'published_at': new_post.published_at,
            'image_url': new_post.image_url,
            'status': new_post.status,
            'business_id': new_post.business_id,
        }

        return new_post, post_data, None  # Retorna el diccionario de datos del post y ningún error

    except Exception as e:
        print('Exception ', str(e))
        # Puedes registrar la excepción aquí para depurarla posteriormente
        return None, None, str(e)  # Retorna None como datos del post y el error como cadena
