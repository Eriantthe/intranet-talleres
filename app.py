import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="Intranet Talleres UNALM", layout="wide")

# --- 1. ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #006b3f !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; }
    input { color: black !important; background-color: white !important; }
    div.stButton > button:first-child { background-color: #006b3f; color: white; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. VARIABLES DE ESTADO Y LISTAS EXACTAS DEL FORMULARIO ---
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "reservas" not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos", "Materiales"])

tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
# (En False temporalmente para pruebas)
formulario_cerrado = False 

dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
horas_form = ["8:00am a 9:00 am", "9:00 am a 10:45 am", "11:00am a 12:00pm", "12:00pm a 12:45pm", "2:00pm a 3:00pm", "3:00pm a 3:50pm"]
ambientes_form = ["Soldadura", "Metalmecánica", "Motores", "Pool", "Patio", "Rejas", "Campo"]
equipos_form = ["Ningún Equipo en particular", "NH TD5.80", "NH TD5.100", "NH TD90", "JD 3050B", "JD 1040", "NH B110B", "NH L223", "SOLD ELECTRODO MANUAL", "SOLD OXI", "SOLD TIG", "SOLD MIG/MAG", "TORNO", "FRESADORA", "ESMERIL", "PRENSA HIDRAULICA", "REMACHADORA", "FRAGUA", "MAQUETA MOTOR"]

# Funciones para crear cuadriculas vacías de checkboxes
def crear_matriz_vacia(columnas):
    return pd.DataFrame(False, index=dias, columns=columnas)

# --- 3. MENÚ LATERAL OCULTO ---
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
        if st.button("Entrar") and clave == "orellana2026":
            st.session_state.admin_mode = True
            st.rerun()

# ==========================================
# VISTA 1: ADMINISTRADOR
# ==========================================
if st.session_state.admin_mode:
    st.title("⚙️ Panel de Administración")
    opcion_admin = st.radio("Seleccione el módulo:", ["⛽ Panel de Combustible (Excel)", "🗑️ Gestionar Reservas"])
    
    if opcion_admin == "⛽ Panel de Combustible (Excel)":
        st.subheader("Estado de Maquinaria")
        csv_url = f"https://docs.google.com/spreadsheets/d/13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM/export?format=csv"
        try:
            df_excel = pd.read_csv(csv_url)
            st.dataframe(df_excel, use_container_width=True)
            if 'Máquina' in df_excel.columns and 'Combustible' in df_excel.columns:
                fig = px.bar(df_excel, x="Combustible", y="Máquina", orientation='h', color="Combustible", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("⚠️ No se pudo cargar el Excel.")
            
    elif opcion_admin == "🗑️ Gestionar Reservas":
        st.session_state.reservas = st.data_editor(st.session_state.reservas, num_rows="dynamic", use_container_width=True)

# ==========================================
# VISTA 2: PÚBLICA PARA PROFESORES
# ==========================================
else:
    st.title("🗓️ Separación Semanal de Ambientes y Equipos")
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.**")
    else:
        st.info("✅ **SISTEMA ABIERTO.** Marque las casillas tal como lo hacía en el formulario anterior.")
        
        # MATRIZ MAIPI GENERAL (Solo lectura)
        st.subheader("📊 Disponibilidad Actual (MAIPI)")
        matriz_disp = pd.DataFrame(index=horas_form, columns=dias)
        matriz_disp.fillna("🟢 Libre", inplace=True)
        for _, row in st.session_state.reservas.iterrows():
            matriz_disp.at[row["Horario"], row["Día"]] = f"🔴 {row['Profesor']}"
        st.dataframe(matriz_disp, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📝 Registrar Separación")
        
        profesor = st.selectbox("Docente Responsable", ["Prof. Alfredo Rebaza Pino", "Prof. Francisco Rojas Alejandro", "Prof. Juvenal García Armas", "Prof. Luis Altamirano Chunga", "Prof. Fredy Cáceres Guerrero", "Prof. Augusto Zingg Rosell", "Prof. Margarita Chevarría"])
        
        # CUADRÍCULAS INTERACTIVAS (Igual a Google Forms)
        st.markdown("#### 1. Horario de Prácticas")
        st.write("Marque las horas que utilizará cada día:")
        df_h = st.data_editor(crear_matriz_vacia(horas_form), use_container_width=True)
        
        st.markdown("#### 2. Qué ambientes necesitará")
        st.write("Marque los ambientes que ocupará cada día:")
        df_a = st.data_editor(crear_matriz_vacia(ambientes_form), use_container_width=True)
        
        st.markdown("#### 3. ¿Qué equipos necesitará?")
        st.write("Deslice hacia la derecha para ver todas las herramientas y máquinas:")
        df_e = st.data_editor(crear_matriz_vacia(equipos_form), use_container_width=True)
        
        st.markdown("#### 4. Materiales adicionales")
        materiales = st.text_area("Redactar. ¿Qué materiales, instrumentos o herramientas aparte necesitará para completar su práctica?")
        
        # PROCESAR DATOS DE LAS CUADRÍCULAS
        reservas_temporales = []
        for d in dias:
            horas_seleccionadas = df_h.columns[df_h.loc[d]].tolist()
            ambientes_seleccionados = df_a.columns[df_a.loc[d]].tolist()
            equipos_seleccionados = df_e.columns[df_e.loc[d]].tolist()
            
            for h in horas_seleccionadas:
                reservas_temporales.append({
                    "Día": d, "Horario": h, "Profesor": profesor.split(" ")[1], 
                    "Ambientes": ", ".join(ambientes_seleccionados) if ambientes_seleccionados else "(Ninguno)", 
                    "Equipos": ", ".join(equipos_seleccionados) if equipos_seleccionados else "(Ninguno)",
                    "Materiales": materiales if materiales else "(Ninguno)"
                })
        
        if st.button("✅ Confirmar Separación", use_container_width=True):
            if not reservas_temporales:
                st.error("⚠️ Debe seleccionar al menos un horario en la primera cuadrícula.")
            else:
                cruces = []
                for res in reservas_temporales:
                    if "🔴" in matriz_disp.at[res["Horario"], res["Día"]]:
                        cruces.append(f"{res['Día']} a las {res['Horario']}")
                
                if cruces:
                    st.error(f"⚠️ **Cruce detectado:** Los bloques ya fueron tomados por otro docente: {', '.join(cruces)}.")
                else:
                    st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame(reservas_temporales)], ignore_index=True)
                    st.success("✅ ¡Horario registrado exitosamente!")
                    st.rerun()
