import jwt
from django.shortcuts import render, redirect
from django.conf import settings
from services.api.client import APIClient
import requests
from django.http import JsonResponse
from services.api.view_factory import ViewFactory

# Decorador para proteger vistas según rol
from functools import wraps
from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            if user_role not in allowed_roles:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@role_required(['creador'])
def admin_only_view(request):
    return render(request, 'creador_home.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'login.html', {'error': 'Correo electrónico y contraseña son obligatorios'})

        try:
            result = APIClient.login(email, password)

            if result.get("msg"):
                return render(request, 'login.html', {'error': result["msg"]})

            token = result.get('access_token')
            if not token:
                return render(request, 'login.html', {'error': 'No fue posible iniciar sesión. Intente más tarde.'})

            try:
                unverified = jwt.decode(token, options={"verify_signature": False})
                user_data = unverified.get('sub', {})
                if isinstance(user_data, dict):
                    user_role = user_data.get('rol')
                else:
                    user_role = None

                request.session['user_token'] = token
                request.session['user_role'] = user_role

                return ViewFactory.get_renderer(request, user_role)
                
            except Exception as e:
                print(f"Error al iniciar sesión: {str(e)}")
                return render(request, 'login.html', {'error': 'Error procesando el inicio de sesión'})
                
        except requests.exceptions.RequestException as e:
            print(f"Error de request: {str(e)}")
            return render(request, 'login.html', {'error': 'Error al conectar con el servidor'})

    return render(request, 'login.html')


def crear_cuenta_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if not all([nombre, email, password, confirm_password]):
            return render(request, 'crear_cuenta.html', {'error': 'Todos los campos son obligatorios'})

        if password != confirm_password:
            return render(request, 'crear_cuenta.html', {'error': 'Las contraseñas no coinciden'})

        if '@' not in email or '.' not in email:
            return render(request, 'crear_cuenta.html', {'error': 'Por favor ingrese un correo electrónico válido'})

        try:
            result = APIClient.registro(nombre, email, password)

            if result.get("msg"):
                return render(request, 'crear_cuenta.html', {'error': result["msg"]})

            login_result = APIClient.login(email, password)
            token = login_result.get('access_token')

            if not token:
                return render(request, 'login.html', {'error': 'Cuenta creada exitosamente. Por favor inicie sesión.'})

            unverified = jwt.decode(token, options={"verify_signature": False})
            user_data = unverified.get('sub', {})
            if isinstance(user_data, dict):
                user_role = user_data.get('rol')
            else:
                user_role = None

            request.session['user_token'] = token
            request.session['user_role'] = user_role

            return ViewFactory.get_renderer(request, user_role)
            
        except requests.exceptions.RequestException as e:
            print(f"Error de request: {str(e)}")
            return render(request, 'crear_cuenta.html', {'error': 'Error al conectar con el servidor'})

    return render(request, 'crear_cuenta.html')


def logout_view(request):
    request.session.pop('user_token', None)
    request.session.pop('user_role', None)
    request.session.flush()  # Limpia toda la sesión
    return redirect('login')


@role_required(['creador'])
def crear_encuesta(request):
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        opciones = request.POST.getlist('opciones')

        if not all([titulo, descripcion, fecha_inicio, fecha_fin, opciones]):
            return render(request, 'crear_encuesta.html', {'error': 'Todos los campos son obligatorios para crear una encuesta'})

        if len(opciones) < 2:
            return render(request, 'crear_encuesta.html', {'error': 'Debe haber al menos dos opciones para la encuesta'})

        try:
            token = request.session.get('user_token')
            if not token:
                return render(request, 'login.html', {'error': 'Debe iniciar sesión para crear la encuesta'})

            headers = {'Authorization': f'Bearer {token}'}
            result = APIClient.crear_encuesta(headers=headers, data={
                'titulo': titulo,
                'descripcion': descripcion,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'opciones': opciones
            })
            return render(request, 'crear_encuesta.html', {'success': 'Encuesta creada exitosamente.'})
        
        except Exception as e:
            return render(request, 'crear_encuesta.html', {'error': 'Ocurrió un error al intentar crear la encuesta. Inténtelo de nuevo.'})

    # Si la solicitud es GET, mostrar el formulario
    return render(request, 'crear_encuesta.html')

def ver_encuestas(request):
    if request.method == 'GET':
        token = request.session.get('user_token')
        if not token:
            return render(request, 'login.html', {'error': 'Debe iniciar sesión para ver las encuestas'})

        try:
            headers = {'Authorization': f'Bearer {token}'}
            result = APIClient.obtener_encuestas_disponibles(headers)

            print(f"Resultado de la API: {result}")  # Depuracion

            if result.get('msg'):
                return render(request, 'ver_encuestas.html', {'error': result['msg']})

            
            encuestas = result.get('encuestas', [])
            return render(request, 'ver_encuestas.html', {'encuestas': encuestas})

        except Exception as e:
            print(e)
            return render(request, 'ver_encuestas.html', {'error': 'Ocurrió un error al ver las encuestas'})

    return render(request, 'ver_encuestas.html', {'error': 'Método no permitido.'})


def votos(request):
    if request.method == 'POST':
        token = request.session.get('user_token')
        if not token:
            return redirect('login')  # Redirigir al login si no hay token

        # Obtener el ID de la encuesta y la opción seleccionada del formulario
        encuesta_id = request.POST.get('encuesta_id')
        opcion_id = request.POST.get('opcion_id')

        if not encuesta_id or not opcion_id:
            return render(request, 'votos.html', {'error': 'Por favor selecciona una opción.'})

        try:
            headers = {'Authorization': f'Bearer {token}'}
            # Aquí llamas a la API para registrar el voto
            result = APIClient.registrar_voto(headers=headers, encuesta_id=encuesta_id, opcion_id=opcion_id)

            print(f"Resultado de la API: {result}")  # Para depuración

            if result.get('msg'):
                return render(request, 'votos.html', {'error': result['msg'], 'encuesta_id': encuesta_id, 'opciones': []})

            # Si el voto se registró correctamente, redirigir a los resultados o a una página de éxito
            return redirect('resultado_encuesta', encuesta_id=encuesta_id)

        except Exception as e:
            print(f"Error al registrar voto: {str(e)}")  # Para depuración
            return render(request, 'votos.html', {'error': 'Ocurrió un error al registrar tu voto.', 'encuesta_id': encuesta_id, 'opciones': []})

    return render(request, 'ver_encuestas.html', {'error': 'Método no permitido.'})



def ver_resultados_encuesta(request):
    """
    Vista para obtener y mostrar los resultados de las encuestas según el rol del usuario autenticado.

    Parámetros:
    - request: Objeto HttpRequest que contiene los datos de la solicitud.

    Funcionalidad:
    1. Inicializa el contexto con 'resultados' y 'error' como None.
    2. Intenta obtener el token de usuario de la sesión.
       - Si no hay token, establece un mensaje de error en el contexto y renderiza la plantilla 'ver_resultados_encuesta.html'.
    3. Configura los encabezados de autorización con el token JWT.
    4. Obtiene el rol del usuario de la sesión.
    5. Llama al método APIClient.obtener_resultados_encuestas(headers) para obtener los resultados de las encuestas.
       - Si la respuesta contiene un mensaje de error ('msg'), lo establece en el contexto.
       - Si la respuesta es exitosa, establece la lista de encuestas en el contexto.
    6. Maneja posibles excepciones:
       - ValueError: Establece un mensaje de error indicando que el ID de la encuesta debe ser un número válido.
       - Exception: Establece un mensaje de error genérico indicando que ocurrió un error al obtener los resultados.
    7. Renderiza la plantilla 'ver_resultados_encuesta.html' con el contexto.

    Retorna:
    - HttpResponse: Renderiza la plantilla 'ver_resultados_encuesta.html' con el contexto actualizado.
    """
    context = {'resultados': None, 'error': None}
    try:
        token = request.session.get('user_token')
        if not token:
            context['error'] = 'Debe iniciar sesión para ver los resultados.'
            return render(request, 'ver_resultados_encuesta.html', context)

        headers = {'Authorization': f'Bearer {token}'}
        user_role = request.session.get('user_role')

        encuestas_resultados = APIClient.obtener_resultados_encuestas(headers)
        if 'msg' in encuestas_resultados:
            context['error'] = encuestas_resultados['msg']
        else:
            context['encuestas'] = encuestas_resultados.get('encuestas', [])

    except ValueError:
        context['error'] = 'El ID de la encuesta debe ser un número válido.'
    except Exception as e:
        context['error'] = 'Ocurrió un error al obtener los resultados. Inténtelo nuevamente.'

    return render(request, 'ver_resultados_encuesta.html', context)


def health(request):
    if request.method == 'GET':
        return JsonResponse({'status': 'OK'})
