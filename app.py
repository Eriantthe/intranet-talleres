import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="Intranet Talleres UNALM", layout="wide")

# --- 1. ESTILO VISUAL CORREGIDO ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #006b3f !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; }
    input { color: black !important; background-color: white !important; }
    
    .stDataFrame { border: 2px solid #e6e6e6; border-radius: 8px; }
    div.stButton > button:first-child { background-color: #006b3f; color: white; border-color: #006b3f; font-weight: bold; }
    
    /* Diseño para los recuadros de detalle de cada hora */
    .bloque-detalle { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #006b3f; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- 2. VARIABLES DE ESTADO ---
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "reservas" not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos", "Materiales"])

# --- 3. LÓGICA DE FECHAS (Cierre Jueves 10pm - Abre Viernes 8am) ---
tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
dia_semana = ahora.weekday() 
hora = ahora.hour

# NOTA: En False temporalmente para que puedas hacer pruebas hoy.
formulario_cerrado = False 
# if (dia_semana == 3 and hora >= 22) or (dia_semana == 4 and hora < 8):
#     formulario_cerrado = True

# --- 4. MENÚ LATERAL OCULTO ---
st.sidebar.markdown("### 🚜 Talleres y Equipos")
st.sidebar.markdown("Sistema Oficial de Separación.")
st.sidebar.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

if st.session_state.admin_mode:
    st.sidebar.success("✅ Modo Admin")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.admin_mode = False
        st.rerun()
else:
    with st.sidebar.expander("🔑 Acceso"):
        clave = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if clave == "orellana2026":
                st.session_state.admin_mode = True
                st.rerun()
            else:
                st.error("Clave incorrecta")

# ==========================================
# VISTA 1: ADMINISTRADOR
# ==========================================
if st.session_state.admin_mode:
    st.title("⚙️ Panel de Administración")
    
    opcion_admin = st.radio("Seleccione el módulo:", ["⛽ Panel de Combustible (Excel)", "🗑️ Gestionar Reservas de Profesores"])
    st.markdown("---")
    
    if opcion_admin == "⛽ Panel de Combustible (Excel)":
        st.subheader("Estado de Maquinaria en Tiempo Real")
        sheet_id = "13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        try:
            df_excel = pd.read_csv(csv_url)
            st.dataframe(df_excel, use_container_width=True)
            if 'Máquina' in df_excel.columns and 'Combustible' in df_excel.columns:
                fig = px.bar(df_excel, x="Combustible", y="Máquina", orientation='h', 
                             color="Combustible", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("⚠️ No se pudo cargar el Excel. Revisa los permisos en Drive.")
            
    elif opcion_admin == "🗑️ Gestionar Reservas de Profesores":
        st.subheader("Borrador de Reservas Activas")
        st.session_state.reservas = st.data_editor(st.session_state.reservas, num_rows="dynamic", use_container_width=True)

# ==========================================
# VISTA 2: PÚBLICA PARA PROFESORES
# ==========================================
else:
    st.title("🗓️ Separación Semanal de Ambientes y Equipos")
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.** El plazo venció el jueves a las 10:00 p.m. Se reabrirá el viernes a las 8:00 a.m.")
    else:
        st.info("✅ **SISTEMA ABIERTO.** Puede separar los requerimientos para la próxima semana.")
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        horas = ["08:00 am - 10:45 am", "11:00 am - 12:45 pm", "01:00 pm - 02:00 pm", "02:00 pm - 03:50 pm", "04:00 pm - 06:00 pm"]
        
        # MATRIZ MAIPI GENERAL
        st.subheader("📊 Disponibilidad en Tiempo Real")
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        for _, row in st.session_state.reservas.iterrows():
            matriz.at[row["Horario"], row["Día"]] = f"🔴 {row['Profesor']}"
        st.dataframe(matriz, use_container_width=True)
        st.markdown("---")
        
        # --- FORMULARIO PASO A PASO ---
        st.subheader("📝 Registrar Separación (Paso a Paso)")
        
        profesor = st.selectbox("Docente Responsable", [
            "Prof. Alfredo Rebaza Pino", "Prof. Francisco Rojas Alejandro", 
            "Prof. Juvenal García Armas", "Prof. Luis Altamirano Chunga", 
            "Prof. Fredy Cáceres Guerrero", "Prof. Augusto Zingg Rosell", "Prof. Margarita Chevarría"
        ])
        
        st.markdown("##### 1. Elija los Días de Práctica")
        dias_sel = st.multiselect("Seleccione uno o varios días:", dias)
        
        horas_por_dia = {}
        if dias_sel:
            st.markdown("##### 2. Asigne los Horarios para cada Día elegido")
            cols_dias = st.columns(len(dias_sel))
            for idx, d in enumerate(dias_sel):
                with cols_dias[idx]:
                    horas_por_dia[d] = st.multiselect(f"Horas para el {d}:", horas, key=f"h_{d}")
        
        # --- SECCIÓN DINÁMICA POR CADA HORA ELEGIDA ---
        reservas_temporales = []
        
        if dias_sel and any(horas_por_dia.values()):
            st.markdown("---")
            st.markdown("##### 3. Detalles Específicos por Bloque Horario")
            st.write("Especifique qué ambientes y equipos usará en cada hora (puede pedir cosas distintas en el mismo día).")
            
            for d in dias_sel:
                for h in horas_por_dia.get(d, []):
                    # Barra visual para separar las horas
                    st.markdown(f'<div class="bloque-detalle">🗓️ {d} | ⏰ {h}</div>', unsafe_allow_html=True)
                    
                    col_a, col_e = st.columns(2)
                    with col_a:
                        amb = st.multiselect("Ambientes", ["Motores", "Pool", "Patio", "Rejas", "Campo", "Metalmecánica", "Soldadura"], key=f"amb_{d}_{h}")
                    with col_e:
                        eq = st.multiselect("Equipos", ["NH TD5.80", "NH TD90", "NH TD5.100", "JD 3050B", "Retroexcavadora NH B110B", "MAQUETA MOTOR"], key=f"eq_{d}_{h}")
                    mat = st.text_input("Materiales extra", key=f"mat_{d}_{h}", placeholder="Ej. Sembradoras al voleo...")
                    
                    reservas_temporales.append({
                        "Día": d, "Horario": h, "Profesor": profesor.split(" ")[1], 
                        "Ambientes": ", ".join(amb) if amb else "(Ninguno)", 
                        "Equipos": ", ".join(eq) if eq else "(Ninguno)",
                        "Materiales": mat if mat else "(Ninguno)"
                    })
                    st.write("") # Espaciador
            
            # --- PREVISUALIZACIÓN TIPO HORARIO REAL ---
            st.markdown("---")
            st.markdown("### 👁️ Previsualización de su Horario")
            st.info("Así quedará su horario registrado en la cuadrícula de la semana:")
            
            # Crear una tabla visual vacía
            df_horario_visual = pd.DataFrame(index=horas, columns=dias)
            df_horario_visual.fillna("", inplace=True)
            
            # Llenar la tabla solo con las elecciones de este profesor
            for res in reservas_temporales:
                texto_celda = f"Ambiente: {res['Ambientes']}\nEquipo: {res['Equipos']}"
                df_horario_visual.at[res["Horario"], res["Día"]] = texto_celda
                
            st.table(df_horario_visual)
            
            # BOTÓN DE CONFIRMACIÓN
            if st.button("✅ Confirmar Separación Definitiva", use_container_width=True):
                cruces = []
                for res in reservas_temporales:
                    if "🔴" in matriz.at[res["Horario"], res["Día"]]:
                        cruces.append(f"{res['Día']} a las {res['Horario']}")
                
                if cruces:
                    st.error(f"⚠️ **Cruce detectado:** Los bloques ya fueron tomados: {', '.join(cruces)}.")
                else:
                    st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame(reservas_temporales)], ignore_index=True)
                    st.success("✅ ¡Horario registrado exitosamente en el MAIPI!")
                    st.rerun()
