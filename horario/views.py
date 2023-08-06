from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Variables, Periodos, Salones, Profesores, Carreras, Materias, Asignaciones
from django.shortcuts import get_object_or_404
from .forms import VariablesForm
from django.contrib import messages
from django.db.models import Sum
import pandas as pd
import environ
import random
from django.db.models import F
env = environ.Env()

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
        return reverse('horario:salones-create')


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
        return reverse('horario:salones-create')
    

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
        return reverse('horario:profesores-create')
    
    
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
        return reverse('horario:carreras-create')
    
    
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
        return reverse('horario:materias-create')
    

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
        return reverse('horario:asignaciones-create')


class AsignacionesCreateView(TemplateView):
    template_name = 'asignaciones_form.html'
    
    def post(self, request, *args, **kwargs):
        Asignaciones.eliminar()
        corridas=env.int('CORRIDAS', default=1)

        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for version in range(1, corridas + 1):
                for index, row in df.iterrows():
                    codigo_profesor = row['profesor']
                    codigo_materia  = row['materia']
                    
                    try:
                        profesor =  get_object_or_404(Profesores,   codigo=codigo_profesor)
                        materia  =  get_object_or_404(Materias,     codigo=codigo_materia)
                        Asignaciones.objects.create(profesor=profesor, materia=materia, manual=True, peso=1, version=version)
                    except Carreras.DoesNotExist:
                        print(f"Asignación con el numero {index} no encontrada.")
                        continue
            
            return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las asignaciones!')
        return reverse('horario:generar')
    

class PreviewView(TemplateView):
    template_name = 'preview.html'
    
    def get_context_data(self, **kwargs):
        context     = super().get_context_data(**kwargs)
        periodos    = Periodos.objects.all().order_by('posicion')
        salones     = Salones.objects.all().order_by('nombre')
        version     = self.kwargs.get('version')
        pagina      = 1 if version is None else int(version)
        
        #Si no trae asignacion que busque la mejor
        if(version is None):
            asignacion_optima = Asignaciones.objects.values('version').annotate(total_peso=Sum('peso')).order_by('-total_peso').first()
            version= asignacion_optima['version']
        
        asignaciones_dict = {}
        for periodo in periodos:
            asignaciones_dict[periodo] = {}
            for salon in salones:
                asignaciones = periodo.asignaciones_set.filter(salon=salon, version=version)
                if asignaciones.exists():
                    asignacion  = asignaciones.first()
                    profesor    = asignacion.profesor.nombre if asignacion.profesor else "Por Asignar"
                    materia     = asignacion.materia.nombre
                    carrera     = asignacion.materia.carrera.nombre
                    asignados   = asignacion.materia.asignados
                    style       = 'bg-warning' if asignacion.alerta else 'bg-primary'
                    asignaciones_dict[periodo][salon] = {
                        'profesor'  : profesor,
                        'materia'   : materia,
                        'carrera'   : carrera,
                        'asignados' : asignados,
                        'style'     : style
                    }
                else:
                    asignaciones_dict[periodo][salon] = None
                    
        context['periodos'] = periodos
        context['salones'] = salones
        context['prev_version'] = pagina-1
        context['next_version'] = pagina+1
        context['asignaciones_dict'] = asignaciones_dict

        return context


class GenerarView(TemplateView):
    template_name = 'generar.html'
    
    #Peticion GET
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})
    
    #Peticion POST
    def post(self, request, *args, **kwargs):
        if 'CUPO' in request.POST['valor']:
            return self.generar_cupo(request)
        elif 'SALON' in request.POST['valor']:
            return self.generar_salon(request)
        elif 'PROFESOR' in request.POST['valor']:
            return self.generar_profesor(request)
        elif 'MEJOR' in request.POST['valor']:
            return self.generar_mejor(request)

    #Generar los cupos
    def generar_cupo(self, request):
        # Obtener todas las asignaciones con manual=False y eliminarlas
        Asignaciones.objects.filter(manual=False).delete()
        
        # Obtener todas las materias que aún no tienen una asignación
        materias_sin_asignacion = Materias.objects.filter(asignaciones__isnull=True)
        corridas=env.int('CORRIDAS', default=1)
        for version in range(1, corridas + 1):
            for materia in materias_sin_asignacion:
                Asignaciones.objects.create(manual=False, materia=materia, periodo=None, profesor=None, salon=None, peso=0, version=version)
        messages.success(self.request, '¡Se crearon los cupos con exito!')
        return redirect('horario:generar')
    
    #Generar la reparticion por salones
    def generar_salon(self, request):
        return redirect('horario:generar')
    
    #Generar la reparticion por horario de contratacion
    def generar_profesor(self, request):
        corridas=env.int('CORRIDAS', default=1)
        # Hacerlo por cada version
        for version in range(1, corridas + 1):
            # Asignar un maestro y horario 
            asignaciones = Asignaciones.objects.filter(version=version)
            asignaciones = asignaciones.annotate(random_order=F('id') % random.randint(1, 10000))
            asignaciones = asignaciones.order_by('random_order')
            for asignacion in asignaciones:
                if asignacion.profesor:
                    periodos_disponibles = asignacion.profesor.periodos_disponibles(version=version)
                    if periodos_disponibles:
                        periodo_asignado = random.choice(periodos_disponibles)
                        asignacion.periodo = periodo_asignado
                        asignacion.peso += 1
                        asignacion.save()
                else:
                    profesores_disponibles = list(Profesores.objects.filter(habilitado=True))
                    random.shuffle(profesores_disponibles)
                    for profesor in profesores_disponibles:
                        periodos_disponibles = profesor.periodos_disponibles(version=version)
                        
                        if periodos_disponibles:
                            periodo_asignado = random.choice(periodos_disponibles)
                            asignacion.profesor = profesor
                            asignacion.periodo = periodo_asignado
                            asignacion.peso += 2
                            asignacion.save()
                            break
                        
            # Asignar salon
            for asignacion in asignaciones:
                if asignacion.salon is None:
                    salones_disponibles = Salones.objects.filter(capacidad__gte=asignacion.materia.asignados).order_by('capacidad')
                    for salon in salones_disponibles:
                        if(Asignaciones.check_salon(periodo=asignacion.periodo, salon=salon, version=version)):
                            asignacion.salon=salon
                            asignacion.peso += 1
                            asignacion.save()
                            break
                    if(asignacion.salon is None):
                        salones_disponibles = Salones.objects.filter(capacidad__lte=asignacion.materia.asignados).order_by('-capacidad')
                        for salon in salones_disponibles:
                            if(Asignaciones.check_salon(periodo=asignacion.periodo, salon=salon, version=version)):
                                asignacion.salon=salon
                                asignacion.alerta=True
                                asignacion.peso += 1
                                asignacion.save()
                                break
                            
        return redirect('horario:preview')
    
    
    #Generar la reparticion de la mejor forma
    def generar_mejor(self, request):
        return redirect('horario:preview')