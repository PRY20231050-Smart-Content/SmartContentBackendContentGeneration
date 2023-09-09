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
    return textos_con_coincidencias  # Devolvemos la lista de diccionarios completos sin IDs repetidos


def devuelve_las_mejores_coincidencias(textos, detalles_post, post,size,return_size):
    textos_coincidentes = encontrar_coincidencias_con_sinonimos(textos, detalles_post.post_keywords)

    # Ordenar la lista de textos por puntaje en orden descendente
    textos_coincidentes.sort(
        key=lambda x: (0.4 * int(x["likes"]) + 0.6 * int(x["shared"])), reverse=True
    )

    # Seleccionar los tres mejores textos
    mejores_textos = textos_coincidentes[:size]
    
    messages = [
    {"role": "system", "content": "You are a social media marketer."},
    {"role": "user", "content": "Create a compelling Facebook post for a floor cleaning service."},
    {"role": "assistant", "content": "Tired of old floor stains ruining your business's appearance? Say goodbye to dirt, grime, and wax buildup with our professional floor cleaning services! ✨\n\nWe use advanced techniques and state-of-the-art equipment to deep clean and restore all types of flooring surfaces. Save time and energy – let us handle the scrubbing while you focus on what you do best! 💼\n\nContact us today for a free consultation:\n📲 Call (951) 403 4384, (909) 258 1797, or (909) 485 6647\n📩 Email: frankjaviord@gmail.com"},
    {"role": "user", "content": "Create another Facebook post for floor cleaning."},
    {"role": "assistant", "content": "Transform your business's appearance with our top-notch floor stripping and waxing services! 💫 Spotless Cleaning Services understands the importance of leaving a lasting impression on your clients. Whether it's an office, store, or business center, our highly skilled team ensures every inch shines brightly. Don't miss out on our exclusive promotion!\n\nContact us today for a free consultation:\n📲 Call (951) 403 4384, (909) 258 1797, or (909) 485 6647\n📩 Email: frankjaviord@gmail.com"},
    {"role": "user", "content": "Create a Facebook post for construction debris removal."},
    {"role": "assistant", "content": "Construction debris can pose risks to your site's safety and stability. From trip hazards to health concerns, it's crucial to handle it safely. That's where we come in!\n\nOur expert team ensures a spotless construction site, handling everything from debris removal to meticulous surface cleaning. Rest easy knowing your site is secure.\n\nContact us today for a free consultation:\n📲 Call (951) 403 4384, (909) 258 1797, or (909) 485 6647\n📩 Email: frankjaviord@gmail.com"}
    ]
    
    respuesta_ia= open_ia(1,messages,3)

    return respuesta_ia


def open_ia(temperature, messages,tamano_respuesta):
    
#  URL de la API de OpenAI
    openai.api_key = "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"

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,n=tamano_respuesta,max_tokens=150,temperature=temperature)
    
    print(json.dumps(completion.choices))

    for choice in completion.choices:
        print(choice.message.content)
        
    return completion.choices
    
    

    