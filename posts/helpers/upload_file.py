from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def upload_file(file_obj, entity_id):
    # Nombre del archivo en S3 (puede ser el mismo nombre que el archivo original)
    file_name = file_obj.name+'/'+entity_id

    try:
        file_name = default_storage.save(file_obj.name, ContentFile(file_obj.read()))
        file_url = default_storage.url(file_name)

        return file_name
    except Exception as e:
        return {str(e)}
    
    
def get_file_url(file_name):
    try:
        if file_name is None:
            return None
    
        file_url = default_storage.url(file_name)
        return file_url
    except Exception as e:
        return {str(e)}