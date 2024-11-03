from django.core.management.base import BaseCommand, CommandError
from api.models import Complaint
import requests
import json
import os
import base64
from dotenv import load_dotenv

# Función para cargar variables de entorno desde un archivo específico
def load_env_file(file_path):
    load_dotenv(dotenv_path=file_path)

load_env_file(os.path.join(os.path.dirname(__file__), 'captura_data.env'))
CAPTURA_LOGIN = os.getenv("CAPTURA_LOGIN")
CAPTURA_LIST = os.getenv("CAPTURA_LIST")
CAPTURA_IMAGE = os.getenv("CAPTURA_IMAGE")
FORM_ID = os.getenv("FORM_ID")
VERSION = os.getenv("VERSION")
ROW_ID = os.getenv("ROW_ID")
ROWS = os.getenv("ROWS")
CAPTURA_USER = os.getenv("CAPTURA_USER")
CAPTURA_PASSWORD = os.getenv("CAPTURA_PASSWORD")
DESCRIPTION = os.getenv("DESCRIPTION")
TYPE_OF_ROAD = os.getenv("TYPE_OF_ROAD")
LOCATION = os.getenv("LOCATION")
COMPLAINT_TYPE = os.getenv("COMPLAINT_TYPE")
CITY = os.getenv("CITY")
IMAGE = os.getenv("IMAGE")

load_env_file(os.path.join(os.path.dirname(__file__), 'cipe_data.env'))
CIPE_POST = os.getenv("CIPE_POST")
CIPE_TOKEN = os.getenv("CIPE_TOKEN")
CIPE_USER = os.getenv("CIPE_USER")
CIPE_PASSWORD = os.getenv("CIPE_PASSWORD")
CITY_ID = json.loads(os.getenv('CITY_ID'))
ROAD_TYPE_ID = json.loads(os.getenv('ROAD_TYPE_ID'))
COMPLAINT_TYPE_ID = json.loads(os.getenv('COMPLAINT_TYPE_ID'))


            

class Command(BaseCommand):
    """
    Function that tries to log in to Captura and returns its' JSESSIONID cookie value
    for future requests.
    """
    def login_captura(self):
        url = CAPTURA_LOGIN
        credentials = {"user": CAPTURA_USER, "password": CAPTURA_PASSWORD}
        try:
            response = requests.post(url, json=credentials)
            response.raise_for_status()
            success = response.json().get("success")
            if success:
                # Convertir el objeto CookieJar a un diccionario de cookies
                cookie_value = response.cookies.get('JSESSIONID')
                return cookie_value
            else:
                raise CommandError("Authentication error: Could not log in.")
        except requests.exceptions.RequestException as e:
            raise CommandError("Authentication error:", e)


    def get_captura_data(self, cookie_jsession_id):
        url = CAPTURA_LIST
        cookie_str = f"JSESSIONID={cookie_jsession_id};"
        try:
            response = requests.get(
                url, 
                params={"formId": FORM_ID, "version": VERSION, "rowId": ROW_ID, "rows": ROWS}, 
                headers={"Cookie": cookie_str}
            )
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                row_id = item["id"]
                if IMAGE in item["data"] and item["data"][IMAGE] is not None:
                    image_response = requests.get(
                        CAPTURA_IMAGE, 
                        params={"formId": FORM_ID, "version": VERSION, "field": IMAGE, "rowId": row_id},
                        headers={"Cookie": cookie_str}
                    )
                    image_response.raise_for_status()
                    # Convertir el contenido de la imagen a base64
                    image_base64 = base64.b64encode(image_response.content).decode('utf-8')
                    item["data"][IMAGE]["image"] = image_base64

            return json.dumps({"forms": data})
        except requests.exceptions.RequestException as e:
            raise CommandError("Error al obtener los datos de captura:", e)


    def login_cipe(self):
        try:
            response = requests.post(
                CIPE_TOKEN, 
                json={"username": CIPE_USER, "password": CIPE_PASSWORD}
            )
            response.raise_for_status()
            token = response.json().get("token")
            return token
        except requests.exceptions.RequestException as e:
            raise CommandError("Error al obtener el token:", e)


    def parse_captura_data(self, captura_data_str):
        try:
            return json.loads(captura_data_str)

        except json.JSONDecodeError as e:
            raise CommandError("Error al decodificar captura_data:", e)


    def get_processed_ids():
        return Complaint.objects.values_list('captura_id', flat=True)


    def upload_cipe_data(self, captura_data, cipe_token, processed_ids):
        for form in captura_data["forms"]:
            form_id = form["id"]
            if form_id in processed_ids:
                continue

            # Obtener los datos del formulario y mapear a IDs
            complaint_description = form["data"].get(DESCRIPTION)
            if complaint_description is None:
                complaint_description = "Descripcion no disponible"

            complaint_type_road = ROAD_TYPE_ID.get(form["data"][TYPE_OF_ROAD], None)
            complaint_city = CITY_ID.get(form["data"][CITY], None)
            complaint_type = COMPLAINT_TYPE_ID.get(form["data"][COMPLAINT_TYPE], None)
            complaint_image = ""
            if form.get("data") is not None:
                complaint_image_data = form["data"].get(IMAGE)
                if complaint_image_data is not None:
                    complaint_image = complaint_image_data.get("image")

            complaint_altitude = form["data"][LOCATION]["altitude"]
            complaint_latitude = form["data"][LOCATION]["latitude"]
            complaint_accuracy = form["data"][LOCATION]["accuracy"]
            complaint_longitude = form["data"][LOCATION]["longitude"]
            # Realizar la solicitud POST a CIPE
            
            # Construir el cuerpo de la solicitud
            payload = {
                "complaint_type": complaint_type,
                "description": complaint_description,
                "city": complaint_city,
                "latitude": complaint_latitude,
                "altitude": complaint_altitude,
                "accuracy": complaint_accuracy,
                "longitude": complaint_longitude,
                "photo_base64": complaint_image,
                "road_type": complaint_type_road,
                "captura_id": form_id
            }

            # Realizar la solicitud POST a CIPE
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {cipe_token}"
            }

            response = requests.post(CIPE_POST, json=payload, headers=headers)

            # Verificar el estado de la solicitud
            if response.status_code == 201:
                self.stdout.write("Data uploaded to CIPE successfully: %s." % response.text)
            else:
                self.stdout.write("Couldn't upload data to CIPE: %s." % response.text)

    def handle(self, *args, **kwargs):
        cookie_jsession_id = self.login_captura()
        cipe_token = self.login_cipe()
        captura_data_str = self.get_captura_data(cookie_jsession_id)
        captura_data = self.parse_captura_data(captura_data_str)
        processed_ids = self.get_processed_ids()
        self.upload_cipe_data(captura_data, cipe_token, processed_ids)
