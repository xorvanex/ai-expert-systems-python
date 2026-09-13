# MEMORIAS DE CÁLCULO - CASO 2: FACTORES DE CERTEZA

**Escenario de Evaluación (Sistema Experto de Ciberseguridad SOC)**

El sistema busca clasificar alertas mediante tres hipótesis concurrentes:
*   **CH1:** Ataque de Denegación de Servicio Distribuido (DDoS)
*   **CH2:** Intrusión de Ransomware / Secuestro de Archivos
*   **CH3:** Falsa Alarma

**Evidencias Recolectadas por los Sensores (CE):**
*   $CE(E1)$ [Pico anómalo de ancho de banda] = $0.85$
*   $CE(E2)$ [Intentos fallidos SSH] = $0.90$
*   $CE(E3)$ [Alertas del antivirus corporativo] = $-0.40$
*   $CE(E4)$ [Cambios en Firmas SHA-256] = $0.70$

---

## 1. EVALUACIÓN DE REGLAS Y PROPAGACIÓN DE CERTEZA

La Teoría de Factores de Certeza establece los siguientes principios de propagación:
1.  **Conjunción (AND):** $CF(A \wedge B) = \min(CF(A), CF(B))$
2.  **Disyunción (OR):** $CF(A \vee B) = \max(CF(A), CF(B))$
3.  **Negación (NOT):** $CF(\neg A) = -CF(A)$
4.  **Propagación en Regla:** $CF(H) = CF(Antecedente) \times CR$. *(Nota: Si $CF(Antecedente) \leq 0$, se considera que no hay evidencia favorable y la regla no se activa para apoyar la hipótesis).*

### Regla 1 (R1): SI E1 ENTONCES CH1 ($CR = 0.80$)
*   **Antecedente:** $E1$
*   $CF(Antecedente_{R1}) = CE(E1) = 0.85$
*   Como $0.85 > 0$, la regla se activa y propaga su certeza hacia la hipótesis CH1.
*   **Cálculo:** $CF(CH1_{R1}) = 0.85 \times 0.80 = \mathbf{0.68}$

### Regla 2 (R2): SI E2 AND E4 ENTONCES CH2 ($CR = 0.75$)
*   **Antecedente:** $E2 \wedge E4$
*   $CF(Antecedente_{R2}) = \min(CE(E2), CE(E4)) = \min(0.90, 0.70) = 0.70$
*   Como $0.70 > 0$, la regla se activa.
*   **Cálculo:** $CF(CH2_{R2}) = 0.70 \times 0.75 = \mathbf{0.525}$

### Regla 3 (R3): SI E3 ENTONCES CH2 ($CR = 0.60$)
*   **Antecedente:** $E3$
*   $CF(Antecedente_{R3}) = CE(E3) = -0.40$
*   **Justificación Teórica:** En el modelo de certeza (estilo MYCIN), un factor de certeza negativo (o menor al umbral de disparo, típicamente $>0.2$) indica que la evidencia desfavorece o está ausente. Dado que el antecedente es negativo (hay certeza de que el antivirus NO detectó amenazas), la regla R3 no se dispara y no aporta evidencia favorable a la hipótesis de Ransomware.
*   **Cálculo:** La regla se descarta. $CF(CH2_{R3}) = \mathbf{0}$ (No aporta).

### Regla 4 (R4): SI NOT E1 OR NOT E3 ENTONCES CH3 ($CR = 0.50$)
*   **Antecedente:** $\neg E1 \vee \neg E3$
*   Evaluación de las negaciones:
    *   $CF(\neg E1) = -CE(E1) = -0.85$
    *   $CF(\neg E3) = -CE(E3) = -(-0.40) = 0.40$
*   $CF(Antecedente_{R4}) = \max(-0.85, 0.40) = 0.40$
*   **Justificación Teórica:** Aunque existe una fuerte evidencia de que *sí* hay pico de ancho de banda (lo que negativiza el primer término a -0.85), el operador OR selecciona el valor máximo. Al existir certeza moderada de que el antivirus *no* detectó amenazas ($0.40$), el antecedente global se vuelve positivo, permitiendo que la regla se active.
*   **Cálculo:** $CF(CH3_{R4}) = 0.40 \times 0.50 = \mathbf{0.20}$

---

## 2. CO-SUSCRIPCIÓN DE HIPÓTESIS

La fórmula de combinación para dos reglas que apoyan la misma hipótesis (con CF positivos concurrentes) es:
$CF_{combinado}(X, Y) = X + Y - (X \times Y)$

Analizando los resultados del paso anterior:
*   **CH1 (DDoS):** Solo es apoyada por R1.
    *   $CF(CH1) = \mathbf{0.68}$
*   **CH2 (Ransomware):** Apoyada por R2 y R3. Sin embargo, R3 fue descartada porque su antecedente fue negativo. Por lo tanto, no hay co-suscripción activa.
    *   $CF(CH2) = \mathbf{0.525}$
*   **CH3 (Falsa Alarma):** Solo es apoyada por R4.
    *   $CF(CH3) = \mathbf{0.20}$

**Conclusión y Recomendación Formal del Triage:**
1.  **CH1 (DDoS):** $68.0\%$ de certeza.
2.  **CH2 (Ransomware):** $52.5\%$ de certeza.
3.  **CH3 (Falsa Alarma):** $20.0\%$ de certeza.

El Sistema Experto recomienda al operador del SOC tratar el incidente como un **Ataque de Denegación de Servicio Distribuido (DDoS)** como prioridad uno (68% de confianza), seguido de un análisis preventivo de Ransomware (52.5%). Se descarta razonablemente la posibilidad de que sea una Falsa Alarma.

---

## 3. ANÁLISIS DE SENSIBILIDAD DE INCERTIDUMBRE

¿Qué sucedería si el factor de certeza de las alertas del antivirus (E3) cambiara de $-0.40$ a $0.60$ (es decir, el antivirus empieza a reportar detecciones positivas)?

### Recálculo de CH2 (Ransomware)
*   **Regla 3:** $Antecedente = E3 = 0.60$.
    *   Al ser positivo, R3 ahora sí se dispara: $CF(CH2_{R3}) = 0.60 \times 0.60 = 0.36$.
*   **Co-suscripción:** Ahora CH2 está apoyada concurrentemente por R2 (0.525) y R3 (0.36).
    *   $CF(CH2) = 0.525 + 0.36 - (0.525 \times 0.36)$
    *   $CF(CH2) = 0.885 - 0.189 = \mathbf{0.696}$

### Recálculo de CH3 (Falsa Alarma)
*   **Regla 4:** $Antecedente = \neg E1 \vee \neg E3$
    *   $CF(\neg E1) = -0.85$
    *   $CF(\neg E3) = -(0.60) = -0.60$
    *   $CF(Antecedente_{R4}) = \max(-0.85, -0.60) = -0.60$
    *   Como el antecedente es negativo, R4 ya no se dispara. $CF(CH3) = \mathbf{0}$.

### Discusión del Comportamiento del Sistema
El cambio en una sola evidencia (E3 de -0.40 a 0.60) reestructura por completo el diagnóstico del SOC:
1.  Alerta a la regla R3, lo que eleva drásticamente la certeza de Ransomware (CH2) pasando de un $52.5\%$ a un **$69.6\%$**.
2.  Con este nuevo valor, **el Ransomware supera al DDoS (68%)**, convirtiéndose en la hipótesis principal y más crítica a mitigar.
3.  Simultáneamente, la confirmación del antivirus aplasta la evidencia a favor de una falsa alarma (pasando de 20% a 0%), haciendo que el sistema descarte cualquier posibilidad de que el tráfico anómalo sea inofensivo. El modelo matemático demostró ser altamente robusto y sensible ante nuevas evidencias críticas.
