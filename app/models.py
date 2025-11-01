from django.db import models

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class BalanceGeneral(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    ano = models.IntegerField()
    # Activos
    efectivo = models.DecimalField(max_digits=15, decimal_places=2)
    cartera_creditos_cp = models.DecimalField(max_digits=15, decimal_places=2)
    cartera_creditos_lp = models.DecimalField(max_digits=15, decimal_places=2)
    total_activo_corriente = models.DecimalField(max_digits=15, decimal_places=2)
    total_activo_no_corriente = models.DecimalField(max_digits=15, decimal_places=2)
    total_activo = models.DecimalField(max_digits=15, decimal_places=2)
    # Pasivos y Patrimonio
    pasivo_corriente = models.DecimalField(max_digits=15, decimal_places=2)
    pasivo_no_corriente = models.DecimalField(max_digits=15, decimal_places=2)
    total_pasivo = models.DecimalField(max_digits=15, decimal_places=2)
    total_patrimonio = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('empresa', 'ano')

    def __str__(self):
        return f"{self.empresa.nombre} - Balance {self.ano}"

class EstadoResultados(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    ano = models.IntegerField()
    total_ingresos = models.DecimalField(max_digits=15, decimal_places=2)
    costo_servicios = models.DecimalField(max_digits=15, decimal_places=2)
    resultado_bruto = models.DecimalField(max_digits=15, decimal_places=2)
    utilidad_antes_impuestos = models.DecimalField(max_digits=15, decimal_places=2)
    utilidad_neta = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('empresa', 'ano')

    def __str__(self):
        return f"{self.empresa.nombre} - E.R. {self.ano}"