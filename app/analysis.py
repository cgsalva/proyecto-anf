from .models import BalanceGeneral, EstadoResultados
from decimal import Decimal

# --- Función Auxiliar ---
def get_data(empresa_id):
    balances = BalanceGeneral.objects.filter(empresa_id=empresa_id).order_by('ano')
    resultados = EstadoResultados.objects.filter(empresa_id=empresa_id).order_by('ano')
    balances_map = {b.ano: b for b in balances}
    anos = sorted(balances_map.keys())
    return balances, resultados, balances_map, anos

# --- Función Auxiliar para División Segura ---
def safe_div(numerador, denominador):
    if denominador in [0, None] or denominador == Decimal(0):
        return Decimal(0)
    return (Decimal(numerador) / Decimal(denominador))

# --- 1. CÁLCULO DE RATIOS ---
def calcular_ratios(empresa_id):
    balances, resultados, _, _ = get_data(empresa_id)
    ratios_finales = {
        'liquidez': {'anos': [], 'razon_corriente': [], 'prueba_acida': []},
        'endeudamiento': {'anos': [], 'endeudamiento': [], 'apalancamiento': []},
        'rentabilidad': {'anos': [], 'margen_neto': [], 'roa': [], 'roe': []},
    }
    balances_con_er = [b for b in balances if b.ano in [r.ano for r in resultados]]
    
    for b in balances_con_er:
        er = next(r for r in resultados if r.ano == b.ano)
        ano = b.ano
        
        # --- Liquidez (convertido a float) ---
        ratios_finales['liquidez']['anos'].append(ano)
        razon_corr = safe_div(b.total_activo_corriente, b.pasivo_corriente)
        # ¡CAMBIO! Convertir Decimal a float para JavaScript
        ratios_finales['liquidez']['razon_corriente'].append(float(razon_corr))
        ratios_finales['liquidez']['prueba_acida'].append(float(razon_corr)) 

        # --- Endeudamiento (convertido a float) ---
        ratios_finales['endeudamiento']['anos'].append(ano)
        endeudamiento = safe_div(b.total_pasivo, b.total_activo)
        ratios_finales['endeudamiento']['endeudamiento'].append(float(endeudamiento * 100))
        apalancamiento = safe_div(b.total_pasivo, b.total_patrimonio)
        ratios_finales['endeudamiento']['apalancamiento'].append(float(apalancamiento))

        # --- Rentabilidad (convertido a float) ---
        ratios_finales['rentabilidad']['anos'].append(ano)
        margen_neto = safe_div(er.utilidad_neta, er.total_ingresos)
        ratios_finales['rentabilidad']['margen_neto'].append(float(margen_neto * 100))
        roa = safe_div(er.utilidad_neta, b.total_activo)
        ratios_finales['rentabilidad']['roa'].append(float(roa * 100))
        roe = safe_div(er.utilidad_neta, b.total_patrimonio)
        ratios_finales['rentabilidad']['roe'].append(float(roe * 100))
    return ratios_finales

# --- 2. CÁLCULO ANÁLISIS VERTICAL ---
def calcular_analisis_vertical(empresa_id):
    balances, resultados, _, anos = get_data(empresa_id)
    vertical = {
        'balance': {'anos': anos, 'cuentas': {}},
        'resultados': {'anos': anos, 'cuentas': {}}
    }
    
    # ¡CAMBIO! Convertir todo a float
    cuentas_b = {
        'Efectivo': [float(safe_div(b.efectivo, b.total_activo) * 100) for b in balances],
        'Cartera Créditos CP': [float(safe_div(b.cartera_creditos_cp, b.total_activo) * 100) for b in balances],
        'Total Activo Corriente': [float(safe_div(b.total_activo_corriente, b.total_activo) * 100) for b in balances],
        'Cartera Créditos LP': [float(safe_div(b.cartera_creditos_lp, b.total_activo) * 100) for b in balances],
        'Total Activo No Corriente': [float(safe_div(b.total_activo_no_corriente, b.total_activo) * 100) for b in balances],
        'Total Activo': [float(safe_div(b.total_activo, b.total_activo) * 100) for b in balances],
        'Pasivo Corriente': [float(safe_div(b.pasivo_corriente, b.total_activo) * 100) for b in balances],
        'Pasivo No Corriente': [float(safe_div(b.pasivo_no_corriente, b.total_activo) * 100) for b in balances],
        'Total Pasivo': [float(safe_div(b.total_pasivo, b.total_activo) * 100) for b in balances],
        'Total Patrimonio': [float(safe_div(b.total_patrimonio, b.total_activo) * 100) for b in balances],
    }
    vertical['balance']['cuentas'] = cuentas_b
    
    # ¡CAMBIO! Convertir todo a float
    cuentas_r = {
        'Total Ingresos': [float(safe_div(r.total_ingresos, r.total_ingresos) * 100) for r in resultados],
        'Costo Servicios': [float(safe_div(r.costo_servicios, r.total_ingresos) * 100) for r in resultados],
        'Resultado Bruto': [float(safe_div(r.resultado_bruto, r.total_ingresos) * 100) for r in resultados],
        'Utilidad Antes Impuestos': [float(safe_div(r.utilidad_antes_impuestos, r.total_ingresos) * 100) for r in resultados],
        'Utilidad Neta': [float(safe_div(r.utilidad_neta, r.total_ingresos) * 100) for r in resultados],
    }
    vertical['resultados']['cuentas'] = cuentas_r
    return vertical

# --- 3. CÁLCULO ANÁLISIS HORIZONTAL ---
def calcular_analisis_horizontal(empresa_id):
    balances, resultados, _, anos = get_data(empresa_id)
    if len(anos) < 2: return {}
    horizontal = {
        'balance': {'periodos': [], 'cuentas': {}},
        'resultados': {'periodos': [], 'cuentas': {}}
    }
    cuentas_b = {
        'Total Activo Corriente': [], 'Total Activo No Corriente': [], 'Total Activo': [], 
        'Pasivo Corriente': [], 'Pasivo No Corriente': [], 'Total Pasivo': [], 'Total Patrimonio': []
    }
    cuentas_r = {
        'Total Ingresos': [], 'Costo Servicios': [], 'Resultado Bruto': [], 'Utilidad Neta': []
    }

    for i in range(1, len(anos)):
        ano_actual, ano_anterior = anos[i], anos[i-1]
        periodo = f"{ano_actual} vs {ano_anterior}"
        horizontal['balance']['periodos'].append(periodo)
        horizontal['resultados']['periodos'].append(periodo)

        b_actual = next(b for b in balances if b.ano == ano_actual)
        b_anterior = next(b for b in balances if b.ano == ano_anterior)
        r_actual = next(r for r in resultados if r.ano == ano_actual)
        r_anterior = next(r for r in resultados if r.ano == ano_anterior)

        for cuenta in cuentas_b.keys():
            attr = cuenta.lower().replace(' ', '_')
            val_actual = getattr(b_actual, attr)
            val_anterior = getattr(b_anterior, attr)
            var_abs = val_actual - val_anterior
            var_rel = safe_div(var_abs, val_anterior) * 100
            # ¡CAMBIO! Convertir Decimal a float
            cuentas_b[cuenta].append({'abs': float(var_abs), 'rel': float(var_rel)})
            
        for cuenta in cuentas_r.keys():
            attr = cuenta.lower().replace(' ', '_')
            val_actual = getattr(r_actual, attr)
            val_anterior = getattr(r_anterior, attr)
            var_abs = val_actual - val_anterior
            var_rel = safe_div(var_abs, val_anterior) * 100
            # ¡CAMBIO! Convertir Decimal a float
            cuentas_r[cuenta].append({'abs': float(var_abs), 'rel': float(var_rel)})

    horizontal['balance']['cuentas'] = cuentas_b
    horizontal['resultados']['cuentas'] = cuentas_r
    return horizontal

# --- 4. CÁLCULO FUENTES Y USOS ---
def calcular_fuentes_y_usos(empresa_id):
    balances, _, _, anos = get_data(empresa_id)
    if len(anos) < 2: return {}
    fuentes_usos_final = {'periodos': [], 'items': []}
    
    for i in range(1, len(anos)):
        b_actual, b_anterior = balances[i], balances[i-1]
        periodo = f"{b_actual.ano} vs {b_anterior.ano}"
        fuentes_usos_final['periodos'].append(periodo)
        items_periodo = []
        
        # ¡CAMBIO! Convertir todo a float
        def check_activo(cuenta, val_act, val_ant):
            var = val_act - val_ant
            if var > 0: return {'cuenta': cuenta, 'var': float(var), 'fuente': 0, 'uso': float(var)}
            if var < 0: return {'cuenta': cuenta, 'var': float(var), 'fuente': float(-var), 'uso': 0}
            return None

        def check_pas_pat(cuenta, val_act, val_ant):
            var = val_act - val_ant
            if var > 0: return {'cuenta': cuenta, 'var': float(var), 'fuente': float(var), 'uso': 0}
            if var < 0: return {'cuenta': cuenta, 'var': float(var), 'fuente': 0, 'uso': float(-var)}
            return None

        items_periodo.append(check_activo('Activo Corriente', b_actual.total_activo_corriente, b_anterior.total_activo_corriente))
        items_periodo.append(check_activo('Activo No Corriente', b_actual.total_activo_no_corriente, b_anterior.total_activo_no_corriente))
        items_periodo.append(check_pas_pat('Pasivo Corriente', b_actual.pasivo_corriente, b_anterior.pasivo_corriente))
        items_periodo.append(check_pas_pat('Pasivo No Corriente', b_actual.pasivo_no_corriente, b_anterior.pasivo_no_corriente))
        items_periodo.append(check_pas_pat('Patrimonio', b_actual.total_patrimonio, b_anterior.total_patrimonio))
        
        items_periodo = [item for item in items_periodo if item is not None]
        total_fuentes = sum(item['fuente'] for item in items_periodo)
        total_usos = sum(item['uso'] for item in items_periodo)
        
        fuentes_usos_final['items'].append({
            'periodo_nombre': periodo,
            'cuentas': items_periodo,
            'total_fuentes': float(total_fuentes),
            'total_usos': float(total_usos)
        })
    return fuentes_usos_final