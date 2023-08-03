from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Variables, Periodos, Salones, Profesores, Carreras, Materias, Asignaciones
from django.shortcuts import get_object_or_404
from .forms import VariablesForm
from django.contrib import messages
import pandas as pd

class Index(TemplateView):
    template_name = 'index.html'


class VariablesCreateView(CreateView):
    model = Variables
    template_name = 'variables_form.html'
    form_class = VariablesForm

    def get(self, request, *args, **kwargs):
        # Verificar si ya existe la instancia, si es así, redirigir a la página de edición
        try:
            variables_instance = Variables.objects.get()
            return redirect('horario:variables-update', pk=variables_instance.pk)
        except Variables.DoesNotExist:
            return super().get(request, *args, **kwargs)
        
    def form_valid(self, form):
        response = super().form_valid(form)
        variables = form.instance
        Periodos.crear_registros_intervalos(hora_inicio=variables.hora_inicio,hora_fin=variables.hora_fin, duracion=variables.duracion)
        return response

    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las variables!')
        return reverse('index')


class VariablesUpdateView(UpdateView):
    model = Variables
    template_name = 'variables_form.html'
    form_class = VariablesForm
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        variables = form.instance
        Periodos.crear_registros_intervalos(hora_inicio=variables.hora_inicio,hora_fin=variables.hora_fin, duracion=variables.duracion)
        return response

    def get_success_url(self):
        messages.success(self.request, '¡Se Actualizaron las variables!')
        return reverse('index')
    

class SalonesCreateView(TemplateView):
    template_name = 'salones_form.html'

    def post(self, request, *args, **kwargs):
        Salones.eliminar()
        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                codigo = row['codigo']
                nombre = row['nombre']
                capacidad = row['capacidad']
                Salones.objects.create(codigo=codigo, nombre=nombre, capacidad=capacidad)
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon los salones')
        return reverse('index')
    
    
class ProfesoresCreateView(TemplateView):
    template_name = 'profesores_form.html'
    
    def post(self, request, *args, **kwargs):
        Profesores.eliminar()
        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                codigo = row['codigo']
                nombre = row['nombre']
                hora_inicio = row['hora_inicio']
                hora_fin = row['hora_fin']
                habilitado = True if row['habilitado'].upper() == 'SI' else False
                Profesores.objects.create(codigo=codigo,nombre=nombre,hora_inicio=hora_inicio,hora_fin=hora_fin,habilitado=habilitado)
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon los profesores!')
        return reverse('index')
    
    
class CarrerasCreateView(TemplateView):
    template_name = 'carreras_form.html'
    
    def post(self, request, *args, **kwargs):
        Carreras.eliminar()

        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                codigo = row['codigo']
                nombre = row['nombre']
                Carreras.objects.create(codigo=codigo, nombre=nombre)
            return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las carreras!s')
        return reverse('index')
    

class MateriasCreateView(TemplateView):
    template_name = 'materias_form.html'
    
    def post(self, request, *args, **kwargs):
        Materias.eliminar()

        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                codigo          = row['codigo']
                nombre          = row['nombre']
                asignados       = row['asignados']
                codigo_carrera  = row['carrera']
                
                try:
                    carrera =  get_object_or_404(Carreras, codigo=codigo_carrera)
                    Materias.objects.create(codigo=codigo, nombre=nombre, asignados=asignados, carrera=carrera)
                except Carreras.DoesNotExist:
                    print(f"Carrera con codigo {codigo_carrera} no encontrada. Saltando a la siguiente carrera.")
                    continue
            return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las materias!')
        return reverse('index')


class AsignacionesCreateView(TemplateView):
    template_name = 'asignaciones_form.html'
    
    def post(self, request, *args, **kwargs):
        Asignaciones.eliminar()

        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                codigo_profesor = row['profesor']
                codigo_materia  = row['materia']
                
                try:
                    profesor =  get_object_or_404(Profesores,   codigo=codigo_profesor)
                    materia  =  get_object_or_404(Materias,     codigo=codigo_materia)
                    Asignaciones.objects.create(profesor=profesor, materia=materia)
                except Carreras.DoesNotExist:
                    print(f"Asignación con el numero {index} no encontrada.")
                    continue
            return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las asignaciones!')
        return reverse('index')
    

class PreviewView(TemplateView):
    template_name = 'preview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        periodos = Periodos.objects.all().order_by('posicion')
        salones = Salones.objects.all().order_by('nombre')

        asignaciones_dict = {}

        for periodo in periodos:
            asignaciones_dict[periodo] = {}
            for salon in salones:
                asignaciones = periodo.asignaciones_set.filter(salon=salon)
                if asignaciones.exists():
                    asignaciones_dict[periodo][salon] = asignaciones.first().materia.nombre
                else:
                    asignaciones_dict[periodo][salon] = ''

        context['periodos'] = periodos
        context['salones'] = salones
        context['asignaciones_dict'] = asignaciones_dict

        return context
