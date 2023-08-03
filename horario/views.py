from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse
from .models import Variables, Periodos
from .forms import VariablesForm
from django.contrib import messages

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

    
class ProfesoresCreateView(TemplateView):
    template_name = 'profesores_form.html'
    
    
class CarrerasCreateView(TemplateView):
    template_name = 'carreras_form.html'
    

class MateriasCreateView(TemplateView):
    template_name = 'materias_form.html'
    

class AsignacionesCreateView(TemplateView):
    template_name = 'asignaciones_form.html'