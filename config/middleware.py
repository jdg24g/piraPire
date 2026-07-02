import re
import os
from django.http import HttpResponse


class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Cargar orígenes permitidos desde variables de entorno
        origins_str = os.environ.get('PIRAPIRE_CORS_ALLOWED_ORIGINS', '')
        self.allowed_origins = [origin.strip() for origin in origins_str.split(',') if origin.strip()]
        
        # Cargar regex permitidos
        regex_str = os.environ.get('PIRAPIRE_CORS_ALLOWED_ORIGIN_REGEXES', '')
        self.allowed_regexes = [re.compile(regex.strip()) for regex in regex_str.split(',') if regex.strip()]

    def __call__(self, request):
        # ponytail: middleware de CORS nativo y simple para evitar dependencias externas extras
        if request.method == 'OPTIONS':
            response = HttpResponse()
        else:
            response = self.get_response(request)

        origin = request.headers.get('Origin')
        if origin:
            is_allowed = False
            
            # Validar por coincidencia exacta
            if origin in self.allowed_origins or '*' in self.allowed_origins:
                is_allowed = True
            else:
                # Validar por regex
                for regex in self.allowed_regexes:
                    if regex.match(origin):
                        is_allowed = True
                        break
            
            if is_allowed:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
                
                # Para solicitudes OPTIONS previas, responder exitosamente
                if request.method == 'OPTIONS':
                    response.status_code = 200

        return response
