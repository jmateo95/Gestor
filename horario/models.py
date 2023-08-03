import uuid
from django.db import models
from datetime import datetime, timedelta

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
        return f"{self.posicion}"
    
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
    
    
class Carreras(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=200,  blank=True,default="")
    
    class Meta:
        db_table = 'horario_carreras'

    def __str__(self):
        return f"{self.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()
    

class Materias(models.Model):
    codigo      = models.CharField(max_length=25,   blank=True,default="")
    nombre      = models.CharField(max_length=200,  blank=True,default="")
    asignados   = models.IntegerField()
    carrera     = models.ForeignKey(Carreras, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'horario_materias'

    def __str__(self):
        return f"{self.nombre}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()
    
    
class Asignaciones(models.Model):
    codigo_asignacion   = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    periodo = models.ForeignKey(Periodos,       on_delete=models.CASCADE, null=True)
    profesor = models.ForeignKey(Profesores,    on_delete=models.CASCADE, null=True)
    materia = models.ForeignKey(Materias,       on_delete=models.CASCADE, null=True)
    salon = models.ForeignKey(Salones,          on_delete=models.CASCADE, null=True)
    
    class Meta:
        db_table = 'horario_asignaciones'

    def __str__(self):
        return f"{self.codigo_asignacion}"
    
    @classmethod
    def eliminar(cls):
        cls.objects.all().delete()
