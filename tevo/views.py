# views.py
import jwt
from django.shortcuts import render, redirect
from django.conf import settings
from services.api.client import APIClient
import requests
from services.api.view_factory import ViewFactory

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'login.html', 
                        {'error': 'Correo electrónico y contraseña son obligatorios'})

        try:
            result = APIClient.login(email, password)

            if result.get("msg"):
                return render(request, 'login.html', {'error': result["msg"]})

            token = result.get('access_token')
            if not token:
                return render(request, 'login.html', {'error': 'No fue posible iniciar sesión. Intente más tarde.'})

            try:
                unverified = jwt.decode(token, options={"verify_signature": False})
                
                # Obtener el rol desde la estructura correcta del token
                user_data = unverified.get('sub', {})
                if isinstance(user_data, dict):
                    user_role = user_data.get('rol')
                else:
                    user_role = None

                # Guardar en sesión
                request.session['user_token'] = token
                request.session['user_role'] = user_role
                
                # Usar la fabrica simplificada

                return ViewFactory.get_renderer(request, user_role)
                
            except Exception as e:
                print(f"Error al iniciar sesión: {str(e)}")
                return render(request, 'login.html', 
                            {'error': 'Error procesando el inicio de sesión'})
                
        except requests.exceptions.RequestException as e:
            print(f"Error de request: {str(e)}")
            return render(request, 'login.html', 
                        {'error': 'Error al conectar con el servidor'})

    return render(request, 'login.html')


def crear_cuenta_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        # Validaciones básicas
        if not all([nombre, email, password, confirm_password]):
            return render(request, 'crear_cuenta.html', 
                        {'error': 'Todos los campos son obligatorios'})

        if password != confirm_password:
            return render(request, 'crear_cuenta.html', 
                        {'error': 'Las contraseñas no coinciden'})

        # Validación básica de formato de email
        if '@' not in email or '.' not in email:
            return render(request, 'crear_cuenta.html', 
                        {'error': 'Por favor ingrese un correo electrónico válido'})

        try:
            # Asumiendo que APIClient tiene un método register similar al login
            print(nombre, email, password)
            result = APIClient.registro(nombre, email, password)

            if result.get("msg"):
                return render(request, 'crear_cuenta.html', {'error': result["msg"]})

            # Si el registro fue exitoso, iniciar sesión automáticamente
            try:
                login_result = APIClient.login(email, password)
                token = login_result.get('access_token')

                if not token:
                    return render(request, 'login.html', 
                                {'error': 'Cuenta creada exitosamente. Por favor inicie sesión.'})

                # Decodificar el token para obtener información del usuario
                unverified = jwt.decode(token, options={"verify_signature": False})
                
                # Obtener el rol desde la estructura del token
                user_data = unverified.get('sub', {})
                if isinstance(user_data, dict):
                    user_role = user_data.get('rol')
                else:
                    user_role = None

                # Guardar en sesión
                request.session['user_token'] = token
                request.session['user_role'] = user_role
                
                # Redirigir según el rol
                return ViewFactory.get_renderer(request, user_role)
            
            except Exception as e:
                print(f"Error al iniciar sesión después del registro: {str(e)}")
                return render(request, 'login.html', 
                            {'error': 'Cuenta creada exitosamente. Por favor inicie sesión.'})

        except requests.exceptions.RequestException as e:
            print(f"Error de request: {str(e)}")
            return render(request, 'crear_cuenta.html', 
                        {'error': 'Error al conectar con el servidor'})

    return render(request, 'crear_cuenta.html')

def logout_view(request):
    # Limpiar las variables de sesión
    request.session.pop('user_token', None)
    request.session.pop('user_role', None)
    request.session.flush()  # Limpia toda la sesión
    
    # Redirigir al login
    return redirect('login')

@role_required(['creador'])
def crear_encuesta(requests):
    if requests.method =="POST":
        titulo =requests.POST.get('titulo')
        descripcion = requests.POST.get('descripcion')
        fecha_inicio = requests.POST.get('fecha_inicio')
        fecha_fin = requests.POST.get('fecha_fin')
        opciones = requests.POST.getlist('opciones')

        if not all([titulo,descripcion,fecha_inicio,fecha_fin,opciones]):
            return render(request,'crear_encuesta.html',{'error':'Todos los campos son obligatorios para crear una encuesta'})
        if len(opciones)<2:
            return render(request,'crear_encuesta.html',{'error':'Debe haber al menos dos opciones para la encuesta'})
    
    try:
        token = request.session.get('user_token')
        if not token:
            return render(request, 'login.html',{'error':'Debe iniciar sesion para crear la encuesta'})
        headers = {'Authorization': f'Bearer {token}'}
        result = APIClient.crear_encuesta(headers=headers,data={
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'opciones': opciones
                })
        return render(request, 'crear_encuesta.html', {'success': 'Encuesta creada exitosamente.'})
    
    except Exception as e:
        return render(request, 'crear_encuesta.html', {'error': 'Ocurrió un error al intentar crear la encuesta. Inténtelo de nuevo.'})
    
    
    
def ver_encuestas(request):
    if request.method == 'GET':
        token = request.session.get('user_token')
        if not token:
            return render(request, 'login.html',{'error','Debe haber iniciado sesion para ver la encuesta'})
    return render(request,'ver_encuestas.html')





# Opcional: Decorator para proteger vistas según rol
from functools import wraps
from django.http import HttpResponseForbidden

# Ítalo: esta función la podemos utilizar para cuando queremos proteger una vista en base al rol.
# ver el ejemplo de la función de más abajo 'role_required'
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

# Ejemplo de uso del decorator
@role_required(['creador'])
def admin_only_view(request):
    return render(request, 'creador_home.html')