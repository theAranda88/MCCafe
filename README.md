#  Sistema de Predicción de Notas Sensoriales de Café

API REST desarrollada con Django que predice la calidad sensorial del café basándose en características de procesamiento y origen utilizando Machine Learning (K-means clustering).

---

##  INICIO RÁPIDO

### **Prerrequisitos**
- Python 3.14+
- PostgreSQL 17 (opcional, puede usar SQLite para desarrollo)
- Git

### **1. Clonar el repositorio**
```bash
git clone <url-del-repo>
cd proyecto_cafe_ml
```

### **2. Crear y activar entorno virtual**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
.\venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

### **3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar variables de entorno**
Copia el archivo `.env.example` a `.env` y edita las credenciales:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edita `.env` con tus datos:
```env
# Base de Datos PostgreSQL
DB_NAME=cafe_ml_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui
DB_HOST=localhost
DB_PORT=5433

# Django
SECRET_KEY=django-insecure-fsdgc%m30-$1@phljk%6onfl*7bbw0t#3xzmt9$vn)%01jaheu
DEBUG=True
```

### **5. Configurar la base de datos**

#### **Opción A: PostgreSQL (Recomendado para producción)**

1. Asegúrate de que PostgreSQL esté corriendo
2. Crea la base de datos:
```bash
# Windows (ajusta el puerto si es diferente)
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -p 5433 -c "CREATE DATABASE cafe_ml_db;"
```

3. Ejecuta el script de configuración:
```bash
python setup_database.py
```

#### **Opción B: SQLite (Más rápido para desarrollo)**

1. Edita `backend/settings.py` y comenta PostgreSQL, descomenta SQLite
2. Ejecuta:
```bash
python setup_database.py
```

### **6. Iniciar el servidor**
```bash
python manage.py runserver
```

El servidor estará disponible en: **http://127.0.0.1:8000**

---

## 📡 ENDPOINTS DE LA API

### **Predicción de notas sensoriales**
```http
POST http://127.0.0.1:8000/api/predict/
Content-Type: application/json

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

**Respuesta:**
```json
{
  "success": true,
  "cluster_asignado": 2,
  "confianza": 95.3,
  "notas_predichas": {
    "Aroma": 7.85,
    "Flavor": 7.92,
    "Aftertaste": 7.68,
    "Acidity": 7.75,
    "Body": 7.60,
    "Balance": 7.80,
    "Total.Cup.Points": 84.50
  }
}
```

### **Otros endpoints disponibles**
- `GET /api/history/` - Historial de predicciones
- `GET /api/clusters/` - Información de clusters
- `GET /api/model-info/` - Metadata del modelo ML
- `GET /api/profiles/` - Perfiles de café guardados
- `GET /admin/` - Panel de administración Django

---

##  ESTRUCTURA DEL PROYECTO

```
proyecto_cafe_ml/
├── backend/              # Configuración Django
│   ├── settings.py      # Configuración principal
│   └── urls.py          # URLs principales
│
├── cafe_app/            # Aplicación principal
│   ├── models.py        # Modelos de BD
│   ├── views.py         # Endpoints de la API
│   ├── serializers.py   # Validación de datos
│   ├── ml_service.py    # Lógica de Machine Learning
│   └── urls.py          # URLs de la app
│
├── ml_models/           # Modelos ML exportados
│   ├── modelo_kmeans.pkl
│   ├── scaler_input.pkl
│   ├── scaler_output.pkl
│   ├── encoders.pkl
│   └── metadata.json
│
├── notebooks/           # Jupyter Notebooks
│   └── PrediccionNotasCafe_KMeans.ipynb
│
├── data/                # Datasets
│   └── merged_data_cleaned.csv
│
├── setup_database.py    # Script de configuración de BD
├── export_model.py      # Script para exportar modelos ML
├── requirements.txt     # Dependencias Python
├── .env                 # Variables de entorno (NO commitear)
└── README.md           # Este archivo
```

---

##  PRUEBAS

### **Usando Postman/Thunder Client**
Importa la colección: `Coffee_Prediction_API.postman_collection.json`

### **Prueba manual rápida**
```bash
# Verificar que el modelo está cargado
curl http://127.0.0.1:8000/api/model-info/

# Hacer una predicción
curl -X POST http://127.0.0.1:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "country_of_origin": "Brazil",
    "processing_method": "Natural / Dry",
    "variety": "Bourbon",
    "altitude_mean": 1200,
    "moisture": 0.11,
    "category_one_defects": 0,
    "category_two_defects": 2
  }'
```

---

##  GESTORES DE BASE DE DATOS

Para visualizar y gestionar los datos guardados:

### **Para PostgreSQL:**
- **pgAdmin** (viene con PostgreSQL)
- **DBeaver Community** (https://dbeaver.io)
- **DataGrip** (JetBrains)
- **Azure Data Studio** (Microsoft)

**Credenciales de conexión:**
- Host: `localhost`
- Puerto: `5433` (o el configurado en tu .env)
- Database: `cafe_ml_db`
- Usuario: `postgres`
- Contraseña: (la configurada en .env)

### **Para SQLite:**
- **DB Browser for SQLite** (https://sqlitebrowser.org/)
- Abre el archivo `db.sqlite3` en la raíz del proyecto

---

##  CARACTERÍSTICAS PRINCIPALES

-  **API REST** completa con Django REST Framework
-  **Machine Learning** con K-means clustering
-  **Validación de datos** robusta
-  **Historial de predicciones** en base de datos
-  **Gestión de perfiles** de café
-  **Documentación completa** de API
-  **Soporte para PostgreSQL y SQLite**
-  **Panel de administración** Django

---

##  DOCUMENTACIÓN ADICIONAL

Consulta la carpeta `docs/` para:
- `RESUMEN_IMPLEMENTACION.md` - Detalles técnicos del proyecto
- `POSTMAN_TESTS.md` - Guía de pruebas de API
- `CONFIGURACION_POSTGRESQL.md` - Configuración detallada de PostgreSQL

---

##  CONTRIBUCIÓN

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

##  LICENCIA

Este proyecto es parte del Semillero SoftLab - Universidad Autónoma.

---

##  AUTORES

- **Semillero SoftLab** - Universidad Autónoma

---

##  REPORTE DE PROBLEMAS

Si encuentras algún bug o tienes sugerencias, por favor abre un issue en GitHub.

---

##  SOPORTE

Para soporte o preguntas:
- Email: semillerosoftlab@uniautonoma.edu.co
- Issues: GitHub Issues del proyecto
