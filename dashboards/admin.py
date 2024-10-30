from django.contrib import admin
from .models import LogExport  # Importe seu modelo aqui

class LogExportAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'resultado', 'date_start', 'date_end', 'created_at')  # Campos que deseja exibir na lista
    list_filter = ('user', 'client', 'resultado')  # Campos para filtrar a lista
    search_fields = ('user__full_name', 'client__fantasy_name', 'log')  # Campos para pesquisa

# Registre o modelo no admin
admin.site.register(LogExport, LogExportAdmin)
