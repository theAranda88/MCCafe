# 📊 RESUMEN EJECUTIVO - Análisis del Notebook y Plan de Implementación

## 🎯 OBJETIVO DEL PROYECTO
Crear una aplicación web Django que permita predecir las **notas sensoriales de café de alta calidad** basándose en parámetros de entrada controlables por una empresa procesadora.

---

## 📋 ANÁLISIS DEL NOTEBOOK

### 1. CARACTERÍSTICAS DEL MODELO

#### **Entrada (Lo que controla la empresa):**
```
CATEGÓRICAS:
✓ Country.of.Origin     - País de origen del café
✓ Processing.Method     - Método de procesamiento (Washed, Natural, etc.)
✓ Variety               - Variedad del café (Bourbon, Typica, etc.)

NUMÉRICAS:
✓ altitude_mean_meters  - Altitud promedio en metros
✓ Moisture              - Nivel de humedad
✓ Category.One.Defects  - Defectos categoría 1
✓ Category.Two.Defects  - Defectos categoría 2
```

#### **Salida (Notas sensoriales predichas):**
```
✓ Aroma           - Aroma del café (escala 0-10)
✓ Flavor          - Sabor (escala 0-10)
✓ Aftertaste      - Retrogusto (escala 0-10)
✓ Acidity         - Acidez (escala 0-10)
✓ Body            - Cuerpo (escala 0-10)
✓ Balance         - Balance (escala 0-10)
✓ Total.Cup.Points - Puntuación total (escala 0-100)
```

---

### 2. TÉCNICA DE BALANCEO DE DATOS

**Problema identificado:**
- Dataset desbalanceado: ~90% Arabica, ~10% Robusta

**Solución implementada: SMOTE**
```python
SMOTE (Synthetic Minority Over-sampling Technique)
- Genera muestras sintéticas de la clase minoritaria
- NO duplica registros, CREA nuevos datos realistas
- Balancea el dataset al 50-50%
- Mejora la representatividad del modelo
```

**Librería usada:**
```bash
imbalanced-learn==0.12.4
```

---

### 3. MODELO DE MACHINE LEARNING

**Tipo:** K-means (Clustering - No supervisado)

**Características:**
```
• Algoritmo: K-means con inicializaciones múltiples
• Selección de k: Basado en Silhouette Score
• Rango evaluado: k = 2 a 8 clusters
• Preprocesamiento:
  - LabelEncoder para variables categóricas
  - StandardScaler para normalización
  - PCA para visualización
```

**Pipeline de procesamiento:**
```
Input → LabelEncoder → StandardScaler → K-means → Cluster → Notas Promedio
```

---

### 4. FLUJO DE PREDICCIÓN

```
1. Usuario ingresa parámetros del café
   ├─ País: Ethiopia
   ├─ Procesamiento: Washed / Wet
   ├─ Altitud: 2000 metros
   └─ Humedad: 0.12

2. Sistema codifica y escala datos
   ├─ LabelEncoder para categóricas
   └─ StandardScaler para numéricas

3. K-means asigna al cluster más cercano
   └─ Calcula distancia a centroides

4. Retorna notas promedio del cluster
   ├─ Aroma: 7.85
   ├─ Flavor: 7.92
   ├─ Acidity: 7.75
   └─ ...más notas
```

---

## 🗂️ ARCHIVOS A EXPORTAR DEL NOTEBOOK

```
ml_models/
├── modelo_kmeans.pkl      ← Modelo K-means entrenado
├── scaler_input.pkl       ← Escalador para entrada
├── scaler_output.pkl      ← Escalador para salida
├── encoders.pkl           ← Dict con LabelEncoders
├── df_clustered.pkl       ← DataFrame con clusters
└── metadata.json          ← Info de clusters y features
```

**Cómo exportar:**
```python
# En el notebook, al final, ejecutar:
%run export_model.py
```

---

## 🏗️ ARQUITECTURA DJANGO

```
proyecto_cafe_ml/
│
├── backend/
│   ├── settings.py         ✅ Ya existe
│   └── urls.py             ✅ Ya existe
│
├── cafe_app/
│   ├── models.py           🔧 A implementar
│   ├── serializers.py      🔧 A implementar
│   ├── ml_service.py       🔧 A implementar (CEREBRO)
│   ├── views.py            🔧 A implementar
│   └── urls.py             🔧 A implementar
│
├── ml_models/              ✅ Ya creado
│   └── (archivos .pkl)
│
├── data/                   ✅ Ya creado
│   └── merged_data_cleaned.csv
│
└── requirements.txt        ✅ Ya actualizado
```

---

## 📝 PLAN DE IMPLEMENTACIÓN

### **FASE 1: Preparación del Modelo** ✅
```
[✅] Analizar notebook completo
[✅] Crear estructura de directorios
[🔄] Ejecutar notebook y exportar modelos
```

### **FASE 2: Backend Django** (Siguiente)
```
[ ] Paso 1: Crear modelos de BD (models.py)
    ├─ Prediction: Historial de predicciones
    ├─ CoffeeProfile: Perfiles de café guardados
    └─ ClusterInfo: Información de clusters

[ ] Paso 2: Crear servicio ML (ml_service.py)
    ├─ load_models(): Cargar .pkl en memoria
    ├─ preprocess_input(): Codificar y escalar
    ├─ predict(): Asignar cluster y retornar notas
    └─ get_cluster_info(): Obtener info del cluster

[ ] Paso 3: Crear serializadores (serializers.py)
    ├─ PredictionInputSerializer: Validar entrada
    └─ PredictionOutputSerializer: Formatear respuesta

[ ] Paso 4: Crear vistas API (views.py)
    ├─ POST /api/predict/: Predicción de notas
    ├─ GET /api/clusters/: Info de clusters
    └─ GET /api/history/: Historial

[ ] Paso 5: Configurar URLs
```

### **FASE 3: Testing**
```
[ ] Probar con Thunder Client/Postman
[ ] Validar predicciones
[ ] Verificar persistencia en BD
```

---

## 🔍 EJEMPLO DE USO (Django API)

**Request:**
```json
POST /api/predict/
{
  "country_of_origin": "Ethiopia",
  "processing_method": "Washed / Wet",
  "variety": "Bourbon",
  "altitude_mean": 2000.0,
  "moisture": 0.12,
  "category_one_defects": 0,
  "category_two_defects": 0
}
```

**Response:**
```json
{
  "success": true,
  "cluster_asignado": 0,
  "confianza": 92.5,
  "notas_predichas": {
    "Aroma": 7.85,
    "Flavor": 7.92,
    "Aftertaste": 7.68,
    "Acidity": 7.75,
    "Body": 7.60,
    "Balance": 7.80,
    "Total.Cup.Points": 84.50
  },
  "cluster_info": {
    "nombre": "Café de Alta Calidad",
    "caracteristicas": "Cafés procesados lavados, alta altitud"
  }
}
```

---

## 📚 CONCEPTOS CLAVE

### **¿Por qué K-means (no supervisado)?**
```
✓ No necesitamos etiquetas manuales
✓ Descubre patrones naturales en los datos
✓ Agrupa cafés con características similares
✓ Las notas se predicen por el promedio del cluster
```

### **¿Por qué SMOTE?**
```
✓ Dataset desbalanceado afecta el clustering
✓ SMOTE genera datos sintéticos realistas
✓ Mejora la representación de Robusta
✓ Clusters más equilibrados y confiables
```

### **¿Cómo funciona la predicción?**
```
1. Nuevo café → Codificar y escalar
2. Calcular distancia a cada centroide
3. Asignar al cluster más cercano
4. Retornar notas promedio de ese cluster
```

---

## 🚀 PRÓXIMOS PASOS

### **AHORA MISMO:**
1. Abrir el notebook `PrediccionNotasCafe_KMeans.ipynb`
2. Ejecutar TODAS las celdas en orden
3. Ejecutar `%run export_model.py` al final
4. Verificar que se crearon los archivos en `ml_models/`

### **LUEGO:**
5. Implementar `models.py` (Base de datos Django)
6. Implementar `ml_service.py` (Lógica de predicción)
7. Implementar API REST
8. Probar con Thunder Client

---

## 💡 NOTAS IMPORTANTES

- El modelo NO se reentrena en producción (se carga de .pkl)
- Los encoders deben manejar valores nuevos (usar "Unknown")
- Cache del modelo en memoria para velocidad
- Guardar historial de predicciones en BD
- Validar entrada antes de predecir

---

**Autor:** GitHub Copilot  
**Fecha:** 2026-01-04  
**Versión:** 1.0

