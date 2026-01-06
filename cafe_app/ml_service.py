"""
SERVICIO DE MACHINE LEARNING - PREDICCIÓN DE NOTAS SENSORIALES DE CAFÉ
=========================================================================

Este módulo es el CEREBRO del sistema de predicción. Contiene toda la lógica
necesaria para cargar el modelo K-means entrenado y realizar predicciones de
notas sensoriales basándose en parámetros de entrada del café.

FLUJO DE PREDICCIÓN:
1. Cargar modelos .pkl en memoria (una sola vez al iniciar)
2. Recibir parámetros de entrada del café
3. Codificar variables categóricas (país, procesamiento, variedad)
4. Normalizar variables numéricas (altitud, humedad, defectos)
5. Calcular distancia a cada centroide del K-means
6. Asignar al cluster más cercano
7. Retornar notas sensoriales promedio de ese cluster

COMPONENTES CARGADOS:
- modelo_kmeans.pkl: Centroides y configuración del modelo
- scaler_input.pkl: StandardScaler para normalizar entrada
- scaler_output.pkl: StandardScaler para normalizar salida (no usado en predicción)
- encoders.pkl: LabelEncoders para variables categóricas
- df_clustered.pkl: DataFrame con datos de entrenamiento y clusters
- metadata.json: Información sobre clusters y características

Autor: Proyecto Café ML
Fecha: 2026-01-05
Versión: 1.0
"""

import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from django.conf import settings
import logging

# Configurar logging para depuración
logger = logging.getLogger(__name__)


class MLModelNotLoadedError(Exception):
    """Excepción personalizada cuando el modelo no está cargado."""
    pass


class CoffeePredictionService:
    """
    Servicio singleton para predicción de notas sensoriales de café.
    
    Este servicio carga los modelos ML una sola vez en memoria y los reutiliza
    para todas las predicciones, mejorando el rendimiento significativamente.
    
    Patrón Singleton: Solo existe una instancia de esta clase en toda la aplicación.
    """
    
    _instance = None  # Variable de clase para almacenar la única instancia
    _models_loaded = False  # Flag para saber si los modelos están cargados
    
    def __new__(cls):
        """
        Implementación del patrón Singleton.
        Garantiza que solo exista una instancia de esta clase.
        """
        if cls._instance is None:
            cls._instance = super(CoffeePredictionService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Inicializa el servicio de predicción.
        
        Solo carga los modelos la primera vez que se instancia.
        Intentos posteriores de inicialización no recargan los modelos.
        """
        if not self._models_loaded:
            self.ml_models_dir = Path(settings.BASE_DIR) / "ml_models"
            self._load_models()
    
    def _load_models(self):
        """
        Carga todos los modelos y transformadores necesarios desde archivos .pkl
        
        ARCHIVOS CARGADOS:
        - modelo_kmeans.pkl: Modelo K-means con centroides
        - scaler_input.pkl: Escalador para características de entrada
        - scaler_output.pkl: Escalador para características de salida
        - encoders.pkl: Diccionario con LabelEncoders para variables categóricas
        - df_clustered.pkl: DataFrame con datos de entrenamiento
        - metadata.json: Metadatos del modelo (configuración, estadísticas)
        
        Raises:
            FileNotFoundError: Si algún archivo del modelo no existe
            Exception: Si hay error al cargar los archivos
        """
        try:
            logger.info("🔄 Iniciando carga de modelos ML...")
            
            # 1. CARGAR MODELO K-MEANS
            # Contiene: centroides, labels, k, silhouette score, inercia
            kmeans_path = self.ml_models_dir / "modelo_kmeans.pkl"
            if not kmeans_path.exists():
                raise FileNotFoundError(f"No se encuentra {kmeans_path}")
            
            self.kmeans_model = joblib.load(kmeans_path)
            logger.info(f"✓ Modelo K-means cargado: {self.kmeans_model['k']} clusters")
            
            # 2. CARGAR ESCALADORES (StandardScaler)
            # scaler_input: Normaliza características de entrada (mean=0, std=1)
            scaler_input_path = self.ml_models_dir / "scaler_input.pkl"
            if not scaler_input_path.exists():
                raise FileNotFoundError(f"No se encuentra {scaler_input_path}")
            
            self.scaler_input = joblib.load(scaler_input_path)
            logger.info("✓ Scaler de entrada cargado")
            
            # scaler_output: Normaliza características de salida (usado en entrenamiento)
            scaler_output_path = self.ml_models_dir / "scaler_output.pkl"
            if not scaler_output_path.exists():
                raise FileNotFoundError(f"No se encuentra {scaler_output_path}")
            
            self.scaler_output = joblib.load(scaler_output_path)
            logger.info("✓ Scaler de salida cargado")
            
            # 3. CARGAR ENCODERS (LabelEncoder para categóricas)
            # Diccionario con encoders para: Country.of.Origin, Processing.Method, Variety
            encoders_path = self.ml_models_dir / "encoders.pkl"
            if not encoders_path.exists():
                raise FileNotFoundError(f"No se encuentra {encoders_path}")
            
            self.encoders = joblib.load(encoders_path)
            logger.info(f"✓ Encoders cargados: {list(self.encoders.keys())}")
            
            # 4. CARGAR DATAFRAME CON CLUSTERS
            # Contiene datos de entrenamiento con su cluster asignado
            # Usado para calcular estadísticas y promedios por cluster
            df_clustered_path = self.ml_models_dir / "df_clustered.pkl"
            if not df_clustered_path.exists():
                raise FileNotFoundError(f"No se encuentra {df_clustered_path}")
            
            self.df_clustered = joblib.load(df_clustered_path)
            logger.info(f"✓ DataFrame cargado: {len(self.df_clustered)} muestras")
            
            # 5. CARGAR METADATA (JSON)
            # Contiene: features, cluster stats, configuración del modelo
            metadata_path = self.ml_models_dir / "metadata.json"
            if not metadata_path.exists():
                raise FileNotFoundError(f"No se encuentra {metadata_path}")
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            logger.info("✓ Metadata cargado")
            
            # 6. EXTRAER CONFIGURACIÓN DEL METADATA
            # Lista de características categóricas esperadas
            self.categorical_features = self.metadata['input_features']['categorical']
            
            # Lista de características numéricas esperadas
            self.numeric_features = self.metadata['input_features']['numeric']
            
            # Lista completa de features en orden correcto
            self.input_feature_names = self.metadata['input_features']['all']
            
            # Lista de notas sensoriales a predecir
            self.output_features = self.metadata['output_features']
            
            # Número de clusters del modelo
            self.n_clusters = self.metadata['n_clusters']
            
            logger.info(f"✓ Configuración:")
            logger.info(f"  - Features categóricas: {self.categorical_features}")
            logger.info(f"  - Features numéricas: {self.numeric_features}")
            logger.info(f"  - Output features: {self.output_features}")
            logger.info(f"  - Número de clusters: {self.n_clusters}")
            
            # Marcar modelos como cargados
            CoffeePredictionService._models_loaded = True
            logger.info("✅ TODOS LOS MODELOS CARGADOS EXITOSAMENTE\n")
            
        except FileNotFoundError as e:
            logger.error(f"❌ Error: Archivo del modelo no encontrado - {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error al cargar modelos: {e}")
            raise
    
    def _encode_categorical(self, value: str, feature_name: str) -> int:
        """
        Codifica una variable categórica a número usando LabelEncoder.
        
        Si el valor no existe en el encoder (valor nuevo no visto en entrenamiento),
        retorna la codificación del primer valor conocido (fallback seguro).
        
        Args:
            value: Valor categórico a codificar (ej: "Ethiopia", "Washed / Wet")
            feature_name: Nombre de la característica (ej: "Country.of.Origin")
        
        Returns:
            int: Valor numérico codificado
            
        Example:
            >>> _encode_categorical("Ethiopia", "Country.of.Origin")
            5  # Número asignado a Ethiopia
        """
        if feature_name not in self.encoders:
            logger.warning(f"⚠️ Encoder no encontrado para '{feature_name}', usando 0")
            return 0
        
        encoder = self.encoders[feature_name]
        
        try:
            # Intentar codificar el valor
            if value in encoder.classes_:
                encoded = encoder.transform([value])[0]
                logger.debug(f"Codificado '{value}' → {encoded}")
                return int(encoded)
            else:
                # Valor desconocido: usar el primer valor conocido
                fallback_value = encoder.classes_[0]
                encoded = encoder.transform([fallback_value])[0]
                logger.warning(
                    f"⚠️ Valor '{value}' no encontrado en {feature_name}. "
                    f"Usando '{fallback_value}' (código {encoded})"
                )
                return int(encoded)
        except Exception as e:
            logger.error(f"❌ Error codificando {feature_name}='{value}': {e}")
            return 0
    
    def preprocess_input(
        self,
        country_of_origin: Optional[str] = None,
        processing_method: Optional[str] = None,
        variety: Optional[str] = None,
        altitude_mean: Optional[float] = None,
        moisture: Optional[float] = None,
        category_one_defects: int = 0,
        category_two_defects: int = 0
    ) -> np.ndarray:
        """
        Preprocesa los parámetros de entrada para la predicción.
        
        PASOS:
        1. Codifica variables categóricas (texto → número)
        2. Asigna valores por defecto a variables faltantes
        3. Construye vector en el orden correcto
        4. Normaliza usando StandardScaler
        
        Args:
            country_of_origin: País de origen del café (ej: "Ethiopia")
            processing_method: Método de procesamiento (ej: "Washed / Wet")
            variety: Variedad del café (ej: "Bourbon")
            altitude_mean: Altitud promedio en metros (ej: 2000.0)
            moisture: Nivel de humedad (ej: 0.12)
            category_one_defects: Defectos categoría 1 (default: 0)
            category_two_defects: Defectos categoría 2 (default: 0)
        
        Returns:
            np.ndarray: Vector normalizado listo para predicción (shape: 1 x n_features)
            
        Example:
            >>> preprocessed = service.preprocess_input(
            ...     country_of_origin="Ethiopia",
            ...     processing_method="Washed / Wet",
            ...     altitude_mean=2000.0,
            ...     moisture=0.12
            ... )
            >>> preprocessed.shape
            (1, 7)  # 7 características de entrada
        """
        # Diccionario para almacenar valores procesados
        input_values = {}
        
        # 1. CODIFICAR VARIABLES CATEGÓRICAS
        logger.debug("Codificando variables categóricas...")
        
        for feature in self.categorical_features:
            if feature == 'Country.of.Origin':
                value = country_of_origin if country_of_origin else 'Unknown'
            elif feature == 'Processing.Method':
                value = processing_method if processing_method else 'Unknown'
            elif feature == 'Variety':
                value = variety if variety else 'Unknown'
            else:
                value = 'Unknown'
            
            # Codificar el valor
            input_values[feature] = self._encode_categorical(value, feature)
        
        # 2. ASIGNAR VARIABLES NUMÉRICAS
        logger.debug("Asignando variables numéricas...")
        
        # Calcular valores por defecto (promedio del dataset de entrenamiento)
        default_altitude = float(self.df_clustered['altitude_mean_meters'].mean()) \
            if 'altitude_mean_meters' in self.df_clustered.columns else 1500.0
        
        default_moisture = float(self.df_clustered['Moisture'].mean()) \
            if 'Moisture' in self.df_clustered.columns else 0.11
        
        # Asignar valores (usar default si no se proporciona)
        if 'altitude_mean_meters' in self.numeric_features:
            input_values['altitude_mean_meters'] = \
                altitude_mean if altitude_mean is not None else default_altitude
        
        if 'Moisture' in self.numeric_features:
            input_values['Moisture'] = \
                moisture if moisture is not None else default_moisture
        
        if 'Category.One.Defects' in self.numeric_features:
            input_values['Category.One.Defects'] = category_one_defects
        
        if 'Category.Two.Defects' in self.numeric_features:
            input_values['Category.Two.Defects'] = category_two_defects
        
        # 3. CONSTRUIR VECTOR EN EL ORDEN CORRECTO
        # El orden debe coincidir exactamente con el usado en entrenamiento
        input_vector = []
        for feature_name in self.input_feature_names:
            if feature_name in input_values:
                input_vector.append(input_values[feature_name])
            else:
                # Si falta alguna feature, usar 0 como fallback
                logger.warning(f"⚠️ Feature '{feature_name}' no encontrado, usando 0")
                input_vector.append(0.0)
        
        # Convertir a numpy array con shape (1, n_features)
        input_array = np.array(input_vector).reshape(1, -1)
        
        logger.debug(f"Vector antes de normalizar: {input_array}")
        
        # 4. NORMALIZAR USANDO SCALER
        # Transforma a media=0, std=1 (mismo que en entrenamiento)
        input_scaled = self.scaler_input.transform(input_array)
        
        logger.debug(f"Vector normalizado: {input_scaled}")
        
        return input_scaled
    
    def predict(
        self,
        country_of_origin: Optional[str] = None,
        processing_method: Optional[str] = None,
        variety: Optional[str] = None,
        altitude_mean: Optional[float] = None,
        moisture: Optional[float] = None,
        category_one_defects: int = 0,
        category_two_defects: int = 0
    ) -> Dict:
        """
        Realiza la predicción de notas sensoriales para un café.
        
        ALGORITMO:
        1. Preprocesar entrada (codificar + normalizar)
        2. Calcular distancia euclidiana a cada centroide del K-means
        3. Asignar al cluster más cercano
        4. Obtener notas promedio de ese cluster
        5. Calcular confianza basada en distancia
        
        Args:
            country_of_origin: País de origen del café
            processing_method: Método de procesamiento
            variety: Variedad del café
            altitude_mean: Altitud promedio en metros
            moisture: Nivel de humedad
            category_one_defects: Defectos categoría 1
            category_two_defects: Defectos categoría 2
        
        Returns:
            Dict con:
                - cluster_asignado (int): ID del cluster (0 a k-1)
                - notas_predichas (dict): Notas sensoriales predichas
                - confianza (float): Porcentaje de confianza (0-100)
                - distancia_centroide (float): Distancia al centroide
                - cluster_info (dict): Información del cluster
        
        Raises:
            MLModelNotLoadedError: Si los modelos no están cargados
            
        Example:
            >>> result = service.predict(
            ...     country_of_origin="Ethiopia",
            ...     processing_method="Washed / Wet",
            ...     altitude_mean=2000.0,
            ...     moisture=0.12
            ... )
            >>> result['notas_predichas']['Aroma']
            7.85
        """
        # Verificar que los modelos estén cargados
        if not self._models_loaded:
            raise MLModelNotLoadedError(
                "Los modelos ML no están cargados. Llama a _load_models() primero."
            )
        
        logger.info("🔮 Iniciando predicción...")
        
        try:
            # 1. PREPROCESAR ENTRADA
            input_scaled = self.preprocess_input(
                country_of_origin=country_of_origin,
                processing_method=processing_method,
                variety=variety,
                altitude_mean=altitude_mean,
                moisture=moisture,
                category_one_defects=category_one_defects,
                category_two_defects=category_two_defects
            )
            
            # 2. OBTENER CENTROIDES DEL MODELO K-MEANS
            # Los centroides están en el espacio combinado (input + output)
            # Solo usamos la parte de INPUT para calcular distancias
            centroids = self.kmeans_model['centroids']
            n_input_features = len(self.input_feature_names)
            
            # Extraer solo la parte de entrada de los centroides
            input_centroids = centroids[:, :n_input_features]
            
            logger.debug(f"Centroides de entrada shape: {input_centroids.shape}")
            
            # 3. CALCULAR DISTANCIA EUCLIDIANA A CADA CENTROIDE
            # Distancia = sqrt(sum((x - centroid)^2))
            distances = np.linalg.norm(input_centroids - input_scaled, axis=1)
            
            logger.debug(f"Distancias a centroides: {distances}")
            
            # 4. ASIGNAR AL CLUSTER MÁS CERCANO
            cluster_asignado = int(np.argmin(distances))
            distancia_centroide = float(distances[cluster_asignado])
            
            logger.info(f"✓ Cluster asignado: {cluster_asignado}")
            logger.info(f"✓ Distancia al centroide: {distancia_centroide:.4f}")
            
            # 5. OBTENER DATOS DEL CLUSTER ASIGNADO
            cluster_data = self.df_clustered[
                self.df_clustered['Cluster'] == cluster_asignado
            ]
            
            # 6. CALCULAR NOTAS PROMEDIO DEL CLUSTER
            notas_predichas = {}
            for note in self.output_features:
                if note in cluster_data.columns:
                    nota_promedio = float(cluster_data[note].mean())
                    notas_predichas[note] = round(nota_promedio, 2)
            
            logger.info(f"✓ Notas predichas: {notas_predichas}")
            
            # 7. CALCULAR CONFIANZA
            # Confianza inversa a la distancia: cerca = alta confianza
            # Formula: max(0, 100 - (distancia * factor))
            # Factor de escala: 10 (ajustable según necesidad)
            confianza = max(0.0, 100.0 - (distancia_centroide * 10))
            confianza = round(confianza, 1)
            
            logger.info(f"✓ Confianza: {confianza}%")
            
            # 8. OBTENER INFORMACIÓN DEL CLUSTER DESDE METADATA
            cluster_stats = self.metadata['cluster_stats'].get(
                str(cluster_asignado), {}
            )
            
            cluster_info = {
                'cluster_id': cluster_asignado,
                'n_samples': cluster_stats.get('count', 0),
                'categorical_modes': cluster_stats.get('categorical_modes', {}),
                'numeric_means': cluster_stats.get('numeric_means', {})
            }
            
            # 9. CONSTRUIR RESPUESTA
            resultado = {
                'cluster_asignado': cluster_asignado,
                'notas_predichas': notas_predichas,
                'confianza': confianza,
                'distancia_centroide': round(distancia_centroide, 4),
                'cluster_info': cluster_info,
                'metodo': 'K-means (No supervisado)',
                'input_procesado': {
                    'country': country_of_origin,
                    'processing': processing_method,
                    'variety': variety,
                    'altitude': altitude_mean,
                    'moisture': moisture
                }
            }
            
            logger.info("✅ Predicción completada exitosamente\n")
            
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error durante la predicción: {e}")
            raise
    
    def get_clusters_info(self) -> List[Dict]:
        """
        Obtiene información detallada de todos los clusters.
        
        Útil para:
        - Mostrar estadísticas de clusters al usuario
        - Análisis exploratorio
        - Debugging
        
        Returns:
            List[Dict]: Lista con información de cada cluster
            
        Example:
            >>> clusters = service.get_clusters_info()
            >>> clusters[0]['n_samples']
            450
        """
        if not self._models_loaded:
            raise MLModelNotLoadedError("Modelos no cargados")
        
        clusters_info = []
        
        for cluster_id in range(self.n_clusters):
            cluster_stats = self.metadata['cluster_stats'].get(str(cluster_id), {})
            
            info = {
                'cluster_id': cluster_id,
                'n_samples': cluster_stats.get('count', 0),
                'categorical_modes': cluster_stats.get('categorical_modes', {}),
                'numeric_means': cluster_stats.get('numeric_means', {}),
                'output_means': cluster_stats.get('output_means', {})
            }
            
            clusters_info.append(info)
        
        return clusters_info
    
    def get_model_info(self) -> Dict:
        """
        Obtiene información general del modelo.
        
        Returns:
            Dict con metadata del modelo (n_clusters, silhouette, features, etc.)
        """
        if not self._models_loaded:
            raise MLModelNotLoadedError("Modelos no cargados")
        
        return {
            'model_type': self.metadata['model_type'],
            'n_clusters': self.metadata['n_clusters'],
            'silhouette_score': self.metadata['silhouette_score'],
            'inertia': self.metadata['inertia'],
            'training_samples': self.metadata['training_samples'],
            'input_features': self.metadata['input_features'],
            'output_features': self.metadata['output_features'],
            'version': self.metadata['version'],
            'created_at': self.metadata['created_at']
        }


# ============================================================================
# INSTANCIA GLOBAL DEL SERVICIO (Singleton)
# ============================================================================
# Esta instancia se crea una sola vez y se reutiliza en toda la aplicación
# Los modelos se cargan en memoria la primera vez y permanecen disponibles

prediction_service = CoffeePredictionService()


# ============================================================================
# FUNCIONES DE CONVENIENCIA (Wrappers)
# ============================================================================
# Estas funciones facilitan el uso del servicio desde las vistas de Django

def predict_coffee_notes(**kwargs) -> Dict:
    """
    Función wrapper para realizar predicciones.
    
    Args:
        **kwargs: Parámetros del café (country_of_origin, processing_method, etc.)
    
    Returns:
        Dict: Resultado de la predicción
    """
    return prediction_service.predict(**kwargs)


def get_all_clusters_info() -> List[Dict]:
    """
    Función wrapper para obtener información de todos los clusters.
    
    Returns:
        List[Dict]: Información de cada cluster
    """
    return prediction_service.get_clusters_info()


def get_model_metadata() -> Dict:
    """
    Función wrapper para obtener metadata del modelo.
    
    Returns:
        Dict: Información general del modelo
    """
    return prediction_service.get_model_info()
