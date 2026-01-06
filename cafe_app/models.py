"""
MODELOS DE BASE DE DATOS - SISTEMA DE PREDICCIÓN DE CAFÉ
==========================================================

Este módulo define los modelos de Django (tablas de base de datos) para
almacenar información relacionada con las predicciones de café.

MODELOS IMPLEMENTADOS:
1. Prediction: Almacena cada predicción realizada (historial)
2. CoffeeProfile: Perfiles de café guardados por usuarios
3. ClusterInfo: Metadata de clusters (opcional, puede usarse para cache)

PROPÓSITO:
- Mantener historial de predicciones para análisis
- Permitir a usuarios guardar perfiles favoritos
- Analizar tendencias y patrones de uso
- Auditoría y trazabilidad

Autor: Proyecto Café ML
Fecha: 2026-01-05
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Prediction(models.Model):
    """
    Modelo para almacenar el historial de predicciones realizadas.
    
    Cada vez que un usuario solicita una predicción, se guarda un registro
    con los parámetros de entrada y el resultado obtenido.
    
    USOS:
    - Historial de predicciones
    - Análisis de tendencias
    - Auditoría
    - Estadísticas de uso
    """
    
    # ========================================================================
    # PARÁMETROS DE ENTRADA (Lo que el usuario proporcionó)
    # ========================================================================
    
    country_of_origin = models.CharField(
        max_length=100,
        verbose_name="País de Origen",
        help_text="País donde se cultivó el café (ej: Ethiopia, Brazil)"
    )
    
    processing_method = models.CharField(
        max_length=100,
        verbose_name="Método de Procesamiento",
        help_text="Método usado para procesar el café (ej: Washed / Wet, Natural / Dry)"
    )
    
    variety = models.CharField(
        max_length=100,
        verbose_name="Variedad",
        help_text="Variedad del café (ej: Bourbon, Typica, Caturra)"
    )
    
    altitude_mean = models.FloatField(
        verbose_name="Altitud Promedio (metros)",
        help_text="Altitud promedio donde se cultivó el café",
        validators=[MinValueValidator(0), MaxValueValidator(5000)]
    )
    
    moisture = models.FloatField(
        verbose_name="Humedad",
        help_text="Nivel de humedad del café (0.0 a 1.0)",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    category_one_defects = models.IntegerField(
        verbose_name="Defectos Categoría 1",
        default=0,
        help_text="Número de defectos primarios",
        validators=[MinValueValidator(0)]
    )
    
    category_two_defects = models.IntegerField(
        verbose_name="Defectos Categoría 2",
        default=0,
        help_text="Número de defectos secundarios",
        validators=[MinValueValidator(0)]
    )
    
    # ========================================================================
    # RESULTADOS DE LA PREDICCIÓN
    # ========================================================================
    
    cluster_asignado = models.IntegerField(
        verbose_name="Cluster Asignado",
        help_text="ID del cluster K-means al que fue asignado"
    )
    
    confianza = models.FloatField(
        verbose_name="Confianza (%)",
        help_text="Porcentaje de confianza de la predicción (0-100)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    distancia_centroide = models.FloatField(
        verbose_name="Distancia al Centroide",
        help_text="Distancia euclidiana al centroide del cluster"
    )
    
    # ========================================================================
    # NOTAS SENSORIALES PREDICHAS (Resultado principal)
    # ========================================================================
    
    aroma = models.FloatField(
        verbose_name="Aroma",
        help_text="Nota de aroma predicha (0-10)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    flavor = models.FloatField(
        verbose_name="Sabor",
        help_text="Nota de sabor predicha (0-10)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    aftertaste = models.FloatField(
        verbose_name="Retrogusto",
        help_text="Nota de retrogusto predicha (0-10)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    acidity = models.FloatField(
        verbose_name="Acidez",
        help_text="Nota de acidez predicha (0-10)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    body = models.FloatField(
        verbose_name="Cuerpo",
        help_text="Nota de cuerpo predicha (0-10)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    balance = models.FloatField(
        verbose_name="Balance",
        help_text="Nota de balance predicha (0-10)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    total_cup_points = models.FloatField(
        verbose_name="Puntos Totales",
        help_text="Puntuación total de la taza (0-100)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    
    # ========================================================================
    # METADATOS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora en que se realizó la predicción"
    )
    
    # Campo opcional para asociar predicciones con usuarios (si hay autenticación)
    # user = models.ForeignKey(
    #     'auth.User',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="Usuario"
    # )
    
    class Meta:
        verbose_name = "Predicción"
        verbose_name_plural = "Predicciones"
        ordering = ['-created_at']  # Más recientes primero
        indexes = [
            models.Index(fields=['-created_at']),  # Índice para consultas por fecha
            models.Index(fields=['cluster_asignado']),  # Índice para filtrar por cluster
        ]
    
    def __str__(self):
        """Representación en string del objeto."""
        return (
            f"Predicción {self.id} - {self.country_of_origin} "
            f"({self.created_at.strftime('%Y-%m-%d %H:%M')})"
        )
    
    @property
    def notas_dict(self):
        """
        Retorna las notas sensoriales como diccionario.
        
        Útil para serialización y respuestas API.
        
        Returns:
            dict: Diccionario con todas las notas sensoriales
        """
        return {
            'Aroma': self.aroma,
            'Flavor': self.flavor,
            'Aftertaste': self.aftertaste,
            'Acidity': self.acidity,
            'Body': self.body,
            'Balance': self.balance,
            'Total.Cup.Points': self.total_cup_points
        }
    
    @property
    def parametros_dict(self):
        """
        Retorna los parámetros de entrada como diccionario.
        
        Returns:
            dict: Diccionario con los parámetros de entrada
        """
        return {
            'country_of_origin': self.country_of_origin,
            'processing_method': self.processing_method,
            'variety': self.variety,
            'altitude_mean': self.altitude_mean,
            'moisture': self.moisture,
            'category_one_defects': self.category_one_defects,
            'category_two_defects': self.category_two_defects
        }


class CoffeeProfile(models.Model):
    """
    Modelo para almacenar perfiles de café guardados por usuarios.
    
    Permite a los usuarios guardar configuraciones de café que usan frecuentemente
    o que les gustan, para reutilizarlas sin tener que ingresarlas manualmente.
    
    USOS:
    - Guardar configuraciones favoritas
    - Comparar diferentes perfiles
    - Catálogo de cafés
    """
    
    # ========================================================================
    # INFORMACIÓN DEL PERFIL
    # ========================================================================
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nombre del Perfil",
        help_text="Nombre descriptivo del perfil (ej: 'Café Etíope Premium')"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción opcional del perfil"
    )
    
    # ========================================================================
    # PARÁMETROS DEL CAFÉ
    # ========================================================================
    
    country_of_origin = models.CharField(
        max_length=100,
        verbose_name="País de Origen"
    )
    
    processing_method = models.CharField(
        max_length=100,
        verbose_name="Método de Procesamiento"
    )
    
    variety = models.CharField(
        max_length=100,
        verbose_name="Variedad"
    )
    
    altitude_mean = models.FloatField(
        verbose_name="Altitud Promedio (metros)",
        validators=[MinValueValidator(0), MaxValueValidator(5000)]
    )
    
    moisture = models.FloatField(
        verbose_name="Humedad",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    category_one_defects = models.IntegerField(
        verbose_name="Defectos Categoría 1",
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    category_two_defects = models.IntegerField(
        verbose_name="Defectos Categoría 2",
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # ========================================================================
    # METADATOS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el perfil está activo"
    )
    
    # Campo opcional para asociar perfiles con usuarios
    # user = models.ForeignKey(
    #     'auth.User',
    #     on_delete=models.CASCADE,
    #     verbose_name="Usuario"
    # )
    
    class Meta:
        verbose_name = "Perfil de Café"
        verbose_name_plural = "Perfiles de Café"
        ordering = ['-created_at']
    
    def __str__(self):
        """Representación en string del objeto."""
        return f"{self.name} - {self.country_of_origin}"
    
    def to_prediction_params(self):
        """
        Convierte el perfil en parámetros para predicción.
        
        Returns:
            dict: Diccionario con parámetros listos para ml_service.predict()
        """
        return {
            'country_of_origin': self.country_of_origin,
            'processing_method': self.processing_method,
            'variety': self.variety,
            'altitude_mean': self.altitude_mean,
            'moisture': self.moisture,
            'category_one_defects': self.category_one_defects,
            'category_two_defects': self.category_two_defects
        }


class ClusterInfo(models.Model):
    """
    Modelo para almacenar información de clusters (OPCIONAL).
    
    Este modelo es opcional y sirve para cachear información de clusters
    en la base de datos. Puede ser útil para análisis y consultas rápidas
    sin tener que cargar el modelo ML.
    
    NOTA: La información real de clusters está en metadata.json y se carga
    desde ml_service.py. Este modelo es solo para persistencia/cache.
    """
    
    cluster_id = models.IntegerField(
        unique=True,
        verbose_name="ID del Cluster",
        help_text="Identificador único del cluster (0 a k-1)"
    )
    
    n_samples = models.IntegerField(
        verbose_name="Número de Muestras",
        help_text="Cantidad de muestras en este cluster"
    )
    
    # Características categóricas más comunes (JSON)
    categorical_modes = models.JSONField(
        verbose_name="Modas Categóricas",
        help_text="Valores más comunes de variables categóricas",
        default=dict
    )
    
    # Promedios de características numéricas (JSON)
    numeric_means = models.JSONField(
        verbose_name="Promedios Numéricos",
        help_text="Valores promedio de variables numéricas",
        default=dict
    )
    
    # Promedios de notas sensoriales (JSON)
    output_means = models.JSONField(
        verbose_name="Promedios de Notas",
        help_text="Valores promedio de notas sensoriales",
        default=dict
    )
    
    # Nombre descriptivo del cluster (opcional)
    cluster_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre del Cluster",
        help_text="Nombre descriptivo asignado manualmente (ej: 'Café Premium Alta Altitud')"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    class Meta:
        verbose_name = "Información de Cluster"
        verbose_name_plural = "Información de Clusters"
        ordering = ['cluster_id']
    
    def __str__(self):
        """Representación en string del objeto."""
        name = self.cluster_name if self.cluster_name else f"Cluster {self.cluster_id}"
        return f"{name} ({self.n_samples} muestras)"
