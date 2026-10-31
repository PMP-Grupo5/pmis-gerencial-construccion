import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Configuración inicial de la página
st.set_page_config(
    page_title="PMIS Híbrido — Torres del Parque & ObraCheck",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para replicar el diseño de las referencias
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 16px;
    }
    .goal-box {
        background-color: #f8fafc;
        border-left: 4px solid #1e3a8a;
        padding: 12px 18px;
        border-radius: 4px;
        font-size: 14px;
        color: #1e293b;
        margin-bottom: 20px;
    }
    .kpi-container {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        text-align: left;
    }
    .kpi-title {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-val {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 12px;
        color: #64748b;
    }
    .kanban-col {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        min-height: 480px;
    }
    .kanban-header {
        font-size: 12px;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
    }
    .kanban-card {
        background: white;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        border-left: 3px solid #3b82f6;
    }
    .card-meta {
        font-size: 11px;
        color: #64748b;
        margin-bottom: 4px;
    }
    .card-title {
        font-size: 12px;
        color: #1e293b;
        font-weight: 500;
        line-height: 1.35;
        margin-bottom: 8px;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #475569;
    }
    .badge-pts {
        background: #1e293b;
        color: white;
        padding: 2px 6px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- BASE DE DATOS MULTIPROYECTO HÍBRIDA (SESSION STATE) -----------------
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = {
        "Torres del Parque (Híbrido: Obra + ObraCheck)": {
            "tipo": "Híbrido",
            "componente_predictivo": {
                "bac": 1000.0,
                "mes_corte": 5,
                "pv_serie": [50, 120, 220, 350, 500, 650, 780, 880, 950, 1000],
                "ev_corte": 400.0,
                "ac_corte": 450.0
            },
            "componente_adaptativo": {
                "nombre_app": "App móvil de inspección de calidad en obra («ObraCheck»)",
                "sprint_actual": 5,
                "duracion_dias": 6,
                "dia_sprint": 3,
                "meta_sprint": "«Un residente puede registrar una no conformidad con foto y ubicación, asignarla y cerrarla desde el celular, aunque no haya señal»",
                "wip_limite": 3,
                "velocidades_historicas": [24, 27, 30, 29],
                "historias_sprint": [
                    {"id": "H27", "epica": "E4 Reportes", "titulo": "Como director quiero ver un tablero con hallazgos abiertos por contratista", "responsable": "Jessica", "pts": 2, "estado": "Por Hacer"},
                    {"id": "H28", "epica": "E5 Administración", "titulo": "Como administrador quiero crear usuarios y roles para controlar el acceso", "responsable": "Andrés", "pts": 2, "estado": "Por Hacer"},
                    {"id": "H24", "epica": "E3 Seguimiento", "titulo": "Como inspector quiero asignar la no conformidad a un contratista para que la corrija", "responsable": "Andrés", "pts": 5, "estado": "En Curso"},
                    {"id": "H25", "epica": "E3 Seguimiento", "titulo": "Como director de obra quiero recibir un correo cuando se cierre un hallazgo crítico", "responsable": "Laura", "pts": 3, "estado": "En Curso"},
                    {"id": "H26", "epica": "E3 Seguimiento", "titulo": "Como inspector quiero cerrar un hallazgo con foto de evidencia para liberar el área", "responsable": "Miguel", "pts": 3, "estado": "En Curso"},
                    {"id": "H23", "epica": "E2 Offline", "titulo": "Como residente quiero trabajar sin conexión para no perder datos en el sótano", "responsable": "Jessica", "pts": 5, "estado": "En Revisión"},
                    {"id": "H21", "epica": "E1 Registro", "titulo": "Como residente quiero registrar una no conformidad con foto para documentarla en el sitio", "responsable": "Laura - Mar", "pts": 5, "estado": "Hecho"},
                    {"id": "H22", "epica": "E1 Registro", "titulo": "Como residente quiero marcar la ubicación en el plano del piso para localizar el hallazgo", "responsable": "Miguel - Mié", "pts": 5, "estado": "Hecho"}
                ],
                "product_backlog": [
                    {"id": "H31", "epica": "E4 Reportes", "historia": "Exportar informe PDF por torre", "pts_100": 20, "moscow": "M (Debe)", "pts": 8},
                    {"id": "H32", "epica": "E2 Offline", "historia": "Plantillas de lista de chequeo por actividad", "pts_100": 18, "moscow": "M (Debe)", "pts": 13},
                    {"id": "H33", "epica": "E3 Seguimiento", "historia": "Firma digital del interventor", "pts_100": 15, "moscow": "S (Debería)", "pts": 8},
                    {"id": "H34", "epica": "E2 Offline", "historia": "Sincronización en segundo plano", "pts_100": 12, "moscow": "S (Debería)", "pts": 13},
                    {"id": "H35", "epica": "E4 Reportes", "historia": "Integración con cronograma de obra", "pts_100": 10, "moscow": "C (Podría)", "pts": 21},
                    {"id": "H36", "epica": "E5 Administración", "historia": "Modo oscuro", "pts_100": 2, "moscow": "W (No por ahora)", "pts": 3}
                ]
            }
        }
    }

# ----------------- BARRA LATERAL: MULTIPROYECTO & CONFIGURACIÓN -----------------
with st.sidebar:
    st.header("⚙️ Portafolio de Proyectos")
    lista_proyectos = list(st.session_state.proyectos.keys())
    proyecto_seleccionado = st.selectbox("Selecciona tu Proyecto:", lista_proyectos)
    
    st.markdown("---")
    st.subheader("➕ Iniciar Nuevo Proyecto Híbrido")
    with st.expander("Crear Proyecto Independiente"):
        n_nombre = st.text_input("Nombre de la Obra:", placeholder="Ej. Hospital Modular Metropolitano")
        n_bac = st.number_input("Presupuesto Físico BAC (COP M):", value=1200.0, step=50.0)
        n_app = st.text_input("Nombre Componente Digital:", value="Módulo de Calidad & Trazabilidad")
        n_meta = st.text_area("Meta del Sprint 1:", value="«Desplegar formulario de captura con validación de geocerca en sitio»")
        
        if st.button("Guardar y Activar Proyecto"):
            if n_nombre.strip() != "":
                pv_base = [n_bac * (i / 10.0) for i in range(1, 11)]
                st.session_state.proyectos[n_nombre] = {
                    "tipo": "Híbrido",
                    "componente_predictivo": {
                        "bac": n_bac,
                        "mes_corte": 3,
                        "pv_serie": pv_base,
                        "ev_corte": n_bac * 0.28,
                        "ac_corte": n_bac * 0.30
                    },
                    "componente_adaptativo": {
                        "nombre_app": n_app,
                        "sprint_actual": 1,
                        "duracion_dias": 6,
                        "dia_sprint": 2,
                        "meta_sprint": n_meta,
                        "wip_limite": 3,
                        "velocidades_historicas": [20, 22, 25],
                        "historias_sprint": [
                            {"id": "H01", "epica": "E1 Core", "titulo": "Crear esquema de base de datos relacional", "responsable": "Carlos", "pts": 5, "estado": "Hecho"},
                            {"id": "H02", "epica": "E1 Core", "titulo": "Configurar interfaz de usuario en AppSheet", "responsable": "Ana", "pts": 8, "estado": "En Curso"},
                            {"id": "H03", "epica": "E2 Geo", "titulo": "Captura de coordenadas GPS en segundo plano", "responsable": "Jorge", "pts": 5, "estado": "Por Hacer"}
                        ],
                        "product_backlog": [
                            {"id": "H04", "epica": "E3 Reportes", "historia": "Exportar PDF de bitácora diaria", "pts_100": 30, "moscow": "M (Debe)", "pts": 5},
                            {"id": "H05", "epica": "E4 Alertas", "historia": "Notificación push de hallazgos críticos", "pts_100": 20, "moscow": "S (Debería)", "pts": 8}
                        ]
                    }
                }
                st.success(f"¡Proyecto '{n_nombre}' creado con éxito!")
                st.rerun()

# Cargar datos del proyecto activo
prj = st.session_state.proyectos[proyecto_seleccionado]
pred = prj["componente_predictivo"]
adapt = prj["componente_adaptativo"]

# ----------------- NAVEGACIÓN POR PESTAÑAS (ENFOQUE HÍBRIDO PMBOK) -----------------
tab_agil, tab_predictivo, tab_backlog, tab_alimentar = st.tabs([
    "🚀 Componente Ágil (ObraCheck / Sprint)", 
    "🏛️ Componente Predictivo (Obra Civil & Curva S)",
    "📋 Backlog Priorizado (100 pts / MoSCoW)",
    "📥 Alimentar / Mover Actividades"
])

# =====================================================================================
# PESTAÑA 1: COMPONENTE ÁGIL (TABLERO KANBAN, BURNDOWN, VELOCIDAD)
# =====================================================================================
with tab_agil:
    st.markdown(f"<div class='main-header'>Proyecto ágil: {adapt['nombre_app']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Demo de clase · Sprint {adapt['sprint_actual']} de 1 semana (lunes a sábado) · arrastre o mueva tarjetas entre columnas y cambie el día del sprint</div>", unsafe_allow_html=True)

    # Controles superiores: Barra de día del Sprint y botones
    c_dia, c_btn1, c_btn2 = st.columns([3, 1, 1])
    with c_dia:
        dia_nombres = ["Lun (día 1 de 6)", "Mar (día 2 de 6)", "Mié (día 3 de 6)", "Jue (día 4 de 6)", "Vie (día 5 de 6)", "Sáb (día 6 de 6)"]
        dia_sel = st.slider("Día del sprint:", min_value=1, max_value=6, value=adapt["dia_sprint"], format="%d")
        adapt["dia_sprint"] = dia_sel
        dia_texto = dia_nombres[dia_sel - 1]
        st.caption(f"**Día actual:** {dia_texto}")
    with c_btn1:
        st.write("")
        st.write("")
        if st.button("▶ Simular el sprint", use_container_width=True):
            st.info("Simulación: Avance dinámico de 5 puntos en historias en curso.")
    with c_btn2:
        st.write("")
        st.write("")
        if st.button("Reiniciar datos", use_container_width=True):
            st.rerun()

    # Meta del Sprint
    st.markdown(f"<div class='goal-box'><strong>Meta del Sprint {adapt['sprint_actual']}:</strong> {adapt['meta_sprint']}</div>", unsafe_allow_html=True)

    # Métricas de cabecera ágil
    historias = adapt["historias_sprint"]
    pts_compromiso = sum(h["pts"] for h in historias)
    pts_terminado = sum(h["pts"] for h in historias if h["estado"] == "Hecho")
    pts_restante = pts_compromiso - pts_terminado
    pct_terminado = int((pts_terminado / pts_compromiso) * 100) if pts_compromiso > 0 else 0
    wip_actual = sum(1 for h in historias if h["estado"] == "En Curso")
    wip_limite = adapt["wip_limite"]
    
    # Cálculo ideal de puntos restantes según el día del sprint
    ideal_hoy = max(0.0, round(pts_compromiso - ((pts_compromiso / 6.0) * dia_sel), 1))
    
    # Velocidad promedio y sprints restantes
    vel_promedio = float(np.mean(adapt["velocidades_historicas"]))
    total_pts_backlog = sum(b["pts"] for b in adapt["product_backlog"])
    sprints_restantes = round(total_pts_backlog / vel_promedio, 1) if vel_promedio > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Compromiso</div><div class='kpi-val'>{pts_compromiso} pts</div><div class='kpi-sub'>{len(historias)} historias en Sprint</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Terminado</div><div class='kpi-val' style='color:#16a34a;'>{pts_terminado} pts</div><div class='kpi-sub'>{pct_terminado}% del compromiso</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Restante</div><div class='kpi-val'>{pts_restante} pts</div><div class='kpi-sub'>ideal hoy: {ideal_hoy}</div></div>""", unsafe_allow_html=True)
    with k4:
        color_wip = "#dc2626" if wip_actual > wip_limite else "#0f172a"
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>WIP</div><div class='kpi-val' style='color:{color_wip};'>{wip_actual}</div><div class='kpi-sub'>límite {wip_limite}</div></div>""", unsafe_allow_html=True)
    with k5:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Impedimentos</div><div class='kpi-val' style='color:#16a34a;'>0</div><div class='kpi-sub'>ninguno abierto</div></div>""", unsafe_allow_html=True)
    with k6:
        st.markdown(f"""<div class='kpi-container'><div class='kpi-title'>Sprints restantes</div><div class='kpi-val'>≈ {int(np.ceil(sprints_restantes))}</div><div class='kpi-sub'>según velocidad {vel_promedio:.1f}</div></div>""", unsafe_allow_html=True)

    st.write("")
    
    # ----------------- TABLERO KANBAN CON LÍMITE WIP -----------------
    st.markdown(f"##### Tablero kanban – Sprint Backlog (límite WIP en «En curso» configurable = {wip_limite})")
    
    col_todo, col_inprog, col_review, col_done = st.columns(4)
    
    estados = ["Por Hacer", "En Curso", "En Revisión", "Hecho"]
    cols_gui = [col_todo, col_inprog, col_review, col_done]
    
    for idx, est in enumerate(estados):
        with cols_gui[idx]:
            items = [h for h in historias if h["estado"] == est]
            pts_col = sum(h["pts"] for h in items)
            count_col = len(items)
            
            # Alerta visual si se excede el WIP en 'En Curso'
            wip_badge = ""
            if est == "En Curso" and count_col > wip_limite:
                wip_badge = " <span style='color:#dc2626; font-weight:800;'>[¡WIP EXCEDIDO!]</span>"
            
            st.markdown(f"""
            <div class='kanban-header'>
                <span>{est.upper()}{wip_badge}</span>
                <span>{count_col} · {pts_col} PTS</span>
            </div>
            """, unsafe_allow_html=True)
            
            for h in items:
                st.markdown(f"""
                <div class='kanban-card'>
                    <div class='card-meta'>{h['id']} · {h['epica']}</div>
                    <div class='card-title'>{h['titulo']}</div>
                    <div class='card-footer'>
                        <span>👤 {h['responsable']}</span>
                        <span class='badge-pts'>{h['pts']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    # ----------------- BURNDOWN Y VELOCIDAD ÁGIL (REFERENCIA 2) -----------------
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.subheader("Gráfica de Trabajo Pendiente (Burndown del Sprint)")
        dias_eje = ["Plan", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        linea_ideal = [30.0, 25.0, 20.0, 15.0, 10.0, 5.0, 0.0]
        # Línea real construida dinámicamente hasta el día seleccionado
        linea_real = [30.0]
        if dia_sel >= 1: linea_real.append(28.0)
        if dia_sel >= 2: linea_real.append(25.0)
        if dia_sel >= 3: linea_real.append(float(pts_restante))
        for d in range(4, dia_sel + 1):
            linea_real.append(max(0.0, float(pts_restante - (d * 2))))
            
        fig_burn = go.Figure()
        fig_burn.add_trace(go.Scatter(x=dias_eje, y=linea_ideal, mode='lines', name='Ideal', line=dict(color='gray', dash='dash')))
        fig_burn.add_trace(go.Scatter(x=dias_eje[:len(linea_real)], y=linea_real, mode='lines+markers', name='Real', line=dict(color='#0d9488', width=3)))
        fig_burn.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Días de la iteración", yaxis_title="Puntos restantes", hovermode="x unified")
        st.plotly_chart(fig_burn, use_container_width=True)
        
        dif_atraso = pts_restante - ideal_hoy
        if dif_atraso > 0:
            st.caption(f"⚠️ Restan {pts_restante} puntos; el ideal para hoy es {ideal_hoy}. Hay atraso de {dif_atraso:.1f} puntos: revise impedimentos y el trabajo en curso (WIP).")
        else:
            st.caption(f"✅ Ritmo saludable: el avance real está en o por delante de la línea ideal.")

    with g_col2:
        st.subheader("Velocidad del Equipo por Sprint")
        sprints_nombres = ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", f"Sprint {adapt['sprint_actual']}"]
        vel_valores = adapt["velocidades_historicas"] + [pts_terminado]
        colores_barras = ['#2563eb', '#2563eb', '#2563eb', '#2563eb', '#d97706']
        
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Bar(x=sprints_nombres, y=vel_valores, marker_color=colores_barras, name='Puntos'))
        fig_vel.add_hline(y=vel_promedio, line_dash="dash", line_color="gray", annotation_text=f"Promedio {vel_promedio:.1f}")
        fig_vel.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Iteraciones", yaxis_title="Puntos de historia entregados")
        st.plotly_chart(fig_vel, use_container_width=True)
        
        st.caption(f"Con velocidad promedio de {vel_promedio:.1f} puntos/sprint, los {total_pts_backlog} puntos restantes del backlog requieren ≈ {sprints_restantes:.0f} sprints.")

# =====================================================================================
# PESTAÑA 2: COMPONENTE PREDICTIVO (CURVA S, EVM, GOBERNANZA)
# =====================================================================================
with tab_predictivo:
    st.markdown("<div class='main-header'>Componente Predictivo: Control Físico & Financiero de Obra Civil</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Línea Base del Desempeño (PMB) · Valor Ganado (EVM) · Curva S acumulada (COP Millones)</div>", unsafe_allow_html=True)
    
    BAC = float(pred["bac"])
    mes_corte = int(pred["mes_corte"])
    pv_serie = pred["pv_serie"]
    PV = float(pv_serie[mes_corte - 1])
    EV = float(pred["ev_corte"])
    AC = float(pred["ac_corte"])
    
    # Fórmulas oficiales EVM
    CV = EV - AC
    SV = EV - PV
    CPI = EV / AC if AC > 0 else 1.0
    SPI = EV / PV if PV > 0 else 1.0
    EAC = BAC / CPI if CPI > 0 else BAC
    ETC = max(0.0, EAC - AC)
    VAC = BAC - EAC
    TCPI = (BAC - EV) / (BAC - AC) if (BAC - AC) > 0 else 1.0
    
    # Semáforo de Gobernanza
    if CPI >= 1.0 and SPI >= 1.0:
        st.success(f"🟢 **SEMÁFORO VERDE: Rendimiento Saludable** — Obra civil operando bajo control (CPI: {CPI:.2f} | SPI: {SPI:.2f}).")
    elif CPI >= 0.90 and SPI >= 0.90:
        st.warning(f"🟡 **SEMÁFORO AMARILLO: Alerta Preventiva** — Desviación moderada (CPI: {CPI:.2f} | SPI: {SPI:.2f}). Rebalancear cuadrillas.")
    else:
        st.error(f"🔴 **SEMÁFORO ROJO: Desviación Crítica** — Atraso o sobrecosto severo (CPI: {CPI:.2f} | SPI: {SPI:.2f}). Escalar a Comité PMO.")

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Índice de Costo (CPI)", f"{CPI:.2f}", f"CV: {CV:+.1f} M COP", delta_color="normal")
    p2.metric("Índice de Cronograma (SPI)", f"{SPI:.2f}", f"SV: {SV:+.1f} M COP", delta_color="normal")
    p3.metric("Estimado al Cierre (EAC)", f"${EAC:,.1f} M", f"VAC: {VAC:+.1f} M COP", delta_color="inverse")
    p4.metric("Desempeño Restante (TCPI)", f"{TCPI:.2f}", f"Meta: BAC (${BAC:,.0f} M)", delta_color="inverse")

    st.write("")
    
    # Curva S Acumulada
    meses = [f"Mes {i}" for i in range(1, 11)]
    meses_ext = meses + ["Mes 11", "Mes 12"]
    ev_serie = [pv_serie[i] * (EV / PV) for i in range(mes_corte)]
    ac_serie = [pv_serie[i] * (AC / PV) for i in range(mes_corte)]
    eac_serie = [None] * (mes_corte - 1) + [AC] + [AC + (ETC * (i / (12 - mes_corte))) for i in range(1, 13 - mes_corte)]

    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(x=meses, y=pv_serie, mode='lines+markers', name='Valor Planificado (PV)', line=dict(color='gray', dash='dash')))
    fig_s.add_trace(go.Scatter(x=meses[:mes_corte], y=ev_serie, mode='lines+markers', name='Valor Ganado (EV)', line=dict(color='#2563eb', width=3)))
    fig_s.add_trace(go.Scatter(x=meses[:mes_corte], y=ac_serie, mode='lines+markers', name='Costo Real (AC)', line=dict(color='#dc2626', width=3)))
    fig_s.add_trace(go.Scatter(x=meses_ext[mes_corte-1:], y=eac_serie[mes_corte-1:], mode='lines+markers', name='Pronóstico al Cierre (EAC)', line=dict(color='#d97706', dash='dot', width=2)))

    fig_s.update_layout(
        title=f"Curva S de Desempeño Acumulado — {proyecto_seleccionado}",
        xaxis_title="Línea de Tiempo",
        yaxis_title="COP Millones",
        hovermode="x unified",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_s, use_container_width=True)

# =====================================================================================
# PESTAÑA 3: BACKLOG PRIORIZADO (MÉTODO 100 PUNTOS & MoSCoW - REFERENCIA 2)
# =====================================================================================
with tab_backlog:
    st.markdown("<div class='main-header'>Backlog del producto restante</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Priorizado mediante asignación de 100 Puntos y categorización MoSCoW (PMBOK 8.ª Edición)</div>", unsafe_allow_html=True)

    df_backlog = pd.DataFrame(adapt["product_backlog"])
    st.dataframe(
        df_backlog.rename(columns={
            "id": "ID",
            "epica": "Épica",
            "historia": "Historia",
            "pts_100": "100 pts (Valor)",
            "moscow": "MoSCoW",
            "pts": "Puntos de Historia"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.info("💡 **Criterio de Priorización PMP:** Las historias 'Debe (M)' concentran el mayor peso en la técnica de 100 puntos y se planifican en las iteraciones más tempranas para mitigar riesgos técnicos.")

# =====================================================================================
# PESTAÑA 4: ALIMENTAR Y MOVER ACTIVIDADES (CAMBIOS Y GESTIÓN)
# =====================================================================================
with tab_alimentar:
    st.markdown("<div class='main-header'>Centro de Control Operativo y Actualización</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Mueve historias de usuario en el Kanban o actualiza el avance de la obra civil</div>", unsafe_allow_html=True)

    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.subheader("🔄 Mover Historia en el Tablero Kanban")
        hist_ids = [f"{h['id']} — {h['titulo'][:40]}..." for h in adapt["historias_sprint"]]
        sel_hist = st.selectbox("Selecciona la historia:", hist_ids)
        hist_id_pura = sel_hist.split(" ")[0]
        
        nuevo_estado = st.selectbox("Mover a la columna:", ["Por Hacer", "En Curso", "En Revisión", "Hecho"])
        
        if st.button("Actualizar Tablero Kanban"):
            for h in adapt["historias_sprint"]:
                if h["id"] == hist_id_pura:
                    h["estado"] = nuevo_estado
                    st.success(f"Historia {hist_id_pura} movida a '{nuevo_estado}'")
                    st.rerun()

    with f_col2:
        st.subheader("⚙️ Configuración del Flujo Ágil")
        nuevo_wip = st.number_input("Límite WIP en «En Curso»:", min_value=1, max_value=10, value=adapt["wip_limite"])
        if st.button("Guardar Límite WIP"):
            adapt["wip_limite"] = int(nuevo_wip)
            st.success(f"Límite WIP actualizado a {nuevo_wip}")
            st.rerun()

        st.markdown("---")
        st.subheader("🏗️ Actualizar Corte de Obra Civil (EVM)")
        n_ev = st.number_input("Nuevo EV Acumulado (COP M):", value=float(pred["ev_corte"]), step=10.0)
        n_ac = st.number_input("Nuevo AC Acumulado (COP M):", value=float(pred["ac_corte"]), step=10.0)
        if st.button("Guardar Datos de Obra Civil"):
            pred["ev_corte"] = n_ev
            pred["ac_corte"] = n_ac
            st.success("Líneas de Valor Ganado y Costo Real actualizadas.")
            st.rerun()
# Historias iniciales del Sprint Backlog
st.session_state.historias = [
    {"id": "H21", "epica": "E1 Registro", "titulo": "Como residente quiero registrar...", "puntos": 5, "estado": "Hecho", "responsable": "Laura"},
    {"id": "H24", "epica": "E3 Seguimiento", "titulo": "Como inspector quiero asignar...", "puntos": 5, "estado": "En curso", "responsable": "Andrés"},
    ...
]
