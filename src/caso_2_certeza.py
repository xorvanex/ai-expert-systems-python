"""
SISTEMA EXPERTO DE CIBERSEGURIDAD (SOC) - FACTORES DE CERTEZA
Proyecto Integrador IA - Corte 1

Este módulo implementa el motor de inferencia basado en Factores de Certeza (MYCIN).
Toma como entrada las evidencias de los sensores de red, aplica propagación
mediante operadores lógicos, resuelve la concurrencia y genera un diagnóstico en consola.
"""

import sys

# ==========================================
# 1. FUNCIONES BASE DEL MOTOR DE INFERENCIA
# ==========================================

def combinar_certezas(cf1: float, cf2: float) -> float:
    """
    Combina dos factores de certeza positivos que apoyan la misma hipótesis.
    Fórmula de acumulación asintótica de MYCIN.
    """
    if cf1 <= 0 and cf2 <= 0:
        return 0.0
    # Si uno es cero, retorna el otro
    if cf1 <= 0: return cf2
    if cf2 <= 0: return cf1
    
    return cf1 + cf2 - (cf1 * cf2)

def evaluar_motor_certeza(evidencias: dict) -> dict:
    """
    Evalúa las 4 reglas del sistema experto aplicando la propagación lógica de la certeza.
    Retorna un diccionario con las certezas finales de las 3 hipótesis (CH1, CH2, CH3)
    y el registro de qué reglas se activaron.
    """
    
    # Extraemos las evidencias para mayor legibilidad
    e1 = evidencias.get('E1', 0.0)
    e2 = evidencias.get('E2', 0.0)
    e3 = evidencias.get('E3', 0.0)
    e4 = evidencias.get('E4', 0.0)
    
    # ---------------------------------------------------------
    # EVALUACIÓN DE ANTECEDENTES Y PROPAGACIÓN DE REGLAS
    # ---------------------------------------------------------
    
    # Regla 1: SI Pico de Ancho de Banda (E1) ENTONCES DDoS (CH1) [CR = 0.80]
    ant_r1 = e1
    cf_r1 = ant_r1 * 0.80 if ant_r1 > 0 else 0.0
    
    # Regla 2: SI Intentos fallidos SSH (E2) AND Cambios en Firmas (E4) ENTONCES Ransomware (CH2) [CR = 0.75]
    # Aplicamos operador MIN para el AND lógico
    ant_r2 = min(e2, e4)
    cf_r2 = ant_r2 * 0.75 if ant_r2 > 0 else 0.0
    
    # Regla 3: SI Antivirus detecta amenazas (E3) ENTONCES Ransomware (CH2) [CR = 0.60]
    ant_r3 = e3
    cf_r3 = ant_r3 * 0.60 if ant_r3 > 0 else 0.0
    
    # Regla 4: SI NOT Pico de Ancho de Banda (E1) OR Antivirus Inactivo (NOT E3) ENTONCES Falsa Alarma (CH3) [CR = 0.50]
    # NOT invierte el signo. OR es el operador MAX.
    ant_r4 = max(-e1, -e3)
    cf_r4 = ant_r4 * 0.50 if ant_r4 > 0 else 0.0

    # ---------------------------------------------------------
    # CO-SUSCRIPCIÓN DE HIPÓTESIS (Combinación concurrente)
    # ---------------------------------------------------------
    
    # CH1 solo depende de R1
    ch1_final = cf_r1
    
    # CH2 es apoyada por R2 y R3 (Requiere combinación si ambas disparan)
    ch2_final = combinar_certezas(cf_r2, cf_r3)
    
    # CH3 solo depende de R4
    ch3_final = cf_r4
    
    return {
        'hipotesis': {
            'CH1 (Ataque DDoS)': ch1_final,
            'CH2 (Ransomware)': ch2_final,
            'CH3 (Falsa Alarma)': ch3_final
        },
        'reglas_activadas': {
            'R1': cf_r1 > 0,
            'R2': cf_r2 > 0,
            'R3': cf_r3 > 0,
            'R4': cf_r4 > 0
        }
    }


# ==========================================
# 2. INTERFAZ DE CONSOLA (CLI ELEGANT)
# ==========================================

def mostrar_encabezado():
    print("=" * 65)
    print("  SOC - SISTEMA DE TRIAGE BASADO EN FACTORES DE CERTEZA")
    print("=" * 65)
    print("Ingrese las lecturas de certeza de los sensores (entre -1.0 y 1.0)\n")

def imprimir_resultados(resultados: dict):
    """Imprime el diagnóstico final formateado de forma elegante en consola."""
    print("\n" + "=" * 65)
    print(" REPORTE DIAGNÓSTICO DEL SISTEMA EXPERTO")
    print("=" * 65)
    
    print("\n[+] ESTADO DE LAS REGLAS LÓGICAS:")
    for regla, activa in resultados['reglas_activadas'].items():
        estado = " DISPARADA" if activa else " DESCARTADA (Antecedente <= 0)"
        print(f"    - {regla}: {estado}")
        
    print("\n[+] CONFIANZA DE LAS HIPÓTESIS (CO-SUSCRIPCIÓN):")
    hipotesis_ordenadas = sorted(resultados['hipotesis'].items(), key=lambda x: x[1], reverse=True)
    
    for hip, certeza in hipotesis_ordenadas:
        barra = "" * int(certeza * 30)
        print(f"    {hip:<20} | {certeza*100:6.2f}% | {barra}")
        
    print("-" * 65)
    
    # Determinación de la amenaza principal (Triage)
    amenaza_principal, certeza_max = hipotesis_ordenadas[0]
    
    if certeza_max == 0:
        print("\n  ADVERTENCIA: Las evidencias no sugieren ninguna amenaza conocida.")
    else:
        print(f"\n TRIAGE RECOMENDADO:")
        print(f"   El sistema experto recomienda al ingeniero del SOC mitigar primero:")
        print(f"   >> {amenaza_principal.upper()} (Nivel de Certeza: {certeza_max*100:.1f}%) <<")
        
    print("=" * 65 + "\n")

def main():
    mostrar_encabezado()
    
    # Modo Interactivo: Captura de valores por consola
    evidencias = {}
    
    try:
        e1_val = input("1. CE(E1) - Pico anómalo en ancho de banda    [Ej. 0.85]: ")
        e2_val = input("2. CE(E2) - Intentos masivos fallidos SSH     [Ej. 0.90]: ")
        e3_val = input("3. CE(E3) - Alerta de Antivirus Corporativo   [Ej.-0.40]: ")
        e4_val = input("4. CE(E4) - Cambios en Firmas SHA-256         [Ej. 0.70]: ")
        
        # Validar si el usuario presionó Enter sin escribir nada
        evidencias['E1'] = float(e1_val) if e1_val.strip() else 0.85
        evidencias['E2'] = float(e2_val) if e2_val.strip() else 0.90
        evidencias['E3'] = float(e3_val) if e3_val.strip() else -0.40
        evidencias['E4'] = float(e4_val) if e4_val.strip() else 0.70
        
    except ValueError:
        print("\nERROR: Por favor ingrese valores numéricos válidos (ej. 0.85 o -0.4).")
        sys.exit(1)
        
    # Verificar rangos válidos del modelo MYCIN [-1.0 a 1.0]
    for key, val in evidencias.items():
        if not (-1.0 <= val <= 1.0):
            print(f"\nERROR: El valor {val} para {key} está fuera del rango teórico [-1.0, 1.0]")
            sys.exit(1)
            
    # Ejecutar el motor de inferencia
    resultados = evaluar_motor_certeza(evidencias)
    
    # Mostrar resultados
    imprimir_resultados(resultados)

if __name__ == "__main__":
    # Permite cancelar la ejecución con Ctrl+C sin ensuciar la consola
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada por el usuario.")
        sys.exit(0)
