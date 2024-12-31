import requests

class APIClient:
    API_BASE_URL = "https://idonosob.pythonanywhere.com" 

    @staticmethod
    def login(email, password):
        url = f'{APIClient.API_BASE_URL}/login'  # Usar la URL base definida en la clase
        try:
            # Hacer la solicitud a la API con POST
            response = requests.post(url, json={'email': email, 'password': password})

            # Comprobar si la respuesta es exitosa
            if response.status_code == 200:
                return response.json()  # Devuelve los datos si la respuesta es exitosa
            else:
                # Si la API responde con un código no 200, devuelve el mensaje de error
                return response.json()  # O si hay un 'msg' en la respuesta, se maneja aquí
        except requests.exceptions.RequestException as e:
            # Si ocurre un error de conexión o algún otro error de la API
            return {"msg": "Error al conectar con el servidor. Intente nuevamente más tarde."}
        
    @staticmethod
    def registro(nombre, email, password):
        url = f'{APIClient.API_BASE_URL}/registro'  # Endpoint de registro
        try:
            # Preparar los datos para el registro
            data = {
                'nombre': nombre,
                'email': email,
                'password': password
            }
            
            # Hacer la solicitud POST al endpoint de registro
            response = requests.post(url, json=data)

            # Comprobar si la respuesta es exitosa
            if response.status_code == 200:
                return response.json()  # Devuelve los datos si la respuesta es exitosa
            else:
                # Si la API responde con un código no 200, devuelve el mensaje de error
                return response.json()
                
        except requests.exceptions.RequestException as e:
            # Manejar errores de conexión o de la API
            return {"msg": "Error al conectar con el servidor. Intente nuevamente más tarde."}
    
    @staticmethod
    def crear_encuesta(headers, data):
        url = f'{APIClient.API_BASE_URL}/crear_encuesta'
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code==200:
                return response.json()
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            return {'msg':'Error al conectar con el servidor'}
        
    @staticmethod
    def obtener_encuestas_disponibles(headers):
        url = f'{APIClient.API_BASE_URL}/encuestas/disponibles'
        try:
            response = requests.get(url, headers=headers)
            print(f"Respuesta de la API: {response.status_code} - {response.text}")  # Agregado para depuración

            if response.status_code == 200:
                return response.json()
            else:
                return {'msg': 'Error en la respuesta de la API', 'status_code': response.status_code}
        except requests.exceptions.RequestException as e:
            return {'msg': 'Error al conectar con el servidor'}
    
    @staticmethod
    def registrar_voto(headers, encuesta_id, opcion_id):
        url = f'{APIClient.API_BASE_URL}/votos'  # Cambia esto al endpoint correcto
        data = {
            'encuesta_id': encuesta_id,
            'opcion_id': opcion_id
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return response.json()  # Devuelve los datos si la respuesta es exitosa
            else:
                return response.json()  # Maneja el error de la API
        except requests.exceptions.RequestException as e:
            return {'msg': 'Error al conectar con el servidor'}
            
    @staticmethod
    def obtener_resultados_encuesta(headers, encuesta_id):
        url = f'{APIClient.API_BASE_URL}/encuestas/{encuesta_id}/resultados'
        try:
            response = requests.get(url, headers=headers)  # Cambiado a GET
            if response.status_code == 200:
                return response.json()
            else:
                return {'msg': 'Error en la respuesta de la API', 'status_code': response.status_code}
        except requests.exceptions.RequestException as e:
            return {'msg': 'Error al conectar con el servidor'}