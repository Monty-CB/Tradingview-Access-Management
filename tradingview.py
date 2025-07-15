import os
import requests
import psycopg2  # Asegúrate de que esta librería esté instalada para conectar con PostgreSQL
import config
import platform
from urllib3 import encode_multipart_formdata
from datetime import datetime, timezone
import helper
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)

class tradingview:
    def __init__(self):
        # Recuperar sessionid desde PostgreSQL
        self.sessionid = self.get_sessionid()
        if not self.sessionid:
            logging.warning("Session ID not found in database, attempting to login.")

            # Si no hay sessionid, realiza el login
            username = os.environ['tvusername']
            password = os.environ['tvpassword']

            payload = {'username': username, 'password': password, 'remember': 'on'}
            body, contentType = encode_multipart_formdata(payload)
            userAgent = 'TWAPI/3.0 (' + platform.system() + '; ' + platform.version() + '; ' + platform.release() + ')'
            logging.info(f"User agent: {userAgent}")
            login_headers = {
                'origin': 'https://www.tradingview.com',
                'User-Agent': userAgent,
                'Content-Type': contentType,
                'referer': 'https://www.tradingview.com'
            }
            login = requests.post(config.urls["signin"], data=body, headers=login_headers)
            cookies = login.cookies.get_dict()
            self.sessionid = cookies.get("sessionid")
            if self.sessionid:
                self.store_sessionid(self.sessionid)
            else:
                logging.error("Failed to retrieve sessionid after login attempt.")
                raise Exception("Unable to login and retrieve session ID.")

        # Verificar la validez del sessionid con una petición a tvcoins
        headers = {'cookie': 'sessionid=' + self.sessionid}
        test = requests.request("GET", config.urls["tvcoins"], headers=headers)
        if test.status_code != 200:
            logging.error(f"Invalid session ID: {self.sessionid}")
            raise Exception("Session ID is invalid.")
        logging.info("Session ID is valid.")

    def get_sessionid(self):
        # Conectar a PostgreSQL para obtener el sessionid
        try:
            connection = psycopg2.connect(
                dbname="hotmart_db",
                user="hotmart_db_user",
                password="Xg0bQfYlSi9VH7ywz90PkP6zgK5nQsbM",
                host="dpg-d1po8bk9c44c738r1e4g-a.frankfurt-postgres.render.com"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT sessionid FROM sessions WHERE id = 1")  # Ajusta la consulta según tu esquema
            sessionid = cursor.fetchone()
            connection.close()
            return sessionid[0] if sessionid else None
        except Exception as e:
            logging.error(f"Error retrieving sessionid from database: {e}")
            return None

    def store_sessionid(self, sessionid):
        # Guardar sessionid en PostgreSQL
        try:
            connection = psycopg2.connect(
                dbname="hotmart_db",
                user="hotmart_db_user",
                password="Xg0bQfYlSi9VH7ywz90PkP6zgK5nQsbM",
                host="dpg-d1po8bk9c44c738r1e4g-a.frankfurt-postgres.render.com"
            )
            cursor = connection.cursor()
            cursor.execute("INSERT INTO sessions (sessionid) VALUES (%s)", (sessionid,))
            connection.commit()
            connection.close()
            logging.info(f"Session ID stored successfully: {sessionid}")
        except Exception as e:
            logging.error(f"Error storing sessionid in database: {e}")

    def validate_username(self, username):
        try:
            users = requests.get(config.urls["username_hint"] + "?s=" + username)
            usersList = users.json()
            validUser = False
            verifiedUserName = ''
            for user in usersList:
                if user['username'].lower() == username.lower():
                    validUser = True
                    verifiedUserName = user['username']
            return {"validuser": validUser, "verifiedUserName": verifiedUserName}
        except Exception as e:
            logging.error(f"Error validating username: {e}")
            return {"validuser": False, "verifiedUserName": ""}

    def get_access_details(self, username, pine_id):
        try:
            user_payload = {'pine_id': pine_id, 'username': username}
            user_headers = {
                'origin': 'https://www.tradingview.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'sessionid=' + self.sessionid
            }
            usersResponse = requests.post(config.urls['list_users'] + '?limit=10&order_by=-created',
                                          headers=user_headers, data=user_payload)
            userResponseJson = usersResponse.json()
            users = userResponseJson['results']

            access_details = user_payload
            hasAccess = False
            noExpiration = False
            expiration = str(datetime.now(timezone.utc))
            for user in users:
                if user['username'].lower() == username.lower():
                    hasAccess = True
                    strExpiration = user.get("expiration")
                    if strExpiration is not None:
                        expiration = user['expiration']
                    else:
                        noExpiration = True

            access_details['hasAccess'] = hasAccess
            access_details['noExpiration'] = noExpiration
            access_details['currentExpiration'] = expiration
            return access_details
        except Exception as e:
            logging.error(f"Error retrieving access details: {e}")
            return {"error": "Error retrieving access details"}

    def add_access(self, access_details, extension_type, extension_length):
        try:
            noExpiration = access_details['noExpiration']
            access_details['expiration'] = access_details['currentExpiration']
            access_details['status'] = 'Not Applied'
            if not noExpiration:
                payload = {'pine_id': access_details['pine_id'], 'username_recip': access_details['username']}
                if extension_type != 'L':
                    expiration = helper.get_access_extension(
                        access_details['currentExpiration'], extension_type, extension_length)
                    payload['expiration'] = expiration
                    access_details['expiration'] = expiration
                else:
                    access_details['noExpiration'] = True
                enpoint_type = 'modify_access' if access_details['hasAccess'] else 'add_access'

                body, contentType = encode_multipart_formdata(payload)
                headers = {
                    'origin': 'https://www.tradingview.com',
                    'Content-Type': contentType,
                    'cookie': 'sessionid=' + self.sessionid
                }
                add_access_response = requests.post(config.urls[enpoint_type], data=body, headers=headers)
                access_details['status'] = 'Success' if (
                    add_access_response.status_code == 200 or add_access_response.status_code == 201) else 'Failure'
            return access_details
        except Exception as e:
            logging.error(f"Error adding access: {e}")
            return {"error": "Error adding access"}

    def remove_access(self, access_details):
        try:
            payload = {'pine_id': access_details['pine_id'], 'username_recip': access_details['username']}
            body, contentType = encode_multipart_formdata(payload)
            headers = {
                'origin': 'https://www.tradingview.com',
                'Content-Type': contentType,
                'cookie': 'sessionid=' + self.sessionid
            }
            remove_access_response = requests.post(config.urls['remove_access'], data=body, headers=headers)
            access_details['status'] = 'Success' if remove_access_response.status_code == 200 else 'Failure'
            return access_details
        except Exception as e:
            logging.error(f"Error removing access: {e}")
            return {"error": "Error removing access"}
