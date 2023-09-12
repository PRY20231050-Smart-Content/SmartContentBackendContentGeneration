from posts.models import Posts
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import pandas as pd
import requests
import json
import openai


def create_post(post_data):
    print("create post")
    try:
        # Create a new Posts instance and set its attributes
        new_post = Posts(
            content=post_data[
                "content"
            ],  # Usa corchetes para acceder a las claves del diccionario
            published_at=post_data["published_at"],
            image_url=post_data["image_url"],
            status=post_data["status"],
            business_id=post_data["business_id"],
        )

        print("create post 1")

        # Save the new instance to the database
        new_post.save()

        print("New post created!", new_post)

        # Convert the new_post instance to a dictionary
        post_data = {
            "id": new_post.id,
            "content": new_post.content,
            "published_at": new_post.published_at,
            "image_url": new_post.image_url,
            "status": new_post.status,
            "business_id": new_post.business_id,
        }

        return (
            new_post,
            post_data,
            None,
        )  # Retorna el diccionario de datos del post y ningún error

    except Exception as e:
        print("Exception ", str(e))
        # Puedes registrar la excepción aquí para depurarla posteriormente
        return (
            None,
            None,
            str(e),
        )  # Retorna None como datos del post y el error como cadena


# Descargar datos de nltk (si no se han descargado previamente)


# Función para obtener sinónimos de una palabra
def obtener_sinonimos(palabra):
    sinonimos = []
    for syn in wordnet.synsets(palabra):
        for lemma in syn.lemmas():
            sinonimos.append(lemma.name())
    return sinonimos


# Definición de la función encontrar_coincidencias_con_sinonimos
def encontrar_coincidencias_con_sinonimos(textos, palabras_clave):
    textos_con_coincidencias = (
        []
    )  # Usamos una lista para almacenar los textos con coincidencias
    ids_agregados = (
        set()
    )  # Usamos un conjunto para mantener un registro de los IDs agregados
    for texto in textos:
        palabras_texto = word_tokenize(
            texto["copy"].lower()
        )  # Accedemos al texto con 'copy'
        for palabra_clave in palabras_clave:
            if palabra_clave.lower() in palabras_texto:
                if texto["id"] not in ids_agregados:
                    textos_con_coincidencias.append(
                        texto
                    )  # Agregamos el diccionario completo
                    ids_agregados.add(texto["id"])  # Agregamos el ID al conjunto
            else:
                sinonimos = obtener_sinonimos(palabra_clave)  # Obtener sinonimos
                for sinonimo in sinonimos:
                    if sinonimo.lower() in palabras_texto:
                        if texto["id"] not in ids_agregados:
                            textos_con_coincidencias.append(
                                texto
                            )  # Agregamos el diccionario completo
                            ids_agregados.add(
                                texto["id"]
                            )  # Agregamos el ID al conjunto
                            break  # Rompe el bucle si encuentra una coincidencia
    if len(textos_con_coincidencias) == 0:
        return textos  # Devolvemos la lista de diccionarios completa si no hay coincidencias
    else:                    
        return textos_con_coincidencias  # Devolvemos la lista de diccionarios completos sin IDs repetidos

def cantidad_palabras(texto):
    if texto == 'Short':
        return 30
    elif texto == 'Medium':
        return 90
    elif texto == 'High':
        return 150
    else:
        return 30

def devuelve_las_mejores_coincidencias(textos, detalles_post,size,return_size):
    
    
    textos_coincidentes = encontrar_coincidencias_con_sinonimos(textos, detalles_post[0]['post_keywords'])

    # Ordenar la lista de textos por puntaje en orden descendente
    textos_coincidentes.sort(
        key=lambda x: (0.4 * int(x["likes"]) + 0.6 * int(x["shared"])), reverse=True
    )

    # Seleccionar los tres mejores textos
    mejores_textos = textos_coincidentes[:size]
    
    # messages role assistant deberia tener la misma cantidad que mejores_textos
    print("detalles_post",detalles_post)
    
    messages = []
        # Determinar el idioma del mensaje de sistema
    if detalles_post[0]['post_language'] == 'Spanish':
        # Crear un mensaje de sistema en español
        system_message = {
            "role": "system",
            "content": f"Eres un creador de contenido experto en publicaciones para facebook en el idioma {detalles_post[0]['post_language']} de máximo {cantidad_palabras(detalles_post[0]['post_copy_size'])} tokens de longitud. Con la siguientes caracteristicas:"
        }
    else:
        # Crear un mensaje de sistema en inglés por defecto
        system_message = {
            "role": "system",
            "content": f"You are an expert content creator for facebook in the language {detalles_post[0]['post_language']} with a maximum of {cantidad_palabras(detalles_post[0]['post_copy_size'])} tokens in length. With the following characteristics:"
        }

    # Verificar si no se deben usar emojis y agregar esa parte al mensaje
    if detalles_post[0]['post_use_emojis'] == 'no' and detalles_post[0]['post_language'] == 'Spanish':
        system_message["content"] += " No usa emojis en su contenido."
    elif detalles_post[0]['post_use_emojis'] == 'no' and detalles_post[0]['post_language'] == 'English':
        system_message["content"] += " Does not use emojis in its content."
    elif detalles_post[0]['post_use_emojis'] == 'yes' and detalles_post[0]['post_language'] == 'Spanish':
        system_message["content"] += " Usa emojis en su contenido."
    else:
        system_message["content"] += " Uses emojis in its content."
    # Agregar el mensaje de sistema a la lista de mensajes
    messages.append(system_message)
    
    
    for texto in mejores_textos:
        #si es el ultimo mensaje
        messages.append({"role": "user", "content": "Aqui tienes un ejemplo de copy para un post de tu negocio"})   
        messages.append({"role": "assistant", "content": texto["copy"]})
      
        # Crear un mensaje de usuario con los detalles del post si tienen datos
    # Si hay detalles de post, agregar un mensaje de usuario con los detalles
    if detalles_post:
        # Crear un mensaje de usuario con los detalles del post inglés por defecto
        
        if detalles_post[0]['post_language'] == 'Spanish':
           user_message = {
            "role": "user",
            "content": "Genera un copy para mi post con las siguientes características:\n"
            }
           # Definir una lista de campos a incluir español
           campos_a_incluir = [
                 ('Ocasion', detalles_post[0]['post_ocassion']),
                 ('Promocion', detalles_post[0]['post_promo']),
                 ('Objetivo', detalles_post[0]['post_objective']),
                 ('Palabras Clave', detalles_post[0]['post_keywords']),
                 ('Incluir Información del Negocio', detalles_post[0]['post_include_business_info']),
                 ('Productos a Incluir', detalles_post[0]['products_to_include']),
                ]
           for campo, valor in campos_a_incluir:
                if valor and (campo != 'Palabras Clave' or valor != '[]') and (campo != 'Incluir Información del Negocio' or valor != 'no') and (campo != 'Productos a Incluir' or valor != '[]'):
                 user_message["content"] += f"{campo}: {valor}\n"
        
        else:
            user_message = {
            "role": "user",
            "content": "Generate a copy for my post with the following characteristics:\n"
            }
            
            # Definir una lista de campos a incluir
            campos_a_incluir = [
                ('Ocassion', detalles_post[0]['post_ocassion']),
                ('Promo', detalles_post[0]['post_promo']),
                ('Objective', detalles_post[0]['post_objective']),
                ('Keywords', detalles_post[0]['post_keywords']),
                ('Include Business Info', detalles_post[0]['post_include_business_info']),
                ('Products to Include', detalles_post[0]['products_to_include']),
            ]
                # Agregar los campos si tienen datos
            for campo, valor in campos_a_incluir:
                if valor and (campo != 'Keywords' or valor != '[]') and (campo != 'Include Business Info' or valor != 'no') and (campo != 'Products to Include' or valor != '[]'):
                 user_message["content"] += f"{campo}: {valor}\n"
        
       

        # Agregar el mensaje de usuario a la lista de mensajes
        messages.append(user_message)
    
    print("messages",messages)
    
    respuesta_ia= open_ia(detalles_post[0]['post_creativity']/5 ,messages,3)

    return respuesta_ia


def open_ia(temperature, messages,tamano_respuesta):
    
#  URL de la API de OpenAI
    openai.api_key = "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"

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,n=tamano_respuesta,max_tokens=150,temperature=temperature)
       
    return completion.choices
    
    

    