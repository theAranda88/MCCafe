"""
SCRIPT DE EXPORTACIÓN DE MODELOS Y TRANSFORMADORES
===================================================
Ejecutar este script DESPUÉS de entrenar el modelo K-means en el notebook.

Este script guarda todos los componentes necesarios para usar el modelo en Django:
1. Modelo K-means entrenado
2. Scalers (estandarizadores)
3. Encoders (codificadores categóricos)
4. Metadata del modelo
5. DataFrame con clusters

Autor: Proyecto Café ML
Fecha: 2026-01-04
"""

import joblib
import json
from pathlib import Path
import os

# Detectar si estamos ejecutando desde notebooks/ o desde raíz
current_dir = Path.cwd()
if current_dir.name == "notebooks":
    # Estamos en notebooks/, subir un nivel
    PROJECT_ROOT = current_dir.parent
else:
    # Estamos en la raíz del proyecto
    PROJECT_ROOT = current_dir

# Directorio de destino
ML_MODELS_DIR = PROJECT_ROOT / "ml_models"
ML_MODELS_DIR.mkdir(exist_ok=True)

print(f"📂 Directorio del proyecto: {PROJECT_ROOT}")
print(f"📂 Directorio de modelos: {ML_MODELS_DIR}")

print("="*70)
print("EXPORTACIÓN DE MODELOS Y TRANSFORMADORES PARA DJANGO")
print("="*70)

# Verificar que tenemos todos los componentes necesarios
required_components = {
    'kmeans_results': kmeans_results,
    'best_kmeans': kmeans_results['best'] if kmeans_results else None,
    'scaler_input': scaler_input,
    'scaler_output': scaler_output,
    'encoders': encoders,
    'df_clustered': df_clustered,
    'input_feature_names': input_feature_names,
    'available_output': available_output,
    'available_categorical': available_categorical,
    'available_numeric_input': available_numeric_input
}

# Verificar componentes
missing = [k for k, v in required_components.items() if v is None]
if missing:
    print(f"\n❌ Faltan componentes: {missing}")
    print("   Ejecuta todas las celdas del notebook antes de exportar")
else:
    print("\n✅ Todos los componentes disponibles")
    
    # 1. GUARDAR MODELO K-MEANS
    print("\n📦 Guardando modelo K-means...")
    best_kmeans = kmeans_results['best']
    kmeans_data = {
        'labels': best_kmeans.labels,
        'centroids': best_kmeans.centroids,
        'inertia': best_kmeans.inertia,
        'silhouette': best_kmeans.silhouette,
        'k': best_kmeans.k
    }
    joblib.dump(kmeans_data, str(ML_MODELS_DIR / "modelo_kmeans.pkl"))
    print(f"   ✓ Modelo guardado con k={best_kmeans.k} clusters")
    
    # 2. GUARDAR SCALERS
    print("\n📦 Guardando escaladores...")
    joblib.dump(scaler_input, str(ML_MODELS_DIR / "scaler_input.pkl"))
    joblib.dump(scaler_output, str(ML_MODELS_DIR / "scaler_output.pkl"))
    print("   ✓ Scalers guardados")
    
    # 3. GUARDAR ENCODERS
    print("\n📦 Guardando encoders...")
    joblib.dump(encoders, str(ML_MODELS_DIR / "encoders.pkl"))
    print(f"   ✓ {len(encoders)} encoders guardados")
    
    # 4. GUARDAR DATAFRAME CON CLUSTERS
    print("\n📦 Guardando DataFrame con clusters...")
    joblib.dump(df_clustered, str(ML_MODELS_DIR / "df_clustered.pkl"))
    print(f"   ✓ DataFrame guardado ({len(df_clustered)} filas)")
    
    # 5. GUARDAR METADATA
    print("\n📦 Guardando metadata...")
    
    # Calcular estadísticas por cluster
    cluster_stats = {}
    for cluster_id in range(best_kmeans.k):
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
        
        # Características de entrada más comunes
        categorical_modes = {}
        for col in available_categorical:
            if col in cluster_data.columns:
                mode_val = cluster_data[col].mode()[0] if len(cluster_data[col].mode()) > 0 else 'Unknown'
                categorical_modes[col] = mode_val
        
        # Promedios de entrada numérica
        numeric_means = {}
        for col in available_numeric_input:
            if col in cluster_data.columns:
                numeric_means[col] = float(cluster_data[col].mean())
        
        # Promedios de notas sensoriales
        output_means = {}
        for col in available_output:
            if col in cluster_data.columns:
                output_means[col] = float(cluster_data[col].mean())
        
        cluster_stats[str(cluster_id)] = {
            'count': int(len(cluster_data)),
            'categorical_modes': categorical_modes,
            'numeric_means': numeric_means,
            'output_means': output_means,
            'centroid': best_kmeans.centroids[cluster_id].tolist()
        }
    
    metadata = {
        'model_type': 'kmeans',
        'n_clusters': int(best_kmeans.k),
        'silhouette_score': float(best_kmeans.silhouette),
        'inertia': float(best_kmeans.inertia),
        'input_features': {
            'categorical': available_categorical,
            'numeric': available_numeric_input,
            'all': input_feature_names
        },
        'output_features': available_output,
        'cluster_stats': cluster_stats,
        'training_samples': int(len(df_clustered)),
        'version': '1.0',
        'created_at': pd.Timestamp.now().isoformat()
    }
    
    with open(str(ML_MODELS_DIR / "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("   ✓ Metadata guardado")
    
    # RESUMEN
    print("\n" + "="*70)
    print("✅ EXPORTACIÓN COMPLETADA")
    print("="*70)
    print(f"\nArchivos generados en {ML_MODELS_DIR.absolute()}/:")
    print("   1. modelo_kmeans.pkl      - Modelo K-means entrenado")
    print("   2. scaler_input.pkl        - Escalador de entrada")
    print("   3. scaler_output.pkl       - Escalador de salida")
    print("   4. encoders.pkl            - Encoders categóricos")
    print("   5. df_clustered.pkl        - DataFrame con clusters")
    print("   6. metadata.json           - Metadatos del modelo")
    
    print(f"\n📊 Información del modelo:")
    print(f"   • Número de clusters: {best_kmeans.k}")
    print(f"   • Silhouette score: {best_kmeans.silhouette:.3f}")
    print(f"   • Features de entrada: {len(input_feature_names)}")
    print(f"   • Features de salida: {len(available_output)}")
    print(f"   • Muestras de entrenamiento: {len(df_clustered):,}")
    
    print("\n🚀 Listo para integrar en Django!")
    print("   Siguiente paso: Implementar ml_service.py")

