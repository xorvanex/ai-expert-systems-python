"""
SISTEMA EXPERTO DIFUSO - ALERTA TEMPRANA
Proyecto Integrador IA - Corte 1

Este módulo implementa el algoritmo de inferencia difusa (Mamdani y Larsen)
para la evaluación del nivel de alerta en el Canal del Dique.
Incluye una interfaz gráfica paramétrica que demuestra cada paso del proceso.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. FUNCIONES DE MEMBRESÍA (FUSIFICACIÓN)
# ==========================================
# Se definen matemáticamente las funciones a trozos de cada término lingüístico.

# --- Nivel del Río (X1) ---
def mu_bajo(x: float) -> float:
    if x <= 2: return 1.0
    if x <= 4: return (4 - x) / 2.0
    return 0.0

def mu_normal(x: float) -> float:
    if 3 < x <= 5: return (x - 3) / 2.0
    if 5 < x < 7: return (7 - x) / 2.0
    return 0.0

def mu_alerta_x1(x: float) -> float:
    if 6 < x <= 7.5: return (x - 6) / 1.5
    if 7.5 < x < 9: return (9 - x) / 1.5
    return 0.0

def mu_critico(x: float) -> float:
    if 8 < x <= 10: return (x - 8) / 2.0
    if x > 10: return 1.0
    return 0.0

# --- Precipitación (X2) ---
def mu_seco(x: float) -> float:
    if x <= 40: return 1.0
    if x <= 80: return (80 - x) / 40.0
    return 0.0

def mu_moderado(x: float) -> float:
    if 60 < x <= 100: return (x - 60) / 40.0
    if 100 < x < 140: return (140 - x) / 40.0
    return 0.0

def mu_fuerte(x: float) -> float:
    if 110 < x <= 160: return (x - 110) / 50.0
    if x > 160: return 1.0
    return 0.0

# --- Alerta de Emergencia (Y) ---
def mu_nula(y: float) -> float:
    if y <= 10: return 1.0
    if y <= 25: return (25 - y) / 15.0
    return 0.0

def mu_preventiva(y: float) -> float:
    if 20 < y <= 35: return (y - 20) / 15.0
    if 35 < y < 50: return (50 - y) / 15.0
    return 0.0

def mu_alerta_amarilla(y: float) -> float:
    if 45 < y <= 60: return (y - 45) / 15.0
    if 60 < y < 75: return (75 - y) / 15.0
    return 0.0

def mu_alerta_roja(y: float) -> float:
    if 70 < y <= 90: return (y - 70) / 20.0
    if y > 90: return 1.0
    return 0.0

# ==========================================
# 2. MOTOR DE INFERENCIA
# ==========================================
def evaluar_sistema_completo(x1: float, x2: float) -> dict:
    """
    Realiza la inferencia difusa completa para las entradas dadas.
    Retorna un diccionario con los grados de activación, el estado de las 
    reglas, y los vectores para graficar la salida agregada.
    """
    
    # 2.1 Fusificación de los valores nítidos de entrada
    fuz_x1 = {
        'Bajo': mu_bajo(x1), 
        'Normal': mu_normal(x1), 
        'Alerta': mu_alerta_x1(x1), 
        'Crítico': mu_critico(x1)
    }
    
    fuz_x2 = {
        'Seco': mu_seco(x2), 
        'Moderado': mu_moderado(x2), 
        'Lluvia Fuerte': mu_fuerte(x2)
    }
    
    # 2.2 Evaluación de las 9 reglas
    # Usamos MIN para la conjunción (AND) y MAX para la disyunción (OR)
    reglas = [
        ("R1", "Bajo", "Nula", fuz_x1['Bajo']),
        ("R2", "Normal ∧ Seco", "Nula", min(fuz_x1['Normal'], fuz_x2['Seco'])),
        ("R3", "Normal ∧ Moderado", "Preventiva", min(fuz_x1['Normal'], fuz_x2['Moderado'])),
        ("R4", "Normal ∧ Fuerte", "Amarilla", min(fuz_x1['Normal'], fuz_x2['Lluvia Fuerte'])),
        ("R5", "Alerta ∧ Seco", "Preventiva", min(fuz_x1['Alerta'], fuz_x2['Seco'])),
        ("R6", "Alerta ∧ Moderado", "Amarilla", min(fuz_x1['Alerta'], fuz_x2['Moderado'])),
        ("R7", "Alerta ∧ Fuerte", "Roja", min(fuz_x1['Alerta'], fuz_x2['Lluvia Fuerte'])),
        ("R8", "Crítico ∨ Lluvia Fuerte", "Roja", max(fuz_x1['Crítico'], fuz_x2['Lluvia Fuerte'])),
        ("R9", "Crítico", "Roja", fuz_x1['Crítico'])
    ]
    
    # Agrupamos la fuerza máxima que empuja hacia cada consecuente
    f_nula = max(reglas[0][3], reglas[1][3])
    f_prev = max(reglas[2][3], reglas[4][3])
    f_amar = max(reglas[3][3], reglas[5][3])
    f_roja = max(reglas[6][3], reglas[7][3], reglas[8][3])
    
    # 2.3 Agregación de los conjuntos de salida activados
    y_vals = np.arange(0, 100.5, 0.5) # Discretizamos el universo de 0 a 100
    
    y_mamdani = np.zeros_like(y_vals)
    y_larsen = np.zeros_like(y_vals)
    
    for i, y in enumerate(y_vals):
        # Mamdani recorta el conjunto con la función MIN
        y_mamdani[i] = max(
            min(f_nula, mu_nula(y)), 
            min(f_prev, mu_preventiva(y)),
            min(f_amar, mu_alerta_amarilla(y)), 
            min(f_roja, mu_alerta_roja(y))
        )
        
        # Larsen escala el conjunto multiplicando
        y_larsen[i] = max(
            f_nula * mu_nula(y), 
            f_prev * mu_preventiva(y),
            f_amar * mu_alerta_amarilla(y), 
            f_roja * mu_alerta_roja(y)
        )
        
    # 2.4 Métodos de Desfusificación
    def calc_centroide(arr):
        """Calcula el centro de gravedad (Centroide) mediante sumatoria discreta."""
        den = np.sum(arr)
        return np.sum(y_vals * arr) / den if den != 0 else 0
        
    def calc_com(arr):
        """Calcula el Centro de Máximos (CoM)."""
        if np.max(arr) == 0: 
            return 0
        max_val = np.max(arr)
        return np.mean(y_vals[np.where(arr == max_val)[0]])

    return {
        'fuz_x1': fuz_x1, 'fuz_x2': fuz_x2, 'reglas': reglas,
        'y_vals': y_vals, 'y_mamdani': y_mamdani, 'y_larsen': y_larsen,
        'cent_m': calc_centroide(y_mamdani), 'com_m': calc_com(y_mamdani),
        'cent_l': calc_centroide(y_larsen), 'com_l': calc_com(y_larsen)
    }

# ==========================================
# 3. INTERFAZ GRÁFICA (DASHBOARD)
# ==========================================
class DashboardDifuso:
    """Clase principal que maneja la ventana interactiva y la renderización de datos."""
    def __init__(self, root):
        self.root = root
        self.root.title("SISTEMA DE ALERTA TEMPRANA - CANAL DEL DIQUE")
        self.root.geometry("1100x850")
        
        # --- Configuración visual base ---
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TNotebook.Tab', font=('Arial', 14, 'bold'), padding=[20, 10])
        style.map('TNotebook.Tab', 
                  background=[('selected', '#28a745')], 
                  foreground=[('selected', 'white')])
        
        style.configure('Treeview', font=('Arial', 12), rowheight=32)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), background="#e0e0e0")

        # Layout general
        self._construir_header()
        
        # Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_fuz = tk.Frame(self.notebook)
        self.tab_reg = tk.Frame(self.notebook)
        self.tab_inf = tk.Frame(self.notebook)
        self.tab_des = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_fuz, text="1. Fusificación")
        self.notebook.add(self.tab_reg, text="2. Reglas Activadas")
        self.notebook.add(self.tab_inf, text="3. Inferencia")
        self.notebook.add(self.tab_des, text="4. Decisión Final")
        
        # Inicializar contenido de cada pestaña
        self._build_tab_fuz()
        self._build_tab_reg()
        self._build_tab_inf()
        self._build_tab_des()
        
        # Ejecutar análisis inicial por defecto
        self.calcular() 

    def _construir_header(self):
        """Construye el panel superior de controles."""
        header = tk.Frame(self.root, bg="#1a3b5c", pady=15)
        header.pack(fill="x")
        
        tk.Label(header, text=" SISTEMA DE ALERTA TEMPRANA - LÓGICA DIFUSA", 
                 font=("Arial", 16, "bold"), bg="#1a3b5c", fg="white").pack()
        
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(fill="x", padx=20)
        
        tk.Label(input_frame, text="Nivel del Río (m):", font=("Arial", 12)).grid(row=0, column=0, padx=10)
        self.ent_x1 = ttk.Entry(input_frame, font=("Arial", 12), width=8)
        self.ent_x1.insert(0, "7.3")
        self.ent_x1.grid(row=0, column=1)
        
        tk.Label(input_frame, text="Precipitación (mm):", font=("Arial", 12)).grid(row=0, column=2, padx=10)
        self.ent_x2 = ttk.Entry(input_frame, font=("Arial", 12), width=8)
        self.ent_x2.insert(0, "115")
        self.ent_x2.grid(row=0, column=3)
        
        btn_calc = tk.Button(input_frame, text="EJECUTAR ANÁLISIS", bg="#28a745", fg="white", 
                             font=("Arial", 12, "bold"), command=self.calcular, padx=10, pady=5)
        btn_calc.grid(row=0, column=4, padx=30)

    def _build_tab_fuz(self):
        """Construye los elementos de la pestaña de fusificación."""
        self.fig_fuz, (self.ax_x1, self.ax_x2) = plt.subplots(1, 2, figsize=(10, 3.5))
        self.canvas_fuz = FigureCanvasTkAgg(self.fig_fuz, master=self.tab_fuz)
        self.canvas_fuz.get_tk_widget().pack(fill="x", pady=5)
        
        frame_tables = tk.Frame(self.tab_fuz)
        frame_tables.pack(fill="both", expand=True, pady=10, padx=80)
        
        self.tree_x1 = ttk.Treeview(frame_tables, columns=("Conjunto", "u"), show="headings", height=4)
        self.tree_x1.heading("Conjunto", text="Conjunto: NIVEL DEL RÍO")
        self.tree_x1.heading("u", text="Grado de Pertenencia (μ)")
        self.tree_x1.pack(side="top", fill="x", pady=5)
        
        self.tree_x2 = ttk.Treeview(frame_tables, columns=("Conjunto", "u"), show="headings", height=3)
        self.tree_x2.heading("Conjunto", text="Conjunto: PRECIPITACIÓN")
        self.tree_x2.heading("u", text="Grado de Pertenencia (μ)")
        self.tree_x2.pack(side="top", fill="x", pady=5)
        
        self.tree_x1.tag_configure('activa', background='#d4edda', font=('Arial', 12, 'bold'))
        self.tree_x2.tag_configure('activa', background='#d4edda', font=('Arial', 12, 'bold'))

    def _build_tab_reg(self):
        """Construye la pestaña que muestra la activación de la base de reglas."""
        tk.Label(self.tab_reg, text="Base de Conocimiento (Reglas de Inferencia)", 
                 font=("Arial", 16, "bold")).pack(pady=10)
                 
        self.lbl_activas = tk.Label(self.tab_reg, text="0 de 9 reglas activadas", font=("Arial", 14), fg="blue")
        self.lbl_activas.pack(pady=5)
        
        self.tree_reglas = ttk.Treeview(self.tab_reg, columns=("ID", "Antecedentes", "Fuerza", "Consecuente"), 
                                        show="headings", height=9)
        self.tree_reglas.heading("ID", text="Regla")
        self.tree_reglas.column("ID", width=60, anchor="center")
        self.tree_reglas.heading("Antecedentes", text="Antecedentes lógicos")
        self.tree_reglas.column("Antecedentes", width=450)
        self.tree_reglas.heading("Fuerza", text="Fuerza de Activación (μ)")
        self.tree_reglas.column("Fuerza", width=180, anchor="center")
        self.tree_reglas.heading("Consecuente", text="Consecuente (Salida)")
        self.tree_reglas.column("Consecuente", width=180, anchor="center")
        self.tree_reglas.pack(fill="x", padx=40, pady=10)
        
        self.tree_reglas.tag_configure('activa', background='#cce5ff', font=('Arial', 12, 'bold'))

    def _build_tab_inf(self):
        """Pestaña que aloja la comparativa gráfica Mamdani vs Larsen."""
        self.fig_inf, (self.ax_mam, self.ax_lar) = plt.subplots(1, 2, figsize=(10, 4.5))
        self.canvas_inf = FigureCanvasTkAgg(self.fig_inf, master=self.tab_inf)
        self.canvas_inf.get_tk_widget().pack(fill="both", expand=True, pady=20)

    def _build_tab_des(self):
        """Pestaña final con resultados de desfusificación y tarjeta de decisión dinámica."""
        frame_top = tk.Frame(self.tab_des)
        frame_top.pack(fill="x", pady=20)
        
        # Panel comparativo (Izquierda)
        frame_comp = tk.LabelFrame(frame_top, text="Comparación de Métodos", font=("Arial", 14, "bold"))
        frame_comp.pack(side="left", padx=30, fill="both", expand=True)
        
        self.tree_comp = ttk.Treeview(frame_comp, columns=("Metodo", "Mamdani", "Larsen"), show="headings", height=2)
        self.tree_comp.heading("Metodo", text="Desfusificación")
        self.tree_comp.heading("Mamdani", text="Mamdani")
        self.tree_comp.heading("Larsen", text="Larsen")
        self.tree_comp.pack(padx=10, pady=20, fill="x")
        
        # Tarjeta de alerta (Derecha)
        self.frame_tarjeta = tk.Frame(frame_top, relief="ridge", bd=4)
        self.frame_tarjeta.pack(side="right", padx=30, ipadx=40, ipady=15)
        
        self.lbl_tarjeta_titulo = tk.Label(self.frame_tarjeta, text="NIVEL DE ALERTA", font=("Arial", 16))
        self.lbl_tarjeta_titulo.pack()
        
        self.lbl_alerta_val = tk.Label(self.frame_tarjeta, text="0.00 %", font=("Arial", 36, "bold"))
        self.lbl_alerta_val.pack(pady=5)
        
        self.lbl_alerta_txt = tk.Label(self.frame_tarjeta, text="ALERTA", font=("Arial", 22, "bold"))
        self.lbl_alerta_txt.pack()
        
        self.lbl_tarjeta_sub = tk.Label(self.frame_tarjeta, text="Método sugerido: Larsen + Centroide", 
                                        font=("Arial", 12, "italic"))
        self.lbl_tarjeta_sub.pack(pady=5)
        
        # Interpretación textual breve
        frame_inter = tk.LabelFrame(self.tab_des, text="Interpretación del Sistema", font=("Arial", 12, "bold"))
        frame_inter.pack(fill="x", padx=30, pady=10)
        self.txt_inter = tk.Text(frame_inter, height=3, font=("Arial", 12), wrap="word", bg="#f4f4f4")
        self.txt_inter.pack(fill="x", padx=10, pady=10)

    def calcular(self):
        """Ejecuta toda la tubería difusa y refresca la interfaz gráfica."""
        try:
            x1 = float(self.ent_x1.get())
            x2 = float(self.ent_x2.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            return
            
        res = evaluar_sistema_completo(x1, x2)
        
        # --- Actualizar Tab 1: Gráficas y tablas ---
        self.ax_x1.clear(); self.ax_x2.clear()
        
        xs = np.linspace(0, 10, 100)
        self.ax_x1.plot(xs, [mu_bajo(x) for x in xs], label='Bajo')
        self.ax_x1.plot(xs, [mu_normal(x) for x in xs], label='Normal')
        self.ax_x1.plot(xs, [mu_alerta_x1(x) for x in xs], label='Alerta')
        self.ax_x1.plot(xs, [mu_critico(x) for x in xs], label='Crítico')
        self.ax_x1.axvline(x=x1, color='red', linestyle='--', linewidth=2)
        self.ax_x1.set_title("X1: Nivel del Río (m)", fontsize=12)
        self.ax_x1.grid(True, alpha=0.3)
        self.ax_x1.legend(fontsize=9)
        
        xs2 = np.linspace(0, 200, 100)
        self.ax_x2.plot(xs2, [mu_seco(x) for x in xs2], label='Seco')
        self.ax_x2.plot(xs2, [mu_moderado(x) for x in xs2], label='Moderado')
        self.ax_x2.plot(xs2, [mu_fuerte(x) for x in xs2], label='Fuerte')
        self.ax_x2.axvline(x=x2, color='red', linestyle='--', linewidth=2)
        self.ax_x2.set_title("X2: Precipitación Acumulada (mm)", fontsize=12)
        self.ax_x2.grid(True, alpha=0.3)
        self.ax_x2.legend(fontsize=9)
        
        self.canvas_fuz.draw()
        
        self.tree_x1.delete(*self.tree_x1.get_children())
        for k, v in res['fuz_x1'].items():
            tag = 'activa' if v > 0 else ''
            self.tree_x1.insert("", "end", values=(k, f"{v:.3f}"), tags=(tag,))
            
        self.tree_x2.delete(*self.tree_x2.get_children())
        for k, v in res['fuz_x2'].items():
            tag = 'activa' if v > 0 else ''
            self.tree_x2.insert("", "end", values=(k, f"{v:.3f}"), tags=(tag,))
            
        # --- Actualizar Tab 2: Reglas activadas ---
        self.tree_reglas.delete(*self.tree_reglas.get_children())
        activas = 0
        textos_activas = []
        for r in res['reglas']:
            tag = 'activa' if r[3] > 0 else ''
            if r[3] > 0: 
                activas += 1
                textos_activas.append(f"{r[2]} ({r[3]:.2f})")
            self.tree_reglas.insert("", "end", values=(r[0], r[1], f"{r[3]:.3f}", r[2]), tags=(tag,))
        self.lbl_activas.config(text=f"Total: {activas} de 9 reglas se han activado")
        
        # --- Actualizar Tab 3: Gráficas de salida ---
        self.ax_mam.clear(); self.ax_lar.clear()
        
        self.ax_mam.plot(res['y_vals'], res['y_mamdani'], color='purple')
        self.ax_mam.fill_between(res['y_vals'], res['y_mamdani'], color='purple', alpha=0.3)
        self.ax_mam.set_title("Agregación MAMDANI\n(Recorte - Op. MIN)", fontsize=12)
        self.ax_mam.set_ylim(0, 1.1)
        self.ax_mam.grid(True, alpha=0.3)
        
        self.ax_lar.plot(res['y_vals'], res['y_larsen'], color='teal')
        self.ax_lar.fill_between(res['y_vals'], res['y_larsen'], color='teal', alpha=0.3)
        self.ax_lar.set_title("Agregación LARSEN\n(Escalado - Op. PRODUCTO)", fontsize=12)
        self.ax_lar.set_ylim(0, 1.1)
        self.ax_lar.grid(True, alpha=0.3)
        
        self.canvas_inf.draw()
        
        # --- Actualizar Tab 4: Desfusificación y Decisión ---
        self.tree_comp.delete(*self.tree_comp.get_children())
        self.tree_comp.insert("", "end", values=("Centroide", f"{res['cent_m']:.2f}%", f"{res['cent_l']:.2f}%"))
        self.tree_comp.insert("", "end", values=("Centro de Máximos", f"{res['com_m']:.2f}%", f"{res['com_l']:.2f}%"))
        
        alerta_final = res['cent_l']
        self.lbl_alerta_val.config(text=f"{alerta_final:.2f} %")
        
        # Lógica de colorimetría para la tarjeta
        if alerta_final >= 70:
            txt = " ALERTA ROJA"
            bg_col = "#f8d7da" # Rojo claro
            fg_col = "#721c24" # Rojo oscuro
        elif alerta_final >= 45:
            txt = " ALERTA AMARILLA"
            bg_col = "#fff3cd" # Amarillo claro
            fg_col = "#856404" # Amarillo oscuro
        elif alerta_final >= 20:
            txt = " ALERTA PREVENTIVA"
            bg_col = "#cce5ff" # Azul claro
            fg_col = "#004085" # Azul oscuro
        else:
            txt = " ALERTA NULA"
            bg_col = "#d4edda" # Verde claro
            fg_col = "#155724" # Verde oscuro
            
        self.lbl_alerta_txt.config(text=txt, fg=fg_col, bg=bg_col)
        self.lbl_alerta_val.config(fg=fg_col, bg=bg_col)
        self.lbl_tarjeta_titulo.config(bg=bg_col, fg=fg_col)
        self.lbl_tarjeta_sub.config(bg=bg_col, fg=fg_col)
        self.frame_tarjeta.config(bg=bg_col)
            
        self.txt_inter.delete(1.0, tk.END)
        texto = f"El sistema evaluó un Nivel de Río de {x1}m y una Precipitación de {x2}mm. "
        if activas == 0:
            texto += "Estas condiciones son atípicas y no activan ninguna regla de la base de conocimientos."
        else:
            texto += f"Se activaron {activas} reglas con impacto hacia: {', '.join(set(textos_activas))}. "
            texto += f"El algoritmo recomienda un nivel de alerta de {alerta_final:.2f}% (Larsen+Centroide)."
        self.txt_inter.insert(tk.END, texto)

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardDifuso(root)
    root.mainloop()
