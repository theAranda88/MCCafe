"""
cafe_app/urls.py
================================================================================
CONFIGURACIÓN DE RUTAS URL PARA EL SISTEMA DE PREDICCIÓN DE CAFÉ
================================================================================

Este archivo configura todas las rutas URL de la aplicación cafe_app.
Mapea las URLs a las vistas correspondientes para crear la API RESTful.

Rutas disponibles:
------------------
1. POST /api/predict/          - Realizar una nueva predicción
2. GET  /api/history/          - Obtener historial de predicciones (paginado)
3. GET  /api/history/<id>/     - Obtener detalle de una predicción específica
4. GET  /api/clusters/         - Obtener información de todos los clusters
5. GET  /api/model-info/       - Obtener información del modelo ML
6. GET  /api/statistics/       - Obtener estadísticas del sistema
7. CRUD /api/profiles/         - CRUD completo para perfiles de café
   - GET    /api/profiles/           - Listar todos los perfiles
   - POST   /api/profiles/           - Crear nuevo perfil
   - GET    /api/profiles/<id>/      - Obtener perfil específico
   - PUT    /api/profiles/<id>/      - Actualizar perfil completo
   - PATCH  /api/profiles/<id>/      - Actualizar perfil parcial
   - DELETE /api/profiles/<id>/      - Eliminar perfil
   - POST   /api/profiles/<id>/predict/ - Predecir usando perfil guardado

Autor: Sistema de Predicción de Café ML
Fecha: 2024
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ============================================================================
# CONFIGURACIÓN DEL ROUTER PARA VIEWSETS
# ============================================================================
# El DefaultRouter genera automáticamente las rutas CRUD para los ViewSets
# Esto incluye: list, create, retrieve, update, partial_update, destroy
# También maneja las acciones personalizadas (como 'predict' en CoffeeProfileViewSet)

router = DefaultRouter()

# Registrar el ViewSet de perfiles de café
# Esto crea automáticamente las siguientes rutas:
# - GET    /profiles/           -> list()
# - POST   /profiles/           -> create()
# - GET    /profiles/<pk>/      -> retrieve()
# - PUT    /profiles/<pk>/      -> update()
# - PATCH  /profiles/<pk>/      -> partial_update()
# - DELETE /profiles/<pk>/      -> destroy()
# - POST   /profiles/<pk>/predict/ -> predict() [acción personalizada]
router.register(r'profiles', views.CoffeeProfileViewSet, basename='coffeeprofile')

# ============================================================================
# CONFIGURACIÓN DE URLS DE LA APP
# ============================================================================
# Prefijo de la app: 'api/'
# Esto se configurará en backend/urls.py como: path('api/', include('cafe_app.urls'))

urlpatterns = [
    # ------------------------------------------------------------------------
    # ENDPOINTS DE PREDICCIÓN
    # ------------------------------------------------------------------------
    
    # Endpoint principal de predicción
    # POST /api/predict/
    # Body: {
    #     "humedad": 0.12,
    #     "altitud": 1500,
    #     "pais": "Colombia",
    #     "region": "Antioquia",
    #     "variedad": "Caturra",
    #     "metodo_procesamiento": "Lavado",
    #     "color": "Verde Azulado"
    # }
    # Response: {
    #     "cluster_id": 0,
    #     "distancia_al_centroide": 0.123,
    #     "confianza_prediccion": 95.5,
    #     "notas_sensoriales": {
    #         "acidez": 8.5,
    #         "aroma": 8.2,
    #         ...
    #     },
    #     "mensaje": "Predicción realizada exitosamente"
    # }
    path('predict/', views.predict_view, name='predict'),
    
    # ------------------------------------------------------------------------
    # ENDPOINTS DE HISTORIAL
    # ------------------------------------------------------------------------
    
    # Listar historial de predicciones con paginación y filtros
    # GET /api/history/
    # Query params opcionales:
    #   - page=1
    #   - cluster_id=0
    #   - pais=Colombia
    #   - metodo_procesamiento=Lavado
    # Response: {
    #     "count": 100,
    #     "next": "http://.../api/history/?page=2",
    #     "previous": null,
    #     "results": [...]
    # }
    path('history/', views.prediction_history_view, name='prediction-history'),
    
    # Obtener detalle de una predicción específica
    # GET /api/history/<id>/
    # Response: {
    #     "id": 1,
    #     "fecha_prediccion": "2024-01-15T10:30:00Z",
    #     "parametros_entrada": {...},
    #     "resultado_prediccion": {...},
    #     ...
    # }
    path('history/<int:pk>/', views.prediction_detail_view, name='prediction-detail'),
    
    # ------------------------------------------------------------------------
    # ENDPOINTS DE INFORMACIÓN DEL MODELO
    # ------------------------------------------------------------------------
    
    # Obtener información de todos los clusters
    # GET /api/clusters/
    # Response: {
    #     "clusters": [
    #         {
    #             "cluster_id": 0,
    #             "num_samples": 250,
    #             "caracteristicas_principales": {...},
    #             "promedios": {...}
    #         },
    #         ...
    #     ],
    #     "total_clusters": 5
    # }
    path('clusters/', views.clusters_info_view, name='clusters-info'),
    
    # Obtener metadata del modelo ML
    # GET /api/model-info/
    # Response: {
    #     "modelo_tipo": "KMeans",
    #     "n_clusters": 5,
    #     "fecha_entrenamiento": "2024-01-01",
    #     "metricas": {...},
    #     "features": [...],
    #     ...
    # }
    path('model-info/', views.model_info_view, name='model-info'),
    
    # ------------------------------------------------------------------------
    # ENDPOINTS DE ESTADÍSTICAS
    # ------------------------------------------------------------------------
    
    # Obtener estadísticas generales del sistema
    # GET /api/statistics/
    # Response: {
    #     "total_predictions": 1000,
    #     "predictions_por_cluster": {...},
    #     "predictions_por_pais": {...},
    #     "predictions_por_metodo": {...},
    #     "promedios_notas": {...},
    #     "total_profiles": 50,
    #     "fecha_primera_prediccion": "2024-01-01T00:00:00Z",
    #     "fecha_ultima_prediccion": "2024-01-15T12:30:00Z"
    # }
    path('statistics/', views.statistics_view, name='statistics'),
    
    # ------------------------------------------------------------------------
    # RUTAS DEL ROUTER (ViewSets)
    # ------------------------------------------------------------------------
    # Incluye todas las rutas generadas automáticamente por el router
    # Esto añade: /api/profiles/ y todas sus subrutas
    path('', include(router.urls)),
]

# ============================================================================
# NOTAS DE IMPLEMENTACIÓN
# ============================================================================
"""
1. PREFIJOS DE URL:
   - Todas estas rutas se sirven bajo el prefijo 'api/' configurado en backend/urls.py
   - Ejemplo: /api/predict/, /api/history/, /api/profiles/

2. VERSIONADO DE API:
   - Actualmente no hay versionado (v1, v2)
   - Si se necesita en el futuro, modificar backend/urls.py:
     path('api/v1/', include('cafe_app.urls'))

3. AUTENTICACIÓN:
   - Las rutas NO tienen autenticación por defecto
   - Para añadir autenticación JWT/OAuth2/Token:
     * Instalar djangorestframework-simplejwt o similar
     * Añadir permission_classes en las vistas
     * Añadir obtain_token endpoint

4. DOCUMENTACIÓN AUTOMÁTICA:
   - Para generar documentación Swagger/ReDoc:
     * Instalar drf-spectacular
     * Añadir rutas de schema y redoc en backend/urls.py
     * Configurar DEFAULT_SCHEMA_CLASS en settings.py

5. RATE LIMITING:
   - No hay límite de tasa implementado
   - Para producción, considerar:
     * django-ratelimit
     * django-throttle
     * Configuración en settings REST_FRAMEWORK

6. CORS (Cross-Origin Resource Sharing):
   - Configurar en settings.py con django-cors-headers
   - Necesario si el frontend está en dominio diferente

7. TESTING:
   - Usar Django TestCase o pytest para testing
   - URLs disponibles para pruebas con APIClient
   - Ejemplo: self.client.post('/api/predict/', data)

8. LOGGING:
   - Las vistas ya tienen logging configurado
   - Los logs se guardan según configuración en settings.py
   - Útil para debugging y monitoreo

9. PAGINACIÓN:
   - Implementada en history_view (20 items por página)
   - Configurable en views.StandardResultsSetPagination
   - También aplica a CoffeeProfileViewSet

10. FILTRADO:
    - history_view acepta filtros por query params
    - Para filtrado avanzado, considerar django-filter
"""
