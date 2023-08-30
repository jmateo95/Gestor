import uuid
from django.db import models
from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import Count

class Variables(models.Model):
    hora_inicio  = models.TimeField()
    hora_fin    = models.TimeField()
    duracion    = models.IntegerField()

    class Meta:
        db_table = 'horario_variables'

    def __str__(self):
        return f"{self.duracion}"
    
    
class Periodos(models.Model):
    hora_inicio  = models.TimeField()
    hora_fin    = models.TimeField()
    posicion    = models.IntegerField()

    class Meta:
        db_table = 'horario_periodos'

    def __str__(self):
        return f"{self.hora_inicio} - {self.hora_fin}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()
        
    @classmethod
    def crear_registros_intervalos(cls, hora_inicio, hora_fin, duracion):
        cls.eliminar()

        hora_inicio_dt = datetime.combine(datetime.today(), hora_inicio)
        hora_fin_dt = datetime.combine(datetime.today(), hora_fin)
        duracion_td = timedelta(minutes=duracion)

        current_time = hora_inicio_dt
        counter = 1

        while current_time <= hora_fin_dt:
            periodo = cls(
                hora_inicio=current_time.time(),
                hora_fin=(current_time + duracion_td).time(),
                posicion=counter
            )
            periodo.save()

            current_time += duracion_td
            counter += 1
            
            # if (current_time + duracion_td).time():
            if current_time.time() >= hora_fin:
                break


class Profesores(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=100,  blank=True,default="")
    hora_inicio  = models.TimeField()
    hora_fin    = models.TimeField()
    habilitado  = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'horario_profesores'

    def __str__(self):
        return f"{self.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()

    @classmethod
    def profesores_disponibles(cls, carrera, area):
        area_filter = Q(habilitaciones__area=area)
        if area.codigo != 'BASICA':
            area_filter &= Q(habilitaciones__carrera=carrera)
        
        profesores_habilitados = cls.objects.filter(
            area_filter,
            habilitaciones__profesor__habilitado=True
        ).distinct()
        return list(profesores_habilitados)
        
    def periodos_disponibles(self, version):
        asignaciones = list(Asignaciones.objects.filter(profesor=self, version=version).values_list('periodo__id', flat=True))
        periodos_disponibles = Periodos.objects.filter(hora_inicio__gte=self.hora_inicio, hora_fin__lte=self.hora_fin).exclude(id__in=asignaciones)
        return periodos_disponibles.order_by('hora_inicio')
    
    
class Salones(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=100,  blank=True,default="")
    capacidad   = models.IntegerField()
    
    class Meta:
        db_table = 'horario_salones'

    def __str__(self):
        return f"{self.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()
        
    def periodos_disponibles(self, version):
        asignaciones = list(Asignaciones.objects.filter(salon=self, version=version).values_list('periodo__id', flat=True))
        periodos_disponibles = Periodos.objects.exclude(id__in=asignaciones)
        return periodos_disponibles
    
    @classmethod
    def salones_disponibles_mayor(cls, version, capacidad, no_periodos):
        cantidad_periodos = Periodos.objects.count()
        id_salon_list = [resultado['salon'] for resultado in Asignaciones.objects.filter(version=version).values('salon').annotate(total=Count('id')).filter(total__gt=(cantidad_periodos-no_periodos))]
        salones = Salones.objects.filter(capacidad__gte=capacidad).exclude(id__in=id_salon_list).order_by('capacidad')
        return salones
    
    @classmethod
    def salones_disponibles_menor(cls, version, capacidad, no_periodos):
        cantidad_periodos = Periodos.objects.count()
        id_salon_list = [resultado['salon'] for resultado in Asignaciones.objects.filter(version=version).values('salon').annotate(total=Count('id')).filter(total__gt=(cantidad_periodos-no_periodos))]
        salones = Salones.objects.filter(capacidad__lte=capacidad).exclude(id__in=id_salon_list).order_by('-capacidad')
        return salones
    
    
class Carreras(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=200,  blank=True,default="")
    color       = models.CharField(max_length=20,  blank=True,default="")
    
    class Meta:
        db_table = 'horario_carreras'

    def __str__(self):
        return f"{self.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()


class Areas(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=200,  blank=True,default="")
    
    class Meta:
        db_table = 'horario_areas'

    def __str__(self):
        return f"{self.nombre}"
    

class Materias(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=200,  blank=True,default="")
    semestre    = models.CharField(max_length=5,    blank=True,default="")
    asignados   = models.IntegerField()
    no_periodos = models.IntegerField()
    carrera     = models.ForeignKey(Carreras, on_delete=models.CASCADE)
    area        = models.ForeignKey(Areas,    on_delete=models.CASCADE)

    
    class Meta:
        db_table = 'horario_materias'

    def __str__(self):
        return f"{self.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()
    
    
class Asignaciones(models.Model):
    codigo_asignacion   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    manual              = models.BooleanField(default=False)
    peso                = models.IntegerField()
    no_periodo          = models.IntegerField()
    version             = models.IntegerField()
    alerta              = models.BooleanField(default=False)
    error               = models.CharField(max_length=4000,  blank=True, default="")
    periodo             = models.ForeignKey(Periodos,       on_delete=models.CASCADE, null=True)
    profesor            = models.ForeignKey(Profesores,     on_delete=models.CASCADE, null=True)
    materia             = models.ForeignKey(Materias,       on_delete=models.CASCADE, null=True)
    salon               = models.ForeignKey(Salones,        on_delete=models.CASCADE, null=True)
    
    
    class Meta:
        db_table = 'horario_asignaciones'

    def __str__(self):
        return f"{self.codigo_asignacion}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()

    @classmethod
    def check_salon(cls, periodos, salon, version):
        asignaciones_existen = cls.objects.filter(periodo__in=periodos, salon=salon, version=version).exists()
        return not asignaciones_existen
        
    @classmethod
    def check_semestre(cls, periodos, materia:Materias, version):
        asignaciones_existen = cls.objects.filter(periodo__in=periodos, version=version, materia__semestre=materia.semestre, materia__carrera=materia.carrera).exists()
        return not asignaciones_existen

class Habilitaciones(models.Model):
    profesor            = models.ForeignKey(Profesores,     on_delete=models.CASCADE, null=True)
    carrera             = models.ForeignKey(Carreras,       on_delete=models.CASCADE, null=True)
    area                = models.ForeignKey(Areas,          on_delete=models.CASCADE, null=True)
    
    class Meta:
        db_table = 'horario_habilitaciones'

    def __str__(self):
        return f"{self.profesor.nombre}- {self.carrera.nombre} - {self.area.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()