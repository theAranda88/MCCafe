"""
SERIALIZERS - VALIDACIÓN Y FORMATO DE DATOS API
================================================

Este módulo define los serializers de Django REST Framework para:
1. Validar datos de entrada (requests)
2. Formatear datos de salida (responses)
3. Transformar entre modelos Django y JSON

SERIALIZERS IMPLEMENTADOS:
- PredictionInputSerializer: Valida parámetros de predicción
- PredictionOutputSerializer: Formatea respuesta de predicción
- PredictionHistorySerializer: Serializa historial de predicciones
- CoffeeProfileSerializer: CRUD de perfiles de café
- ClusterInfoSerializer: Info de clusters

Autor: Proyecto Café ML
Fecha: 2026-01-05
"""

from rest_framework import serializers
from .models import Prediction, CoffeeProfile, ClusterInfo


class PredictionInputSerializer(serializers.Serializer):
    """
    Serializer para validar los parámetros de entrada de una predicción.
    
    VALIDACIONES:
    - Campos requeridos vs opcionales
    - Rangos de valores numéricos
    - Tipos de datos correctos
    
    USO:
    Se usa en la vista POST /api/predict/ para validar el request body.
    """
    
    # ========================================================================
    # CAMPOS REQUERIDOS
    # ========================================================================
    
    country_of_origin = serializers.CharField(
        max_length=100,
        required=True,
        help_text="País de origen del café (ej: Ethiopia, Brazil, Colombia)"
    )
    
    processing_method = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Método de procesamiento (ej: Washed / Wet, Natural / Dry, Honey)"
    )
    
    variety = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Variedad del café (ej: Bourbon, Typica, Caturra, Geisha)"
    )
    
    # ========================================================================
    # CAMPOS NUMÉRICOS CON VALIDACIÓN DE RANGO
    # ========================================================================
    
    altitude_mean = serializers.FloatField(
        required=True,
        min_value=0.0,
        max_value=5000.0,
        help_text="Altitud promedio en metros (0-5000)"
    )
    
    moisture = serializers.FloatField(
        required=True,
        min_value=0.0,
        max_value=1.0,
        help_text="Nivel de humedad (0.0-1.0, donde 0.12 = 12%)"
    )
    
    # ========================================================================
    # CAMPOS OPCIONALES CON VALORES POR DEFECTO
    # ========================================================================
    
    category_one_defects = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        help_text="Número de defectos categoría 1 (primarios)"
    )
    
    category_two_defects = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        help_text="Número de defectos categoría 2 (secundarios)"
    )
    
    def validate_moisture(self, value):
        """
        Validación personalizada para humedad.
        
        La humedad debe estar en un rango realista para café procesado.
        Típicamente entre 0.08 y 0.14 (8% a 14%).
        
        Args:
            value: Valor de humedad a validar
        
        Returns:
            float: Valor validado
        
        Raises:
            ValidationError: Si el valor está fuera del rango recomendado
        """
        if value < 0.05 or value > 0.20:
            raise serializers.ValidationError(
                "La humedad debe estar entre 0.05 y 0.20 (5% a 20%). "
                f"Valor recibido: {value}"
            )
        return value
    
    def validate_altitude_mean(self, value):
        """
        Validación personalizada para altitud.
        
        Aunque el café puede crecer a diferentes altitudes, hay rangos típicos:
        - Bajo: 0-900m
        - Medio: 900-1500m
        - Alto: 1500-2400m
        - Muy alto: >2400m
        
        Args:
            value: Valor de altitud a validar
        
        Returns:
            float: Valor validado
        
        Raises:
            ValidationError: Si el valor es poco realista
        """
        if value > 3500:
            raise serializers.ValidationError(
                "La altitud es poco realista para cultivo de café. "
                f"Máximo recomendado: 3500m. Valor recibido: {value}m"
            )
        return value


class PredictionOutputSerializer(serializers.Serializer):
    """
    Serializer para formatear la respuesta de predicción.
    
    Estructura la respuesta con:
    - Información del cluster asignado
    - Notas sensoriales predichas
    - Confianza de la predicción
    - Metadata adicional
    """
    
    # Resultado principal
    cluster_asignado = serializers.IntegerField(
        help_text="ID del cluster K-means asignado"
    )
    
    confianza = serializers.FloatField(
        help_text="Porcentaje de confianza (0-100)"
    )
    
    distancia_centroide = serializers.FloatField(
        help_text="Distancia euclidiana al centroide del cluster"
    )
    
    # Notas sensoriales (nested object)
    notas_predichas = serializers.DictField(
        child=serializers.FloatField(),
        help_text="Diccionario con las 7 notas sensoriales predichas"
    )
    
    # Información del cluster (nested object)
    cluster_info = serializers.DictField(
        help_text="Información del cluster asignado"
    )
    
    # Metadata
    metodo = serializers.CharField(
        help_text="Método ML usado (K-means)"
    )
    
    input_procesado = serializers.DictField(
        required=False,
        help_text="Parámetros de entrada procesados"
    )


class PredictionHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Prediction (historial).
    
    Convierte objetos Prediction de la BD a JSON y viceversa.
    Incluye todas las propiedades del modelo.
    """
    
    # Propiedades computadas del modelo (read-only)
    notas_dict = serializers.ReadOnlyField()
    parametros_dict = serializers.ReadOnlyField()
    
    class Meta:
        model = Prediction
        fields = '__all__'  # Incluir todos los campos del modelo
        read_only_fields = ['id', 'created_at']  # Campos no editables
    
    def to_representation(self, instance):
        """
        Personaliza la representación JSON de una predicción.
        
        Organiza los datos en secciones lógicas para mejor legibilidad.
        
        Args:
            instance: Objeto Prediction de la BD
        
        Returns:
            dict: Representación personalizada en JSON
        """
        representation = super().to_representation(instance)
        
        # Reorganizar en secciones
        return {
            'id': representation['id'],
            'fecha': representation['created_at'],
            'parametros_entrada': {
                'country_of_origin': representation['country_of_origin'],
                'processing_method': representation['processing_method'],
                'variety': representation['variety'],
                'altitude_mean': representation['altitude_mean'],
                'moisture': representation['moisture'],
                'category_one_defects': representation['category_one_defects'],
                'category_two_defects': representation['category_two_defects']
            },
            'resultado': {
                'cluster_asignado': representation['cluster_asignado'],
                'confianza': representation['confianza'],
                'distancia_centroide': representation['distancia_centroide']
            },
            'notas_sensoriales': {
                'Aroma': representation['aroma'],
                'Flavor': representation['flavor'],
                'Aftertaste': representation['aftertaste'],
                'Acidity': representation['acidity'],
                'Body': representation['body'],
                'Balance': representation['balance'],
                'Total.Cup.Points': representation['total_cup_points']
            }
        }


class CoffeeProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo CoffeeProfile.
    
    Permite CRUD completo de perfiles de café:
    - Create: Guardar nuevo perfil
    - Read: Listar/detallar perfiles
    - Update: Modificar perfil existente
    - Delete: Eliminar perfil
    """
    
    class Meta:
        model = CoffeeProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validación cruzada de campos.
        
        Verifica que los datos del perfil sean coherentes.
        
        Args:
            data: Diccionario con los datos a validar
        
        Returns:
            dict: Datos validados
        
        Raises:
            ValidationError: Si hay inconsistencias
        """
        # Validar que el nombre no esté vacío
        if 'name' in data and not data['name'].strip():
            raise serializers.ValidationError({
                'name': 'El nombre del perfil no puede estar vacío'
            })
        
        # Validar humedad realista
        if 'moisture' in data:
            if data['moisture'] < 0.05 or data['moisture'] > 0.20:
                raise serializers.ValidationError({
                    'moisture': 'La humedad debe estar entre 0.05 y 0.20'
                })
        
        return data


class ClusterInfoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo ClusterInfo.
    
    Usado para cachear y consultar información de clusters
    desde la base de datos.
    """
    
    class Meta:
        model = ClusterInfo
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClusterStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de clusters (sin persistencia en BD).
    
    Usado para retornar información de clusters directamente
    desde ml_service.py sin guardar en BD.
    """
    
    cluster_id = serializers.IntegerField(
        help_text="ID del cluster"
    )
    
    n_samples = serializers.IntegerField(
        help_text="Número de muestras en el cluster"
    )
    
    categorical_modes = serializers.DictField(
        help_text="Valores más comunes de variables categóricas"
    )
    
    numeric_means = serializers.DictField(
        help_text="Promedios de variables numéricas de entrada"
    )
    
    output_means = serializers.DictField(
        help_text="Promedios de notas sensoriales del cluster"
    )


class ModelInfoSerializer(serializers.Serializer):
    """
    Serializer para información general del modelo ML.
    
    Retorna metadata del modelo K-means entrenado.
    """
    
    model_type = serializers.CharField(
        help_text="Tipo de modelo (kmeans)"
    )
    
    n_clusters = serializers.IntegerField(
        help_text="Número de clusters encontrados"
    )
    
    silhouette_score = serializers.FloatField(
        help_text="Silhouette score (calidad del clustering)"
    )
    
    inertia = serializers.FloatField(
        help_text="Inercia del modelo (suma de distancias al cuadrado)"
    )
    
    training_samples = serializers.IntegerField(
        help_text="Número de muestras usadas en entrenamiento"
    )
    
    input_features = serializers.DictField(
        help_text="Diccionario con features de entrada"
    )
    
    output_features = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de notas sensoriales predichas"
    )
    
    version = serializers.CharField(
        help_text="Versión del modelo"
    )
    
    created_at = serializers.CharField(
        help_text="Fecha de creación del modelo"
    )
