from django.contrib import admin
from .models import Prediction, CoffeeProfile, ClusterInfo

admin.site.register(Prediction)
admin.site.register(CoffeeProfile)
admin.site.register(ClusterInfo)

admin.site.site_header = 'Sistema de Predicción de Café - Administración'
admin.site.site_title = 'Admin Café ML'
admin.site.index_title = 'Panel de Control del Sistema de Predicción'
