from django.urls import path
from .views import VariablesCreateView, VariablesUpdateView, SalonesCreateView, ProfesoresCreateView, CarrerasCreateView, MateriasCreateView, AsignacionesCreateView, PreviewView, GenerarView

app_name = 'horario'

urlpatterns = [
    path('variables/create/',           VariablesCreateView.as_view(),      name='variables-create'),
    path('variables/update/<int:pk>/',  VariablesUpdateView.as_view(),      name='variables-update'),
    path('salones/create/',             SalonesCreateView.as_view(),        name='salones-create'),
    path('profesores/create/',          ProfesoresCreateView.as_view(),     name='profesores-create'),
    path('carreras/create/',            CarrerasCreateView.as_view(),       name='carreras-create'),
    path('materias/create/',            MateriasCreateView.as_view(),       name='materias-create'),
    path('asignaciones/create/',        AsignacionesCreateView.as_view(),   name='asignaciones-create'),
    path('preview/',                    PreviewView.as_view(),              name='preview'),
    path('preview/<int:version>/',      PreviewView.as_view(),              name='preview'),
    path('generar/',                    GenerarView.as_view(),              name='generar'),
]