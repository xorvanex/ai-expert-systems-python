# PRIMER PROYECTO INTEGRADOR - INTELIGENCIA ARTIFICIAL
**Sistemas Basados en Conocimiento y Lógica Difusa**

Este repositorio contiene la implementación matemática y computacional de dos sistemas expertos diseñados para la resolución de problemas de ingeniería bajo incertidumbre.

## 📋 Estructura del Proyecto

El proyecto está organizado en las siguientes directivas:

```text
📦 primer-proyecto-integrador-ia
 ┣ 📂 docs               # Memorias de cálculo y justificaciones matemáticas
 ┣ 📂 src                # Código fuente principal de los motores de inferencia
 ┣ 📜 .gitignore         # Archivos ignorados por el control de versiones
 ┣ 📜 requirements.txt   # Dependencias necesarias para ejecutar el proyecto
 ┗ 📜 README.md          # Instructivo de ejecución
```

## 🛠️ Requisitos del Sistema

Para ejecutar los scripts de este proyecto se requiere **Python 3.8 o superior**. Se recomienda encarecidamente utilizar un entorno virtual (venv) para la instalación de las dependencias.

1. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```

2. **Instalar dependencias requeridas:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Dependencias principales: `numpy` y `matplotlib`)*

---

## 🚀 Ejecución de los Programas

### A) CASO 1: Lógica Difusa (Sistema de Alerta Temprana)
Implementación paramétrica de un algoritmo de inferencia difusa (Mamdani/Larsen) que incluye una Interfaz Gráfica de Usuario (Dashboard) interactiva para el trazado de funciones de membresía y cálculo del centroide.

**Instrucciones de ejecución:**
1. Ejecute el siguiente comando en la raíz del proyecto:
   ```bash
   python src/caso_1_difuso.py
   ```
2. Se desplegará el **Dashboard Difuso**.
3. Ingrese los valores numéricos nítidos para **Nivel del Río** (0 a 10) y **Precipitación** (0 a 200).
4. Haga clic en el botón verde **"EJECUTAR ANÁLISIS"**.
5. Navegue por las pestañas para auditar el proceso completo: Fusificación, Activación de la Base de Reglas, Gráficas de Inferencia y Desfusificación (Decisión Final).

### B) CASO 2: Factores de Certeza (Triage SOC)
Motor de inferencia lógico desarrollado para un Centro de Operaciones de Seguridad (SOC). Utiliza las fórmulas de propagación y co-suscripción del modelo MYCIN para clasificar incidentes cibernéticos.

**Instrucciones de ejecución:**
1. Ejecute el siguiente comando en la raíz del proyecto:
   ```bash
   python src/caso_2_certeza.py
   ```
2. El sistema interactivo en consola le solicitará ingresar los **4 valores de certeza de los sensores** (rango entre -1.0 y 1.0).
3. *(Opcional):* Si desea evaluar rápidamente el caso de estudio base documentado, simplemente presione la tecla **ENTER** en cada pregunta para cargar los valores por defecto.
4. El motor imprimirá un reporte diagnóstico estructurado detallando las reglas disparadas, descartadas, y la jerarquía de las amenazas detectadas.

---

## 📝 Resultados Esperados y Justificación

- **Caso 1:** El sistema demuestra visualmente el efecto matemático del operador Mínimo (recorte de Mamdani) frente al operador Producto (escalado de Larsen), y recomienda de manera autónoma la alerta más conservadora para protección civil.
- **Caso 2:** El algoritmo propaga exitosamente las certezas mediante los operadores `AND/OR/NOT` y resuelve hipótesis concurrentes de manera asintótica para entregar una recomendación de triage al ingeniero en tiempo real.
