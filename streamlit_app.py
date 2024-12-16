import streamlit as st
import pandas as pd
import re  
import os
from PIL import Image
import base64
from io import BytesIO
import datetime
import copy
from groq import Groq
from datetime import date
import requests

hoy = date.today()

ruta_imagen = "https://i.ibb.co/vcgGs9B/a10.png"

api_key = "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"
modelo = 'llama-3.1-70b-versatile'

# Inicializa el cliente de Groq usando la clave API
client = Groq(
    api_key=api_key,
)


def limpiar_texto(texto):
    #Limpia una cadena de texto
    #Quita (, . ;)
    texto = re.sub(r",", "", texto)
    texto = re.sub(r"\.", "", texto)
    texto = re.sub(r";", "", texto)
    texto = re.sub(r":", "", texto)
    texto = re.sub(r"¢", "o", texto)
    texto = re.sub(r"'", "", texto)
    texto = re.sub(r"~", "", texto)
    texto = re.sub(r"ñ", "n", texto)
    texto = re.sub(r"Ñ", "n", texto)
    #texto = re.sub(r")", "", texto)
    texto = re.sub(r"-", "", texto)
    
    #Elimino numeros de la cadena
    #texto = re.sub(r'[0-9]+', '', texto)
    
    #Elimino espacio de mas y tabulaciones
    texto = re.sub(r"\s", " ", texto)
    texto = re.sub(r"( ){2,}", " ", texto)
    texto = re.sub(r"\A ", "", texto)
    texto = re.sub(r'\n\s*\n', '\n', texto)
    #Quitamos acentos
    texto = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
        normalize( "NFD", texto), 0, re.I
        )
    #Dejamos todas las letras en minusculas
    texto = texto.lower()
    
    return texto


def generar_resumen(pregunta, horoscopo):

    prompt = f"""
    Respecto a este comentario: {horoscopo},
    responde esta pregunta, sin detalles metodológicos:
    {pregunta}
    """   
    MODEL = modelo
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "Eres uastrólogo y experto en etimología de nombres."
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        #tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message.content
    
    return response_message

def generar_recomendacion(nombre):
    prompt = f"""
    
    Hola, mi nombre es {nombre} (Si está vacío o el nombre no existe solicita que lo corrija, no generes output adicional).
    Genera un mensaje en dos párrafos:
      En el primer párrafo, un mensaje con una breve reflexióin, inspiracional y con predicciones o consejos, 
      divertido y reflexivo como los que se encuentran dentro de las galletas de la fortuna. Este mensaje debe ser directo, 
      sin introducciones ni frases de apertura como "Aquí tienes tu mensaje".

      En el segundo párrafo, escribe un mensaje astrológico relacionado con mi nombre si es posible. 
      Además, utiliza la información del día actual (Hoy es {hoy}) para encontrar aspectos relevantes del día como  
      la posición de los planetas o tránsitos importantes y la fase lunar. Buscando un vínculo simbólico o astrológico que resuene con 
      el nombre o la situación general. Este mensaje también debe ser breve y sin introducciones.
    Asegúrate de que ambos párrafos sean muy creativos, y usa emojis eventualmente!
        
    """
    
    MODEL = modelo
    # Step 1: send the conversation and available functions to the model
    messages=[
        {
            "role": "system",
            "content": "Eres uastrólogo y experto en etimología de nombres."
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        #tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message.content
    
    return response_message


# La función principal, ahora recibe el tópico como parámetro
def get_tip(nombre):
    
    nombre = nombre
    # Recomendaciones
    Reco = generar_recomendacion(nombre)



    # Guardar en el estado de sesión para acceso rápido
    st.session_state['Reco'] = Reco
    st.session_state['comentarios'] = Reco

    return {"recomendacion": Reco} 

# Mostrar resultados en Streamlit
def mostrar_resultados(recomendacion):
    """
    Función para mostrar los resultados de indicadores y recomendaciones en Streamlit.
    
    Args:
        indicadores (dict): Diccionario con los indicadores calculados.
        recomendacion (str): Recomendación generada.
    """
    # Mostrar recomendación
    if recomendacion:
        st.subheader("💬")
        recomendacion_html = recomendacion.replace("\n", "<br>")
        st.markdown(
        f"""
        <div style="background-color: #FCF3EA; padding: 10px; border-radius: 7px; color: #606062;
        font-size: 16px; font-weight: 600; line-height: 1; margin-bottom: 10px !important;">
        <br>{recomendacion_html}<br>
        <br>
        </div>
        <br>
        <hr style="border: 1px solid #606062; margin-top: 10px;">
        """,
        unsafe_allow_html=True
    )
        #st.write(recomendacion)
    else:
        st.warning("No se generó ninguna recomendación.")


############################################################################################################################
######---- Interfaz en Streamlit-----#######################################################################################
############################################################################################################################

# Inicia ngrok con la URL de Streamlit, omitiendo la advertencia del navegador
#public_url = ngrok.connect(8501,  bind_tls=True)

# Mostrar la URL de ngrok generada
#print(f"Streamlit is running on: {public_url}")


# Descargar la imagen desde la URL
response = requests.get(ruta_imagen)

if response.status_code == 200:
    image = Image.open(BytesIO(response.content))

    # Convertir la imagen a base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Mostrar la imagen en Streamlit
    #st.image(image, caption="Imagen cargada desde URL")
else:
    st.error("No se pudo cargar la imagen desde la URL")

# Crear el HTML para una imagen responsiva
st.markdown(
    f"""
    <style>
    .responsive-img {{
        width: 33%;
        max-width: 200px;
        height: auto;
    }}
    </style>
    <img src="data:image/png;base64,{img_str}" class="responsive-img">
    """,
    unsafe_allow_html=True
    )

# Ingreso de Nombre
st.subheader("Ingresá tu Nombre")
nombre_ingresado = st.text_input("tu nombre?:", "")

if nombre_ingresado:  # Verifica que se haya ingresado algo
    # Verificar si se ha ingresado un nuevo Nombre
    if 'nombre' not in st.session_state or st.session_state['nombre'] != nombre_ingresado:
        st.session_state['nombre'] = nombre_ingresado

        # Obtener resultados para el nuevo Nombre
        nuevo_resultado = get_tip(nombre_ingresado)

        # Inicializar el historial si no existe
        if 'historial_resultados' not in st.session_state:
            st.session_state['historial_resultados'] = []

        # Eliminar los resultados previos del historial para este Nombre si ya existían
        st.session_state['historial_resultados'] = [
            entry for entry in st.session_state['historial_resultados'] 
            if entry['nombre'] != nombre_ingresado
        ]

        # Agregar los nuevos resultados al historial
        st.session_state['historial_resultados'].append({
            "nombre": nombre_ingresado,
            "resultados": nuevo_resultado
        })

    # Mostrar historial en orden inverso
    for idx, item in enumerate(reversed(st.session_state['historial_resultados'])):
        try:
            # Verificar que 'resultados' no sea None
            if item.get('resultados') is not None:
                resultados = item['resultados']

                # Verificar que 'indicadores' y 'recomendacion' estén presentes en 'resultados'
                indicadores = resultados.get('indicadores', 'No hay indicadores')
                recomendacion = resultados.get('recomendacion', 'No hay recomendación')

                # Usar st.markdown para mostrar el Nombre y estilo
                nombre = item.get('nombre', 'N/A')
                st.markdown(f"""
                    <div style="background-color: #f9f9f9; color: grey; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 5px;">
                        {len(st.session_state['historial_resultados']) - idx} - {nombre}
                    </div>
                """, unsafe_allow_html=True)

                # Mostrar los detalles de los resultados para este Nombre
                mostrar_resultados(recomendacion)
            else:
                st.warning(f"El item {idx+1} no tiene resultados válidos.")
        
        except KeyError as e:
            st.error(f"Error al acceder a la clave {e} en el item del historial de resultados.")
        except Exception as e:
            st.error(f"Ocurrió un error inesperado: {e}")

else:
    st.write("Luego de ingrear tu NOMBRE presioná Enter.")


# Preguntas sobre los comentarios
if "comentarios" in st.session_state:
    st.subheader("¿Querés hacerme alguna pregunta respecto al mensaje?")
    pregunta = st.text_area(f"""Escribe la pregunta o solicitud y haz click en 'Preguntar' Ej:\n 
                                Explicame la influencia de los planetas """, height=150)
    
    if st.button("Preguntar"):
        resumen = generar_resumen(pregunta, st.session_state.comentarios)
        
        # Almacenar la respuesta en session_state para persistencia
        if 'respuestas' not in st.session_state:
            st.session_state.respuestas = []
        st.session_state.respuestas.append({"pregunta": pregunta, "respuesta": resumen, "nombre": st.session_state['nombre']})


# Mostrar preguntas y respuestas previas
if 'respuestas' in st.session_state:
    st.subheader("Historial de preguntas y respuestas")

    # Iterar en orden inverso para mostrar la última respuesta primero
    for idx, item in enumerate(reversed(st.session_state.respuestas), start=1):
        st.markdown(f"""
        <div style="background-color: #f9f9f9; color: grey; font-weight: bold; font-size: 18px; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            {item['nombre']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="margin-left: 20px; font-size: 16px;">
            <br>        
            <strong>Pregunta {len(st.session_state['respuestas']) - idx + 1}:</strong> {item['pregunta']}<br>
            <br>
        </div>
        """, unsafe_allow_html=True)

        # Manejar los saltos de línea en la respuesta
        respuesta_formateada = item['respuesta'].replace('\n', '<br>')
        st.markdown(f"""
        <div style="margin-left: 20px;">       
            {respuesta_formateada}<br>
            <br> 
        </div>
        """, unsafe_allow_html=True)


#streamlit run Horoscopo.py --server.enableXsrfProtection false         
