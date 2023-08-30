from django.views.generic import TemplateView, CreateView, UpdateView, View
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Variables, Periodos, Salones, Profesores, Carreras, Materias, Asignaciones,  Areas, Habilitaciones
from django.shortcuts import get_object_or_404
from .forms import VariablesForm
from django.contrib import messages
from django.db.models import Sum, Avg, F
import pandas as pd
import environ
import random
from django.db.models import F
from django.db.models.functions import Round
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
                color  = row['color']
                Carreras.objects.create(codigo=codigo, nombre=nombre, color=color)
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
                semestre        = row['semestre']
                asignados       = row['asignados']
                no_periodos     = row['no_periodos']
                codigo_carrera  = row['carrera']
                codigo_area     = row['area']
                
                try:
                    carrera =  get_object_or_404(Carreras, codigo=codigo_carrera)
                    area =  get_object_or_404(Areas, codigo=codigo_area)
                    Materias.objects.create(codigo=codigo, nombre=nombre, semestre=semestre, asignados=asignados, no_periodos=no_periodos, carrera=carrera, area=area)
                except Carreras.DoesNotExist:
                    print(f"Carrera con codigo {codigo_carrera} o area {codigo_area} no encontrada. Saltando a la siguiente materia.")
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
                        for no_periodo in range(materia.no_periodos): 
                            Asignaciones.objects.create(profesor=profesor, materia=materia, manual=True, peso=0, version=version, no_periodo=no_periodo)
                    except Carreras.DoesNotExist:
                        print(f"Asignación con el numero {index} no encontrada.")
                        continue
            
            return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las asignaciones!')
        return reverse('horario:habilitaciones-create')
    

class HabilitacionesCreateView(TemplateView):
    template_name = 'habilitaciones_form.html'
    
    def post(self, request, *args, **kwargs):
        Habilitaciones.eliminar()
        file = request.FILES.get('file')
        if file:
            df = pd.read_excel(file)
            for index, row in df.iterrows():
                codigo_profesor = row['profesor']
                codigo_carrera  = row['carrera']
                codigo_area     = row['area']
                
                try:
                    profesor =  get_object_or_404(Profesores,   codigo=codigo_profesor)
                    carrera  =  get_object_or_404(Carreras,     codigo=codigo_carrera)
                    area     =  get_object_or_404(Areas,        codigo=codigo_area)
                    Habilitaciones.objects.create(profesor=profesor, carrera=carrera, area=area)
                except Carreras.DoesNotExist:
                    print(f"Profesor con codigo {codigo_profesor}, o carrera con codigo {codigo_carrera} o area {codigo_area} no encontrada. Saltando a la siguiente habilitacion.")
                    continue

            return redirect(self.get_success_url())
    
    def get_success_url(self):
        messages.success(self.request, '¡Se Crearon las habilitaciones!')
        return reverse('horario:generar')
    

class PreviewView(TemplateView):
    template_name = 'preview.html'
    
    def get_context_data(self, **kwargs):
        context     = super().get_context_data(**kwargs)
        periodos    = Periodos.objects.all().order_by('posicion')
        salones     = Salones.objects.all().order_by('nombre')
        version     = self.kwargs.get('version')
        flag        = self.kwargs.get('version')
        pagina      = 1 if version is None else int(version)
        
        #Si no trae asignacion que busque la mejor
        if(version is None):
            asignacion_optima = Asignaciones.objects.values('version').annotate(total_peso=Sum('peso')).order_by('-total_peso').first()
            version= asignacion_optima['version']

        #Efectividad
        queryset = Asignaciones.objects.filter(version=version)
        result = queryset.aggregate(avg_peso=Round(Avg('peso'), 2))
        efectividad = 0 if not result['avg_peso'] else round((result['avg_peso'] / 13) * 100, 2)
        
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
                    semestre    = asignacion.materia.semestre
                    asignados   = asignacion.materia.asignados
                    error       = asignacion.error
                    style       = '#ffc107!important' if asignacion.alerta else ('#'+asignacion.materia.carrera.color+'!important')
                    asignaciones_dict[periodo][salon] = {
                        'profesor'  : profesor,
                        'materia'   : materia,
                        'carrera'   : carrera,
                        'semestre'  : semestre,
                        'asignados' : asignados,
                        'error'     : error,
                        'style'     : style
                    }
                else:
                    asignaciones_dict[periodo][salon] = None
        
        #Con Problemas
        asignacion_problemas = Asignaciones.objects.filter(version=version, periodo=None) | Asignaciones.objects.filter(version=version, salon=None)
    
        context['periodos'] = periodos
        context['salones'] = salones
        context['prev_version'] = pagina-1
        context['next_version'] = pagina + 1 if flag is not None else 1
        context['asignaciones_dict'] = asignaciones_dict
        context['asignacion_problemas'] = asignacion_problemas
        context['version'] = version
        context['efectividad'] = efectividad

        return context


class GenerarView(TemplateView):
    template_name = 'generar.html'
    
    #Peticion GET
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={})
    
    #Peticion POST
    def post(self, request, *args, **kwargs):
        if 'SALON' in request.POST['valor']:
            return self.generar_salon(request)
        elif 'PROFESOR' in request.POST['valor']:
            return self.generar_profesor(request)
        elif 'MEJOR' in request.POST['valor']:
            return self.generar_mejor(request)
    
    #Generar la reparticion por salones
    def generar_salon(self, request):
        #Inicializacion
        corridas=env.int('CORRIDAS', default=1)
        limpiar_horarios()
        generar_cupo()
        
        # Hacerlo por cada version
        for version in range(1, corridas + 1):

            #Obtener las materias
            materias = list(Materias.objects.all())
            random.shuffle(materias)
                        
            # Asignar salon
            for materia in materias:
                
                #Obtengo la asignacion
                asignaciones = Asignaciones.objects.filter(version=version, materia=materia).order_by('no_periodo')

                #Si no tiene salon buscamos salon
                if asignaciones[0].salon is None:
                    salones_disponibles = Salones.salones_disponibles_mayor(version=version, capacidad=materia.asignados, no_periodos=materia.no_periodos)
                    #Escoje un salon que cubra la capacidad
                    if salones_disponibles:
                        asignaciones.update(salon=salones_disponibles[0])
                    
                    #Si no hay salones que  cubran la demanda
                    if(asignaciones[0].salon is None):
                        salones_disponibles = Salones.salones_disponibles_menor(version=version, capacidad=materia.asignados, no_periodos=materia.no_periodos)
                        if salones_disponibles:
                            asignaciones.update(salon=salones_disponibles[0])
            
            # Asignar un maestro y horario 
            for materia in materias:
                
                #Obtengo la asignacion
                asignaciones = Asignaciones.objects.filter(version=version, materia=materia).order_by('no_periodo')

                #Si ya teiene un profesor se le busca periodo
                if (asignaciones[0].profesor):
                    #Lista de periodos  habiles para usar
                    periodos_habiles = asignaciones[0].profesor.periodos_disponibles(version=version)

                    #tuplas de periodos disponibles
                    periodos_disponibles = get_periodos_disponibles(periodos_habiles, materia.no_periodos, version=version)
                    
                    for periodos in periodos_disponibles:

                        if(Asignaciones.check_salon(periodos=periodos, salon=asignaciones[0].salon, version=version) and Asignaciones.check_semestre(periodos=periodos, materia=materia, version=version) ):

                            for index, asignacion in enumerate(asignaciones):
                                asignacion.periodo=periodos[index]
                                asignacion.save()
                            break
                            
                        
                #Si no tiene un profesor se busca un profesor y horario
                else:
                    profesores_disponibles = Profesores.profesores_disponibles(carrera=materia.carrera, area=materia.area)
                    random.shuffle(profesores_disponibles)
                    for profesor in profesores_disponibles:
                        periodos_habiles = profesor.periodos_disponibles(version=version)

                        #tuplas de periodos disponibles
                        periodos_disponibles = get_periodos_disponibles(periodos_habiles, materia.no_periodos, version=version)

                        for periodos in periodos_disponibles:
                            if(Asignaciones.check_salon(periodos=periodos, salon=asignaciones[0].salon, version=version) and Asignaciones.check_semestre(periodos=periodos, materia=materia, version=version) ):
                                for index, asignacion in enumerate(asignaciones):
                                    asignacion.profesor = profesor
                                    asignacion.periodo=periodos[index]
                                    asignacion.save()
                                break
                        if(asignaciones[0].periodo):
                            break
                    
                    #Si ningun profesor cumplio el requisito solo se le asigna un horario.
                    if(asignaciones[0].periodo is None and asignaciones[0].salon):
                        periodos_habiles = asignaciones[0].salon.periodos_disponibles(version=version)

                        #tuplas de periodos disponibles
                        periodos_disponibles = get_periodos_disponibles(periodos_habiles, materia.no_periodos, version=version)

                        if periodos_disponibles:
                            periodos_asignados = random.choice(periodos_disponibles)
                            for index, asignacion in enumerate(asignaciones):
                                asignacion.periodo=periodos_asignados[index]
                                asignacion.save()
            
        puntuar_horario()
        return redirect('horario:preview')
    
    
    #Generar la reparticion por horario de contratacion
    def generar_profesor(self, request):
        #Inicializacion
        corridas=env.int('CORRIDAS', default=1)
        limpiar_horarios()
        generar_cupo()
        
        # Hacerlo por cada version
        for version in range(1, corridas + 1):
            asignaciones = Asignaciones.objects.filter(version=version)
            asignaciones = asignaciones.annotate(random_order=F('id') % random.randint(1, 10000))
            asignaciones = asignaciones.order_by('random_order')
            
            # Asignar horario
            for asignacion in asignaciones:
                # Si ya tiene profesor buscamos horario
                if asignacion.profesor:
                    periodos_disponibles = asignacion.profesor.periodos_disponibles(version=version)
                    #Periodo disponible
                    if periodos_disponibles:
                        periodo_asignado = random.choice(periodos_disponibles)
                        asignacion.periodo = periodo_asignado
                        asignacion.save()
                
                # Si no tiene profesor buscamos horario y profesor
                else:
                    profesores_disponibles = list(Profesores.objects.filter(habilitado=True))
                    random.shuffle(profesores_disponibles)
                    for profesor in profesores_disponibles:
                        periodos_disponibles = profesor.periodos_disponibles(version=version)
                        #Profesor y periodo disponible
                        if periodos_disponibles:
                            periodo_asignado = random.choice(periodos_disponibles)
                            asignacion.profesor = profesor
                            asignacion.periodo = periodo_asignado
                            asignacion.save()
                            break
                        
            # Asignar salon
            for asignacion in asignaciones:
                #Si no tiene salon buscamos salon
                if asignacion.salon is None:
                    salones_disponibles = Salones.objects.filter(capacidad__gte=asignacion.materia.asignados).order_by('capacidad')
                    for salon in salones_disponibles:
                        #Escoje un salon que cubra la capacidad
                        if(Asignaciones.check_salon(periodo=asignacion.periodo, salon=salon, version=version)):
                            asignacion.salon=salon
                            asignacion.save()
                            break
                    
                    #Si no hay salones que  cubran la demanda
                    if(asignacion.salon is None):
                        salones_disponibles = Salones.objects.filter(capacidad__lte=asignacion.materia.asignados).order_by('-capacidad')
                        for salon in salones_disponibles:
                            if(Asignaciones.check_salon(periodo=asignacion.periodo, salon=salon, version=version)):
                                asignacion.salon=salon
                                asignacion.save()
                                break
                                        
                #Si no se encuentra Profesor se busca un periodo disponible
                if asignacion.profesor is None and asignacion.salon:
                    periodos_disponibles = asignacion.salon.periodos_disponibles(version=version)
                    if(periodos_disponibles):
                        periodo_asignado = random.choice(periodos_disponibles)
                        asignacion.periodo = periodo_asignado
                        asignacion.save()
                        
        puntuar_horario()         
        return redirect('horario:preview')
    
    #Generar la reparticion de la mejor forma
    def generar_mejor(self, request):
        return redirect('horario:preview')


# Limpiar los horarios
def limpiar_horarios():
    Asignaciones.objects.filter(manual=False).delete()
    # Luego, actualiza los registros con manual=True
    Asignaciones.objects.filter(manual=True).update(periodo=None, salon=None, peso=0, alerta=False, error="")


#Generar los cupos
def generar_cupo():
    # Obtener todas las asignaciones con manual=False y eliminarlas
    Asignaciones.objects.filter(manual=False).delete()
    
    # Obtener todas las materias que aún no tienen una asignación
    materias_sin_asignacion = Materias.objects.filter(asignaciones__isnull=True)
    corridas=env.int('CORRIDAS', default=1)
    for version in range(1, corridas + 1):
        for materia in materias_sin_asignacion:
            for no_periodo in range(materia.no_periodos):
                Asignaciones.objects.create(manual=False, materia=materia, periodo=None, profesor=None, salon=None, peso=0, version=version, alerta=False, no_periodo=no_periodo)
            

# Puntuar los horarios    
def puntuar_horario():
    asignaciones = Asignaciones.objects.all()
    # Esquema de calificacion
    for asignacion in asignaciones:
        if asignacion.materia:
            asignacion.peso += 1
        if asignacion.profesor:
            asignacion.peso += 1
        if asignacion.periodo:
            asignacion.peso += 1
        if asignacion.salon:
            asignacion.peso += 1
            if asignacion.periodo:
                asignacion.peso += 2
                if asignacion.profesor:
                    asignacion.peso += 3
                    if asignacion.salon.capacidad >= asignacion.materia.asignados:
                        asignacion.peso += 4
                    

        if None in (asignacion.materia, asignacion.profesor, asignacion.periodo, asignacion.salon):
            asignacion.alerta = True
            #Añadir el error
            error_messages = {
                'materia': "No se encontró una materia que satisfaga las necesidades.",
                'profesor': "No se encontró un profesor disponible.",
                'periodo': "No se encontró un periodo válido.",
                'salon': "No se encontró un salón disponible."
            }

            asignacion.alerta = any(value is None for value in [asignacion.materia, asignacion.profesor, asignacion.periodo, asignacion.salon])
            asignacion.error = '\n'.join(message for field, message in error_messages.items() if getattr(asignacion, field) is None)

        if asignacion.salon:
            if asignacion.salon.capacidad < asignacion.materia.asignados:
                asignacion.alerta = True
                asignacion.peso -= 1
                #Añadir el error
                asignacion.error+= "La capacidad del salón puede no ser la desada.\n"
        asignacion.save()


def get_periodos_disponibles(periodos_habiles, no_periodos, version):
    randoms=env.int('RANDOMS', default=5)
    periodos_disponibles=[]
    for i in range(len(periodos_habiles) -(no_periodos - 1)):
        secuencia = periodos_habiles[i:i+no_periodos]
        
        # Verificar si la secuencia tiene 'no_periodos' elementos consecutivos
        if all(secuencia[j].hora_fin == secuencia[j+1].hora_inicio for j in range(no_periodos - 1)):
            periodos_disponibles.append(secuencia)
    if version>=randoms:
        random.shuffle(periodos_disponibles)
    return periodos_disponibles