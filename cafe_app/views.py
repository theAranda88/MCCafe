"""
VISTAS API - ENDPOINTS REST PARA PREDICCIÓN DE CAFÉ
====================================================

Este módulo implementa los endpoints de la API REST usando Django REST Framework.

ENDPOINTS DISPONIBLES:
1. POST /api/predict/           - Realizar predicción de notas sensoriales
2. GET  /api/history/           - Listar historial de predicciones
3. GET  /api/history/<id>/      - Detalle de una predicción
4. GET  /api/clusters/          - Información de todos los clusters
5. GET  /api/model-info/        - Metadata del modelo ML
6. GET  /api/profiles/          - Listar perfiles de café guardados
7. POST /api/profiles/          - Crear nuevo perfil
8. GET  /api/profiles/<id>/     - Detalle de un perfil
9. PUT  /api/profiles/<id>/     - Actualizar perfil
10. DELETE /api/profiles/<id>/  - Eliminar perfil

Autor: Proyecto Café ML
Fecha: 2026-01-05
"""

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg
import logging

from .models import Prediction, CoffeeProfile, ClusterInfo
from .serializers import (
    PredictionInputSerializer,
    PredictionOutputSerializer,
    PredictionHistorySerializer,
    CoffeeProfileSerializer,
    ClusterStatsSerializer,
    ModelInfoSerializer
)
from .ml_service import (
    predict_coffee_notes,
    get_all_clusters_info,
    get_model_metadata,
    MLModelNotLoadedError
)

# Configurar logging
logger = logging.getLogger(__name__)


# ============================================================================
# PAGINACIÓN PERSONALIZADA
# ============================================================================

class StandardResultsSetPagination(PageNumberPagination):
    """
    Configuración de paginación estándar para las listas.
    
    Configuración:
    - page_size: 20 items por página (default)
    - page_size_query_param: Permite al cliente especificar tamaño
    - max_page_size: Máximo 100 items por página
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================================
# ENDPOINT: PREDICCIÓN DE NOTAS SENSORIALES
# ============================================================================

@api_view(['POST'])
def predict_view(request):
    """
    POST /api/predict/
    
    Realiza una predicción de notas sensoriales basándose en los parámetros
    del café proporcionados.
    
    FLUJO:
    1. Validar datos de entrada con PredictionInputSerializer
    2. Llamar a ml_service.predict() para obtener predicción
    3. Guardar resultado en BD (modelo Prediction)
    4. Retornar respuesta formateada con PredictionOutputSerializer
    
    Request Body (JSON):
    {
        "country_of_origin": "Ethiopia",
        "processing_method": "Washed / Wet",
        "variety": "Bourbon",
        "altitude_mean": 2000.0,
        "moisture": 0.12,
        "category_one_defects": 0,
        "category_two_defects": 0
    }
    
    Response (201 Created):
    {
        "success": true,
        "prediction_id": 123,
        "cluster_asignado": 0,
        "confianza": 92.5,
        "notas_predichas": {
            "Aroma": 7.85,
            "Flavor": 7.92,
            ...
        },
        "cluster_info": {...},
        ...
    }
    
    Errores:
    - 400 Bad Request: Datos de entrada inválidos
    - 500 Internal Server Error: Error en el modelo ML
    """
    try:
        # 1. VALIDAR DATOS DE ENTRADA
        input_serializer = PredictionInputSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            logger.warning(f"Datos de entrada inválidos: {input_serializer.errors}")
            return Response({
                'success': False,
                'error': 'Datos de entrada inválidos',
                'details': input_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = input_serializer.validated_data
        logger.info(f"📥 Solicitud de predicción recibida: {validated_data}")
        
        # 2. REALIZAR PREDICCIÓN USANDO ML SERVICE
        try:
            prediction_result = predict_coffee_notes(**validated_data)
            logger.info(f"✅ Predicción exitosa: Cluster {prediction_result['cluster_asignado']}")
        
        except MLModelNotLoadedError as e:
            logger.error(f"❌ Modelo ML no cargado: {e}")
            return Response({
                'success': False,
                'error': 'El modelo ML no está disponible. Contacte al administrador.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"❌ Error durante predicción: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error al realizar predicción: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 3. GUARDAR EN BASE DE DATOS
        try:
            # Extraer notas predichas
            notas = prediction_result['notas_predichas']
            
            # Crear registro en BD
            prediction_record = Prediction.objects.create(
                # Parámetros de entrada
                country_of_origin=validated_data['country_of_origin'],
                processing_method=validated_data['processing_method'],
                variety=validated_data['variety'],
                altitude_mean=validated_data['altitude_mean'],
                moisture=validated_data['moisture'],
                category_one_defects=validated_data.get('category_one_defects', 0),
                category_two_defects=validated_data.get('category_two_defects', 0),
                
                # Resultado de la predicción
                cluster_asignado=prediction_result['cluster_asignado'],
                confianza=prediction_result['confianza'],
                distancia_centroide=prediction_result['distancia_centroide'],
                
                # Notas sensoriales
                aroma=notas.get('Aroma', 0),
                flavor=notas.get('Flavor', 0),
                aftertaste=notas.get('Aftertaste', 0),
                acidity=notas.get('Acidity', 0),
                body=notas.get('Body', 0),
                balance=notas.get('Balance', 0),
                total_cup_points=notas.get('Total.Cup.Points', 0)
            )
            
            logger.info(f"💾 Predicción guardada en BD: ID={prediction_record.id}")
        
        except Exception as e:
            logger.error(f"⚠️  Error al guardar en BD: {e}", exc_info=True)
            # No retornar error - la predicción se realizó correctamente
        
        # 4. FORMATEAR RESPUESTA
        output_serializer = PredictionOutputSerializer(data=prediction_result)
        output_serializer.is_valid()  # Siempre será válido
        
        # 5. RETORNAR RESPUESTA
        response_data = {
            'success': True,
            'prediction_id': prediction_record.id if 'prediction_record' in locals() else None,
            **output_serializer.validated_data
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"❌ Error inesperado en predict_view: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINT: HISTORIAL DE PREDICCIONES
# ============================================================================

@api_view(['GET'])
def prediction_history_view(request):
    """
    GET /api/history/
    
    Retorna el historial de predicciones realizadas.
    
    Query Parameters:
    - page: Número de página (default: 1)
    - page_size: Items por página (default: 20, max: 100)
    - cluster: Filtrar por cluster (opcional)
    - country: Filtrar por país (opcional)
    
    Response (200 OK):
    {
        "count": 150,
        "next": "http://...?page=2",
        "previous": null,
        "results": [
            {
                "id": 123,
                "fecha": "2026-01-05T10:30:00Z",
                "parametros_entrada": {...},
                "resultado": {...},
                "notas_sensoriales": {...}
            },
            ...
        ]
    }
    """
    try:
        # Obtener queryset base
        queryset = Prediction.objects.all()
        
        # FILTROS OPCIONALES
        
        # Filtrar por cluster
        cluster_id = request.query_params.get('cluster', None)
        if cluster_id is not None:
            try:
                queryset = queryset.filter(cluster_asignado=int(cluster_id))
            except ValueError:
                pass
        
        # Filtrar por país
        country = request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country_of_origin__icontains=country)
        
        # Filtrar por método de procesamiento
        processing = request.query_params.get('processing', None)
        if processing:
            queryset = queryset.filter(processing_method__icontains=processing)
        
        # PAGINACIÓN
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = PredictionHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Sin paginación (fallback)
        serializer = PredictionHistorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    except Exception as e:
        logger.error(f"❌ Error en prediction_history_view: {e}", exc_info=True)
        return Response({
            'error': 'Error al obtener historial'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def prediction_detail_view(request, pk):
    """
    GET /api/history/<id>/
    
    Retorna el detalle de una predicción específica.
    
    Path Parameters:
    - pk: ID de la predicción
    
    Response (200 OK):
    {
        "id": 123,
        "fecha": "2026-01-05T10:30:00Z",
        "parametros_entrada": {...},
        "resultado": {...},
        "notas_sensoriales": {...}
    }
    
    Errores:
    - 404 Not Found: Predicción no existe
    """
    try:
        prediction = Prediction.objects.get(pk=pk)
        serializer = PredictionHistorySerializer(prediction)
        return Response(serializer.data)
    
    except Prediction.DoesNotExist:
        return Response({
            'error': f'Predicción con ID {pk} no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"❌ Error en prediction_detail_view: {e}", exc_info=True)
        return Response({
            'error': 'Error al obtener detalle'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINT: INFORMACIÓN DE CLUSTERS
# ============================================================================

@api_view(['GET'])
def clusters_info_view(request):
    """
    GET /api/clusters/
    
    Retorna información detallada de todos los clusters del modelo.
    
    Response (200 OK):
    [
        {
            "cluster_id": 0,
            "n_samples": 450,
            "categorical_modes": {
                "Country.of.Origin": "Ethiopia",
                "Processing.Method": "Washed / Wet",
                ...
            },
            "numeric_means": {
                "altitude_mean_meters": 1850.5,
                "Moisture": 0.11,
                ...
            },
            "output_means": {
                "Aroma": 7.85,
                "Flavor": 7.92,
                ...
            }
        },
        ...
    ]
    """
    try:
        # Obtener info de clusters desde ML service
        clusters_data = get_all_clusters_info()
        
        # Serializar
        serializer = ClusterStatsSerializer(clusters_data, many=True)
        
        return Response(serializer.data)
    
    except MLModelNotLoadedError as e:
        logger.error(f"❌ Modelo no cargado: {e}")
        return Response({
            'error': 'El modelo ML no está disponible'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"❌ Error en clusters_info_view: {e}", exc_info=True)
        return Response({
            'error': 'Error al obtener información de clusters'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINT: INFORMACIÓN DEL MODELO
# ============================================================================

@api_view(['GET'])
def model_info_view(request):
    """
    GET /api/model-info/
    
    Retorna metadata del modelo de machine learning.
    
    Response (200 OK):
    {
        "model_type": "kmeans",
        "n_clusters": 4,
        "silhouette_score": 0.42,
        "inertia": 12345.67,
        "training_samples": 2682,
        "input_features": {...},
        "output_features": [...],
        "version": "1.0",
        "created_at": "2026-01-05T00:00:00"
    }
    """
    try:
        # Obtener metadata desde ML service
        model_data = get_model_metadata()
        
        # Serializar
        serializer = ModelInfoSerializer(data=model_data)
        serializer.is_valid()
        
        return Response(serializer.validated_data)
    
    except MLModelNotLoadedError as e:
        logger.error(f"❌ Modelo no cargado: {e}")
        return Response({
            'error': 'El modelo ML no está disponible'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"❌ Error en model_info_view: {e}", exc_info=True)
        return Response({
            'error': 'Error al obtener información del modelo'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# VIEWSET: PERFILES DE CAFÉ (CRUD COMPLETO)
# ============================================================================

class CoffeeProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de perfiles de café.
    
    Endpoints generados automáticamente:
    - GET    /api/profiles/           Lista todos los perfiles
    - POST   /api/profiles/           Crea nuevo perfil
    - GET    /api/profiles/<id>/      Detalle de un perfil
    - PUT    /api/profiles/<id>/      Actualiza perfil completo
    - PATCH  /api/profiles/<id>/      Actualiza parcialmente
    - DELETE /api/profiles/<id>/      Elimina perfil
    
    Acciones personalizadas:
    - POST /api/profiles/<id>/predict/   Predice con este perfil
    """
    
    queryset = CoffeeProfile.objects.filter(is_active=True)
    serializer_class = CoffeeProfileSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        Permite filtrar perfiles por query parameters.
        
        Filtros disponibles:
        - country: Filtrar por país
        - processing: Filtrar por método de procesamiento
        - search: Búsqueda en nombre y descripción
        """
        queryset = super().get_queryset()
        
        # Filtrar por país
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country_of_origin__icontains=country)
        
        # Filtrar por procesamiento
        processing = self.request.query_params.get('processing', None)
        if processing:
            queryset = queryset.filter(processing_method__icontains=processing)
        
        # Búsqueda general
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                name__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def predict(self, request, pk=None):
        """
        POST /api/profiles/<id>/predict/
        
        Realiza una predicción usando los parámetros de este perfil.
        
        Útil para predecir rápidamente con perfiles guardados sin
        tener que ingresar todos los parámetros manualmente.
        
        Response (201 Created):
        {
            "success": true,
            "profile_used": {...},
            "prediction_result": {...}
        }
        """
        try:
            # Obtener el perfil
            profile = self.get_object()
            
            # Convertir perfil a parámetros de predicción
            params = profile.to_prediction_params()
            
            # Realizar predicción
            prediction_result = predict_coffee_notes(**params)
            
            # Guardar en BD (similar a predict_view)
            notas = prediction_result['notas_predichas']
            Prediction.objects.create(
                country_of_origin=params['country_of_origin'],
                processing_method=params['processing_method'],
                variety=params['variety'],
                altitude_mean=params['altitude_mean'],
                moisture=params['moisture'],
                category_one_defects=params.get('category_one_defects', 0),
                category_two_defects=params.get('category_two_defects', 0),
                cluster_asignado=prediction_result['cluster_asignado'],
                confianza=prediction_result['confianza'],
                distancia_centroide=prediction_result['distancia_centroide'],
                aroma=notas.get('Aroma', 0),
                flavor=notas.get('Flavor', 0),
                aftertaste=notas.get('Aftertaste', 0),
                acidity=notas.get('Acidity', 0),
                body=notas.get('Body', 0),
                balance=notas.get('Balance', 0),
                total_cup_points=notas.get('Total.Cup.Points', 0)
            )
            
            return Response({
                'success': True,
                'profile_used': CoffeeProfileSerializer(profile).data,
                'prediction_result': prediction_result
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"❌ Error en predict con perfil: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# ENDPOINT: ESTADÍSTICAS DEL SISTEMA
# ============================================================================

@api_view(['GET'])
def statistics_view(request):
    """
    GET /api/statistics/
    
    Retorna estadísticas generales del sistema.
    
    Response (200 OK):
    {
        "total_predictions": 1250,
        "predictions_by_cluster": {
            "0": 450,
            "1": 350,
            ...
        },
        "predictions_by_country": {
            "Ethiopia": 200,
            "Brazil": 180,
            ...
        },
        "average_confidence": 87.5,
        "total_profiles": 25
    }
    """
    try:
        # Total de predicciones
        total_predictions = Prediction.objects.count()
        
        # Predicciones por cluster
        predictions_by_cluster = dict(
            Prediction.objects.values('cluster_asignado')
            .annotate(count=Count('id'))
            .values_list('cluster_asignado', 'count')
        )
        
        # Predicciones por país
        predictions_by_country = dict(
            Prediction.objects.values('country_of_origin')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
            .values_list('country_of_origin', 'count')
        )
        
        # Confianza promedio
        avg_confidence = Prediction.objects.aggregate(
            avg=Avg('confianza')
        )['avg'] or 0.0
        
        # Total de perfiles
        total_profiles = CoffeeProfile.objects.filter(is_active=True).count()
        
        return Response({
            'total_predictions': total_predictions,
            'predictions_by_cluster': predictions_by_cluster,
            'predictions_by_country': predictions_by_country,
            'average_confidence': round(avg_confidence, 2),
            'total_profiles': total_profiles
        })
    
    except Exception as e:
        logger.error(f"❌ Error en statistics_view: {e}", exc_info=True)
        return Response({
            'error': 'Error al obtener estadísticas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
