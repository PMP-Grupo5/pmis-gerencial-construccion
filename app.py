import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuración de página de alta gerencia
st.set_page_config(page_title="PMIS Alta Gerencia — Construction SaaS", layout="wide", initial_sidebar_state="expanded")

# Título y Encabezado
st.title("🏗️ PMIS Alta Gerencia — Control Físico & Financiero")
st.caption("Plataforma Global de Control de Proyectos bajo el Estándar PMBOK (EVM & Gobernanza)")

# ----------------- GESTIÓN DE PROYECTOS INDEPENDIENTES -----------------
# Inicializar datos en la sesión del usuario si no existen
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = {
        "Torres del Parque (Demo)": {
            "bac": 1000.0,
            "mes_corte": 5,
            "pv_serie": [50, 120, 220, 350, 500, 650, 780, 880, 950, 1000],
            "ev_corte": 400.0,
            "ac_corte": 450.0
        }
    }

# Barra lateral para seleccionar o crear proyectos
with st.sidebar:
    st.header("⚙️ Portafolio de Proyectos")
    lista_proyectos = list(st.session_state.proyectos.keys())
    proyecto_seleccionado = st.selectbox("Selecciona tu Proyecto:", lista_proyectos)
    
    st.markdown("---")
    st.subheader("➕ Iniciar Nuevo Proyecto")
    with st.expander("Crear Proyecto Independiente"):
        nuevo_nombre = st.text_input("Nombre de la Obra:", placeholder="Ej. Edificio Horizonte")
        nuevo_bac = st.number_input("Presupuesto Total Aprobado BAC (COP M):", value=800.0, step=50.0)
        nuevo_mes_corte = st.slider("Mes de Corte Actual:", 1, 10, 3)
        nuevo_ev = st.number_input("Valor Ganado Actual EV (COP M):", value=220.0, step=10.0)
        nuevo_ac = st.number_input("Costo Real Gastado AC (COP M):", value=240.0, step=10.0)
        
        if st.button("Guardar y Activar Proyecto"):
            if nuevo_nombre.strip() != "":
                # Crear curva PV estándar proporcional al BAC
                pv_base = [nuevo_bac * (i / 10.0) for i in range(1, 11)]
                st.session_state.proyectos[nuevo_nombre] = {
                    "bac": nuevo_bac,
                    "mes_corte": nuevo_mes_corte,
                    "pv_serie": pv_base,
                    "ev_corte": nuevo_ev,
                    "ac_corte": nuevo_ac
                }
                st.success(f"¡Proyecto '{nuevo_nombre}' creado con éxito!")
                st.rerun()

# ----------------- EXTRACCIÓN DE DATOS Y MOTOR EVM -----------------
datos_prj = st.session_state.proyectos[proyecto_seleccionado]
BAC = float(datos_prj["bac"])
mes_corte = int(datos_prj["mes_corte"])
pv_serie = datos_prj["pv_serie"]
PV_actual = float(pv_serie[mes_corte - 1])
EV_actual = float(datos_prj["ev_corte"])
AC_actual = float(datos_prj["ac_corte"])

# Fórmulas oficiales de Gestión del Valor Ganado (PMBOK)
CV = EV_actual - AC_actual
SV = EV_actual - PV_actual
CPI = EV_actual / AC_actual if AC_actual > 0 else 1.0
SPI = EV_actual / PV_actual if PV_actual > 0 else 1.0
EAC = BAC / CPI if CPI > 0 else BAC
ETC = max(0.0, EAC - AC_actual)
VAC = BAC - EAC
TCPI = (BAC - EV_actual) / (BAC - AC_actual) if (BAC - AC_actual) > 0 else 1.0

# ----------------- SEMÁFORO DE GOBERNANZA -----------------
if CPI >= 1.0 and SPI >= 1.0:
    st.success(f"🟢 **SEMÁFORO VERDE: Rendimiento Saludable** — Proyecto '{proyecto_seleccionado}' operando dentro de la línea base.")
elif CPI >= 0.90 and SPI >= 0.90:
    st.warning(f"🟡 **SEMÁFORO AMARILLO: Alerta Preventiva** — Desviación moderada detectada. Convoque comité de control de cuadrillas.")
else:
    st.error(f"🔴 **SEMÁFORO ROJO: Desviación Crítica** — Sobrecosto o retraso severo (CPI: {CPI:.2f} | SPI: {SPI:.2f}). Se requiere trámite de control integrado de cambios.")

# ----------------- TARJETAS EJECUTIVAS -----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Índice de Costo (CPI)", f"{CPI:.2f}", f"CV: {CV:+.1f} M COP", delta_color="normal")
col2.metric("Índice de Cronograma (SPI)", f"{SPI:.2f}", f"SV: {SV:+.1f} M COP", delta_color="normal")
col3.metric("Estimado al Cierre (EAC)", f"${EAC:,.1f} M", f"VAC: {VAC:+.1f} M COP", delta_color="inverse")
col4.metric("Desempeño Restante (TCPI)", f"{TCPI:.2f}", f"Meta: BAC (${BAC:,.0f} M)", delta_color="inverse")

st.markdown("---")

# ----------------- CURVA S INTERACTIVA (PLOTLY) -----------------
meses = [f"Mes {i}" for i in range(1, 11)]
meses_ext = meses + ["Mes 11", "Mes 12"]

# Proyección de serie histórica y pronóstico
ev_serie = [pv_serie[i] * (EV_actual / PV_actual) for i in range(mes_corte)]
ac_serie = [pv_serie[i] * (AC_actual / PV_actual) for i in range(mes_corte)]
eac_serie = [None] * (mes_corte - 1) + [AC_actual] + [AC_actual + (ETC * (i / (12 - mes_corte))) for i in range(1, 13 - mes_corte)]

fig = go.Figure()
# Línea Base (PV)
fig.add_trace(go.Scatter(x=meses, y=pv_serie, mode='lines+markers', name='Valor Planificado (PV)', line=dict(color='gray', dash='dash')))
# Valor Ganado (EV)
fig.add_trace(go.Scatter(x=meses[:mes_corte], y=ev_serie, mode='lines+markers', name='Valor Ganado (EV)', line=dict(color='#2563eb', width=3)))
# Costo Real (AC)
fig.add_trace(go.Scatter(x=meses[:mes_corte], y=ac_serie, mode='lines+markers', name='Costo Real (AC)', line=dict(color='#dc2626', width=3)))
# Pronóstico (EAC)
fig.add_trace(go.Scatter(x=meses_ext[mes_corte-1:], y=eac_serie[mes_corte-1:], mode='lines+markers', name='Pronóstico al Cierre (EAC)', line=dict(color='#d97706', dash='dot', width=2)))

fig.update_layout(
    title=f"Curva S de Desempeño Acumulado — {proyecto_seleccionado}",
    xaxis_title="Línea de Tiempo",
    yaxis_title="COP Millones",
    hovermode="x unified",
    template="plotly_white",
    height=450
)
st.plotly_chart(fig, use_container_width=True)

# ----------------- CENTRO DE GOBERNANZA & MITIGACIÓN -----------------
st.subheader("🛠️ Acciones de Mitigación y Gobernanza")
b1, b2, b3 = st.columns(3)

with b1:
    if st.button("⚡ Simular Crashing / Fast-tracking"):
        st.info("💡 **Compresión de Cronograma:** Se evalúa jornada extendida en la ruta crítica para recuperar el desfase del SPI.")
with b2:
    if st.button("🛡️ Solicitar Reserva de Contingencia"):
        st.warning("📋 **Gestión Financiera:** Solicitud radicada ante el patrocinador para liberar reserva de costos imprevistos.")
with b3:
    if st.button("📑 Exportar Acta de Comité PMO"):
        st.success(f"📄 **Gobernanza:** Informe de estado compilado exitosamente para '{proyecto_seleccionado}'.")
