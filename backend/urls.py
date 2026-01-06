"""
backend/urls.py
================================================================================
CONFIGURACIÓN PRINCIPAL DE URLS DEL PROYECTO
================================================================================

Este archivo configura las rutas URL principales del proyecto Django.
Incluye el panel de administración y las rutas de la API de café.

Estructura de URLs:
-------------------
/admin/              - Panel de administración de Django
/api/                - API RESTful del sistema de predicción de café
  ├── /api/predict/         - Realizar predicciones
  ├── /api/history/         - Historial de predicciones
  ├── /api/clusters/        - Información de clusters
  ├── /api/model-info/      - Metadata del modelo ML
  ├── /api/profiles/        - CRUD de perfiles de café
  └── /api/statistics/      - Estadísticas del sistema

Autor: Sistema de Predicción de Café ML
Fecha: 2024
"""

from django.contrib import admin
from django.urls import path, include

# ============================================================================
# CONFIGURACIÓN DE RUTAS PRINCIPALES
# ============================================================================

urlpatterns = [
    # ------------------------------------------------------------------------
    # PANEL DE ADMINISTRACIÓN DE DJANGO
    # ------------------------------------------------------------------------
    # Acceso: http://localhost:8000/admin/
    # Permite gestionar modelos, usuarios, y datos desde interfaz web
    # Usuario admin debe crearse con: python manage.py createsuperuser
    path("admin/", admin.site.urls),
    
    # ------------------------------------------------------------------------
    # API RESTFUL DEL SISTEMA DE CAFÉ
    # ------------------------------------------------------------------------
    # Acceso: http://localhost:8000/api/
    # Incluye todas las rutas definidas en cafe_app/urls.py
    # Endpoints disponibles:
    #   - POST   /api/predict/              - Nueva predicción
    #   - GET    /api/history/              - Historial paginado
    #   - GET    /api/history/<id>/         - Detalle predicción
    #   - GET    /api/clusters/             - Info de clusters
    #   - GET    /api/model-info/           - Metadata del modelo
    #   - GET    /api/statistics/           - Estadísticas
    #   - GET    /api/profiles/             - Listar perfiles
    #   - POST   /api/profiles/             - Crear perfil
    #   - GET    /api/profiles/<id>/        - Ver perfil
    #   - PUT    /api/profiles/<id>/        - Actualizar perfil
    #   - PATCH  /api/profiles/<id>/        - Actualizar parcial
    #   - DELETE /api/profiles/<id>/        - Eliminar perfil
    #   - POST   /api/profiles/<id>/predict/ - Predecir con perfil
    path("api/", include("cafe_app.urls")),
]

# ============================================================================
# NOTAS DE CONFIGURACIÓN
# ============================================================================
"""
1. DESARROLLO vs PRODUCCIÓN:
   - En desarrollo: DEBUG=True en settings.py
   - En producción: 
     * DEBUG=False
     * Configurar ALLOWED_HOSTS correctamente
     * Usar servidor web (Gunicorn, uWSGI)
     * Proxy reverso (Nginx, Apache)

2. ARCHIVOS ESTÁTICOS Y MEDIA:
   - Si usas archivos estáticos en producción, añadir:
     from django.conf import settings
     from django.conf.urls.static import static
     
     if settings.DEBUG:
         urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
         urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

3. DOCUMENTACIÓN DE API:
   - Para añadir Swagger/ReDoc, instalar drf-spectacular:
     pip install drf-spectacular
   
   - Añadir rutas:
     from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
     
     urlpatterns += [
         path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
         path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
     ]

4. AUTENTICACIÓN:
   - Para JWT, instalar djangorestframework-simplejwt:
     pip install djangorestframework-simplejwt
   
   - Añadir rutas:
     from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
     
     urlpatterns += [
         path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
         path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     ]

5. CORS (Cross-Origin Resource Sharing):
   - Instalar: pip install django-cors-headers
   - Configurar en settings.py:
     INSTALLED_APPS += ['corsheaders']
     MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', ...] + MIDDLEWARE
     CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']

6. SALUD DEL SISTEMA:
   - Añadir endpoint de health check para monitoreo:
     from django.http import JsonResponse
     
     def health_check(request):
         return JsonResponse({"status": "healthy", "service": "coffee-prediction-api"})
     
     urlpatterns += [path('health/', health_check, name='health-check')]

7. VERSIONADO DE API:
   - Para versión múltiple, cambiar:
     path("api/v1/", include("cafe_app.urls")),
     path("api/v2/", include("cafe_app.urls_v2")),

8. TESTING:
   - Las URLs son testeables con Django TestCase:
     from django.test import TestCase, Client
     
     class URLTests(TestCase):
         def test_predict_endpoint(self):
             response = self.client.post('/api/predict/', data={...})
             self.assertEqual(response.status_code, 200)

9. SEGURIDAD:
   - Configurar CSRF_TRUSTED_ORIGINS en settings.py
   - Usar HTTPS en producción (Let's Encrypt)
   - Implementar rate limiting con django-ratelimit

10. MONITOREO:
    - Integrar con Sentry para error tracking
    - Usar Django Debug Toolbar en desarrollo
    - Configurar logging adecuado en settings.py
"""
