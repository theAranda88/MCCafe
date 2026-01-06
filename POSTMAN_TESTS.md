# PRUEBAS DE API CON POSTMAN/THUNDER CLIENT
================================================================================

## CONFIGURACIÓN BASE
- **Base URL**: `http://127.0.0.1:8000`
- **Content-Type**: `application/json` (en Headers para POST/PUT/PATCH)

## 📋 ORDEN RECOMENDADO DE PRUEBAS

### 1. GET /api/model-info/ - Verificar que el modelo está cargado
```
GET http://127.0.0.1:8000/api/model-info/
```

**Respuesta esperada:**
```json
{
    "modelo_tipo": "KMeans",
    "n_clusters": 5,
    "fecha_entrenamiento": "...",
    "metricas": {...},
    "features": [...]
}
```

---

### 2. GET /api/clusters/ - Ver información de clusters
```
GET http://127.0.0.1:8000/api/clusters/
```

**Respuesta esperada:**
```json
{
    "clusters": [
        {
            "cluster_id": 0,
            "num_samples": 250,
            "caracteristicas_principales": {...},
            "promedios": {...}
        }
    ],
    "total_clusters": 5
}
```

---

### 3. POST /api/predict/ - REALIZAR PREDICCIÓN ⭐
```
POST http://127.0.0.1:8000/api/predict/
Content-Type: application/json

{
    "country": "Colombia",
    "region": "Huila",
    "variety": "Caturra",
    "processing_method": "Washed / Wet",
    "color": "Green",
    "altitude_mean": 1650,
    "moisture": 0.12
}
```

**Nota**: Valores posibles (según los encoders del modelo):
- **country**: Colombia, Ethiopia, Guatemala, Brazil, Kenya, etc.
- **region**: Huila, Antioquia, Sidama, Yirgacheffe, etc.
- **variety**: Caturra, Bourbon, Typica, Catimor, SL28, etc.
- **processing_method**: "Washed / Wet", "Natural / Dry", "Pulped natural / honey", "Semi-washed / Semi-pulped"
- **color**: "Green", "Bluish-Green", "Blue-Green"
- **altitude_mean**: 800 - 2500 (metros)
- **moisture**: 0.08 - 0.15 (porcentaje en decimal)

**Respuesta esperada:**
```json
{
    "cluster_id": 2,
    "distancia_al_centroide": 1.234,
    "confianza_prediccion": 85.5,
    "notas_sensoriales": {
        "acidez": 7.8,
        "aroma": 7.6,
        "cuerpo": 7.5,
        "sabor": 7.9,
        "balance": 7.7,
        "puntaje_catador": 7.8,
        "puntaje_total": 82.5
    },
    "caracteristicas_cluster": {
        "paises_principales": ["Colombia", "Ethiopia"],
        "variedades_principales": ["Caturra", "Bourbon"],
        "altitud_promedio": 1600
    },
    "mensaje": "Predicción realizada exitosamente"
}
```

---

### 4. GET /api/history/ - Ver historial de predicciones
```
GET http://127.0.0.1:8000/api/history/
```

**Con paginación y filtros:**
```
GET http://127.0.0.1:8000/api/history/?page=1
GET http://127.0.0.1:8000/api/history/?cluster_id=2
GET http://127.0.0.1:8000/api/history/?country=Colombia
GET http://127.0.0.1:8000/api/history/?processing_method=Washed
```

**Respuesta esperada:**
```json
{
    "count": 10,
    "next": "http://127.0.0.1:8000/api/history/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "fecha_prediccion": "2026-01-05T22:58:00Z",
            "parametros_entrada": {
                "country": "Colombia",
                "region": "Huila",
                ...
            },
            "resultado_prediccion": {
                "cluster_id": 2,
                "confianza_prediccion": 85.5
            },
            "notas_sensoriales": {...}
        }
    ]
}
```

---

### 5. GET /api/history/{id}/ - Ver detalle de una predicción
```
GET http://127.0.0.1:8000/api/history/1/
```

---

### 6. GET /api/statistics/ - Estadísticas del sistema
```
GET http://127.0.0.1:8000/api/statistics/
```

**Respuesta esperada:**
```json
{
    "total_predictions": 5,
    "predictions_por_cluster": {
        "0": 2,
        "2": 3
    },
    "predictions_por_pais": {
        "Colombia": 3,
        "Ethiopia": 2
    },
    "predictions_por_metodo": {
        "Washed / Wet": 4,
        "Natural / Dry": 1
    },
    "promedios_notas": {
        "acidez": 7.5,
        "aroma": 7.3,
        ...
    },
    "total_profiles": 0,
    "fecha_primera_prediccion": "2026-01-05T22:58:00Z",
    "fecha_ultima_prediccion": "2026-01-05T23:05:00Z"
}
```

---

### 7. POST /api/profiles/ - Crear perfil de café
```
POST http://127.0.0.1:8000/api/profiles/
Content-Type: application/json

{
    "nombre": "Café Colombia Premium",
    "descripcion": "Café especial de Huila con notas frutales",
    "country": "Colombia",
    "region": "Huila",
    "variety": "Caturra",
    "processing_method": "Washed / Wet",
    "color": "Green",
    "altitude_mean": 1650,
    "moisture": 0.12
}
```

---

### 8. GET /api/profiles/ - Listar todos los perfiles
```
GET http://127.0.0.1:8000/api/profiles/
```

---

### 9. GET /api/profiles/{id}/ - Ver un perfil específico
```
GET http://127.0.0.1:8000/api/profiles/1/
```

---

### 10. POST /api/profiles/{id}/predict/ - Predecir usando perfil guardado
```
POST http://127.0.0.1:8000/api/profiles/1/predict/
```
(Sin body necesario, usa los parámetros del perfil)

---

### 11. PUT /api/profiles/{id}/ - Actualizar perfil completo
```
PUT http://127.0.0.1:8000/api/profiles/1/
Content-Type: application/json

{
    "nombre": "Café Colombia Premium ACTUALIZADO",
    "descripcion": "Descripción actualizada",
    "country": "Colombia",
    "region": "Antioquia",
    "variety": "Bourbon",
    "processing_method": "Natural / Dry",
    "color": "Bluish-Green",
    "altitude_mean": 1800,
    "moisture": 0.11
}
```

---

### 12. PATCH /api/profiles/{id}/ - Actualizar parcialmente
```
PATCH http://127.0.0.1:8000/api/profiles/1/
Content-Type: application/json

{
    "descripcion": "Solo actualizo la descripción",
    "moisture": 0.10
}
```

---

### 13. DELETE /api/profiles/{id}/ - Eliminar perfil
```
DELETE http://127.0.0.1:8000/api/profiles/1/
```

---

## 🧪 CASOS DE PRUEBA ADICIONALES

### Prueba 1: Café de Ethiopia
```json
POST /api/predict/
{
    "country": "Ethiopia",
    "region": "Yirgacheffe",
    "variety": "Ethiopian Heirlooms",
    "processing_method": "Washed / Wet",
    "color": "Bluish-Green",
    "altitude_mean": 1900,
    "moisture": 0.11
}
```

### Prueba 2: Café de Guatemala
```json
POST /api/predict/
{
    "country": "Guatemala",
    "region": "Antigua",
    "variety": "Bourbon",
    "processing_method": "Washed / Wet",
    "color": "Green",
    "altitude_mean": 1600,
    "moisture": 0.12
}
```

### Prueba 3: Café Natural de Brazil
```json
POST /api/predict/
{
    "country": "Brazil",
    "region": "Minas Gerais",
    "variety": "Yellow Bourbon",
    "processing_method": "Natural / Dry",
    "color": "Green",
    "altitude_mean": 1100,
    "moisture": 0.13
}
```

---

## ⚠️ PRUEBAS DE VALIDACIÓN (Deberían fallar)

### Error: Humedad fuera de rango
```json
POST /api/predict/
{
    "country": "Colombia",
    "region": "Huila",
    "variety": "Caturra",
    "processing_method": "Washed / Wet",
    "color": "Green",
    "altitude_mean": 1650,
    "moisture": 0.95
}
```
**Respuesta esperada**: Error 400 - "La humedad debe estar entre 0.0 y 0.20"

### Error: Altitud negativa
```json
POST /api/predict/
{
    "country": "Colombia",
    "altitude_mean": -100,
    ...
}
```
**Respuesta esperada**: Error 400

### Error: Campos faltantes
```json
POST /api/predict/
{
    "country": "Colombia"
}
```
**Respuesta esperada**: Error 400 - "Este campo es requerido"

---

## 📊 IMPORTAR COLECCIÓN EN POSTMAN

Para importar en Postman:
1. Abrir Postman
2. Click en "Import"
3. Seleccionar "Raw text"
4. Copiar y pegar el JSON de abajo
5. Click en "Import"

### Colección JSON para Postman:
```json
{
    "info": {
        "name": "Coffee Prediction API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "1. Get Model Info",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://127.0.0.1:8000/api/model-info/",
                    "protocol": "http",
                    "host": ["127", "0", "0", "1"],
                    "port": "8000",
                    "path": ["api", "model-info", ""]
                }
            }
        },
        {
            "name": "2. Get Clusters Info",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://127.0.0.1:8000/api/clusters/",
                    "protocol": "http",
                    "host": ["127", "0", "0", "1"],
                    "port": "8000",
                    "path": ["api", "clusters", ""]
                }
            }
        },
        {
            "name": "3. Predict - Colombia Caturra",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"country\": \"Colombia\",\n    \"region\": \"Huila\",\n    \"variety\": \"Caturra\",\n    \"processing_method\": \"Washed / Wet\",\n    \"color\": \"Green\",\n    \"altitude_mean\": 1650,\n    \"moisture\": 0.12\n}"
                },
                "url": {
                    "raw": "http://127.0.0.1:8000/api/predict/",
                    "protocol": "http",
                    "host": ["127", "0", "0", "1"],
                    "port": "8000",
                    "path": ["api", "predict", ""]
                }
            }
        },
        {
            "name": "4. Get Prediction History",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://127.0.0.1:8000/api/history/",
                    "protocol": "http",
                    "host": ["127", "0", "0", "1"],
                    "port": "8000",
                    "path": ["api", "history", ""]
                }
            }
        },
        {
            "name": "5. Get Statistics",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "http://127.0.0.1:8000/api/statistics/",
                    "protocol": "http",
                    "host": ["127", "0", "0", "1"],
                    "port": "8000",
                    "path": ["api", "statistics", ""]
                }
            }
        }
    ]
}
```

---

## ✅ CHECKLIST DE PRUEBAS

- [ ] Verificar modelo cargado (/api/model-info/)
- [ ] Ver clusters disponibles (/api/clusters/)
- [ ] Realizar predicción con café colombiano
- [ ] Realizar predicción con café etíope
- [ ] Verificar historial de predicciones
- [ ] Filtrar historial por país
- [ ] Ver detalle de predicción específica
- [ ] Ver estadísticas del sistema
- [ ] Crear perfil de café
- [ ] Listar perfiles creados
- [ ] Predecir usando perfil guardado
- [ ] Actualizar perfil
- [ ] Eliminar perfil
- [ ] Probar validación con datos inválidos

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "Connection refused"
- Verificar que el servidor está corriendo: `python manage.py runserver`
- Verificar que el puerto 8000 no está ocupado

### Error: "ModuleNotFoundError: No module named 'joblib'"
- Activar venv: `.\venv\Scripts\Activate.ps1`
- Instalar dependencias: `pip install joblib scikit-learn numpy pandas`

### Error: "ml_service models not loaded"
- Verificar que existen los archivos .pkl en `ml_models/`
- Revisar logs del servidor para warnings

### Warnings de scikit-learn version
- No afectan funcionalidad
- Para eliminar: re-entrenar modelo con scikit-learn 1.8.0

