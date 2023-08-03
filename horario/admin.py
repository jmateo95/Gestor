from django.contrib import admin
from .models import Variables, Periodos, Profesores, Salones, Carreras, Materias, Asignaciones

@admin.register(Variables)
class VariablesAdmin(admin.ModelAdmin):
    list_display = ['hora_inicio', 'hora_fin', 'duracion']

@admin.register(Periodos)
class PeriodosAdmin(admin.ModelAdmin):
    list_display = ['hora_inicio', 'hora_fin', 'posicion']

@admin.register(Profesores)
class ProfesoresAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'hora_inicio', 'hora_fin', 'habilitado']

@admin.register(Salones)
class SalonesAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'capacidad']

@admin.register(Carreras)
class CarrerasAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre']

@admin.register(Materias)
class MateriasAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'asignados', 'carrera']

@admin.register(Asignaciones)
class AsignacionesAdmin(admin.ModelAdmin):
    list_display = ['codigo_asignacion', 'periodo', 'profesor', 'materia', 'salon']
