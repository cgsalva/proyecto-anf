from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import pandas as pd
import io
from decimal import Decimal

from .models import Empresa, BalanceGeneral, EstadoResultados
from .forms import UploadDataForm 
from .analysis import (
    calcular_ratios, 
    calcular_analisis_vertical, 
    calcular_analisis_horizontal, 
    calcular_fuentes_y_usos
)

@login_required
def dashboard(request):
    try:
        empresa = Empresa.objects.get(id=1) 
    except Empresa.DoesNotExist:
        messages.error(request, 'No hay datos cargados. Por favor, sube los archivos.')
        return redirect('upload_data')

    # --- LÍNEAS DE DEPURACIÓN ELIMINADAS ---
    # Ya no mostramos mensajes en la terminal ni en el dashboard
    # ----------------------------------------

    # Ejecutar todos los análisis
    ratios = calcular_ratios(empresa.id)
    vertical = calcular_analisis_vertical(empresa.id)
    horizontal = calcular_analisis_horizontal(empresa.id)
    fuentes_usos = calcular_fuentes_y_usos(empresa.id)

    context = {
        'empresa_nombre': empresa.nombre,
        'ratios': ratios,
        'vertical_balance': vertical.get('balance', {}),
        'vertical_resultados': vertical.get('resultados', {}),
        'horizontal_balance': horizontal.get('balance', {}),
        'horizontal_resultados': horizontal.get('resultados', {}),
        'fuentes_usos': fuentes_usos.get('items', []),
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def upload_data(request):
    if request.method == 'POST':
        form = UploadDataForm(request.POST, request.FILES)
        if form.is_valid():
            nombre_empresa = form.cleaned_data['empresa_nombre']
            archivo_balance_csv = request.FILES['archivo_balance']
            archivo_resultados_csv = request.FILES['archivo_resultados']
            
            try:
                empresa, created = Empresa.objects.update_or_create(
                    id=1, 
                    defaults={'nombre': nombre_empresa}
                )
                
                BalanceGeneral.objects.filter(empresa=empresa).delete()
                EstadoResultados.objects.filter(empresa=empresa).delete()
                
                df_balance = pd.read_csv(io.StringIO(archivo_balance_csv.read().decode('utf-8')))
                df_resultados = pd.read_csv(io.StringIO(archivo_resultados_csv.read().decode('utf-8')))
                df_balance = df_balance.fillna(0)
                df_resultados = df_resultados.fillna(0)

                balances_a_crear = []
                for index, row in df_balance.iterrows():
                    balances_a_crear.append(
                        BalanceGeneral(
                            empresa=empresa, ano=int(row['ano']), 
                            efectivo=Decimal(str(row.get('efectivo', 0))),
                            cartera_creditos_cp=Decimal(str(row.get('cartera_creditos_cp', 0))),
                            cartera_creditos_lp=Decimal(str(row.get('cartera_creditos_lp', 0))),
                            total_activo_corriente=Decimal(str(row.get('total_activo_corriente', 0))),
                            total_activo_no_corriente=Decimal(str(row.get('total_activo_no_corriente', 0))),
                            total_activo=Decimal(str(row.get('total_activo', 0))),
                            pasivo_corriente=Decimal(str(row.get('pasivo_corriente', 0))),
                            pasivo_no_corriente=Decimal(str(row.get('pasivo_no_corriente', 0))),
                            total_pasivo=Decimal(str(row.get('total_pasivo', 0))),
                            total_patrimonio=Decimal(str(row.get('total_patrimonio', 0)))
                        )
                    )
                BalanceGeneral.objects.bulk_create(balances_a_crear)

                resultados_a_crear = []
                for index, row in df_resultados.iterrows():
                    resultados_a_crear.append(
                        EstadoResultados(
                            empresa=empresa, ano=int(row['ano']), 
                            total_ingresos=Decimal(str(row.get('total_ingresos', 0))),
                            costo_servicios=Decimal(str(row.get('costo_servicios', 0))),
                            resultado_bruto=Decimal(str(row.get('resultado_bruto', 0))),
                            utilidad_antes_impuestos=Decimal(str(row.get('utilidad_antes_impuestos', 0))),
                            utilidad_neta=Decimal(str(row.get('utilidad_neta', 0)))
                        )
                    )
                EstadoResultados.objects.bulk_create(resultados_a_crear)
                
                # --- MENSAJE DE DEPURACIÓN CAMBIADO ---
                # Cambiamos el mensaje para que sea más simple
                messages.success(request, f'¡Datos de "{empresa.nombre}" cargados exitosamente!')
                return redirect('dashboard')

            except KeyError as e:
                messages.error(request, f'Error de Columna: No se encontró la columna {e}. Asegúrate de subir los archivos "BalanceData.csv" y "ResultadosData.csv" correctos.')
            except Exception as e:
                messages.error(request, f'Error al procesar los archivos: {e}. Asegúrate que las columnas del CSV coincidan.')

    else:
        form = UploadDataForm()

    return render(request, 'upload.html', {'form': form})