import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="Intranet Talleres UNALM", layout="wide")

# --- 1. ESTILO VISUAL CORREGIDO ---
st.markdown("""
    <style>
    /* Fondo verde solo para la barra lateral */
    [data-testid="stSidebar"] { background-color: #006b3f !important; }
    /* Solo los textos fijos en blanco, NO el contenido de las cajas de texto */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; }
    /* Cajas de texto con letra negra y fondo blanco */
    input { color: black !important; background-color: white !important; }
    
    .stDataFrame { border: 2px solid #e6e6e6; border-radius: 8px; }
    div.stButton > button:first-child { background-color: #006b3f; color: white; border-color: #006b3f; }
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
st.sidebar.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True) # Espacio para mandarlo abajo

# Sistema de Login Oculto
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
            st.error("⚠️ No se pudo cargar el Excel. Revisa los permisos de lectura del enlace de Drive.")
            
    elif opcion_admin == "🗑️ Gestionar Reservas de Profesores":
        st.subheader("Borrador de Reservas Activas")
        st.write("Selecciona el recuadro a la izquierda de cualquier fila y presiona `Suprimir` (Delete) para borrarla.")
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
        
        # MATRIZ MAIPI
        st.subheader("📊 Disponibilidad en Tiempo Real")
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        for _, row in st.session_state.reservas.iterrows():
            matriz.at[row["Horario"], row["Día"]] = f"🔴 {row['Profesor']}"
            
        st.dataframe(matriz, use_container_width=True)
        st.markdown("---")
        
        # FORMULARIO
        st.subheader("📝 Registrar Separación")
        
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
        
        st.markdown("##### 3. Requerimientos Generales")
        col_a, col_e = st.columns(2)
        with col_a:
            ambientes = st.multiselect("Ambientes requeridos", ["Motores", "Pool", "Patio", "Rejas", "Campo", "Metalmecánica", "Soldadura"])
        with col_e:
            equipos = st.multiselect("Equipos requeridos", ["NH TD5.80", "NH TD90", "NH TD5.100", "JD 3050B", "Retroexcavadora NH B110B", "MAQUETA MOTOR"])
        
        materiales = st.text_area("¿Qué materiales, instrumentos o herramientas aparte necesitará?")
        
        # --- PREVISUALIZACIÓN TIPO HORARIO ---
        if dias_sel and any(horas_por_dia.values()):
            st.markdown("---")
            st.markdown("### 👁️ Resumen de su Horario (Previsualización)")
            st.info("Verifique el orden de su separación. Si todo es correcto, presione Confirmar en la parte inferior.")
            
            nuevas_filas = []
            
            # Construir la previsualización visual ordenada por días
            for d in dias_sel:
                horas_d = horas_por_dia.get(d, [])
                if horas_d:
                    st.markdown(f"#### 🗓️ **{d}**")
                    for h in horas_d:
                        # Se muestran los ambientes y equipos elegidos para esa hora
                        st.markdown(f"- **⏰ {h}** ➔ **Ambiente:** {', '.join(ambientes) if ambientes else 'Ninguno'} | **Equipos:** {', '.join(equipos) if equipos else 'Ninguno'}")
                    
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**🛠️ Materiales extra:** *{materiales if materiales else 'Ninguno'}*")
                    st.write("") # Espacio
                    
                    # Guardar los datos estructurados en la memoria para la tabla final
                    for h in horas_d:
                        nuevas_filas.append({
                            "Día": d, "Horario": h, "Profesor": profesor.split(" ")[1], 
                            "Ambientes": ", ".join(ambientes) if ambientes else "(Ninguno)", 
                            "Equipos": ", ".join(equipos) if equipos else "(Ninguno)",
                            "Materiales": materiales if materiales else "(Ninguno)"
                        })
            
            df_preview = pd.DataFrame(nuevas_filas)
            
            # BOTÓN FINAL DE CONFIRMACIÓN
            if st.button("Confirmar Separación"):
                cruces = []
                for _, row_prev in df_preview.iterrows():
                    if "🔴" in matriz.at[row_prev["Horario"], row_prev["Día"]]:
                        cruces.append(f"{row_prev['Día']} a las {row_prev['Horario']}")
                
                if cruces:
                    st.error(f"⚠️ **Cruce detectado:** Los bloques ya fueron tomados por otro docente: {', '.join(cruces)}.")
                else:
                    st.session_state.reservas = pd.concat([st.session_state.reservas, df_preview], ignore_index=True)
                    st.success("✅ ¡Separación registrada exitosamente en el MAIPI!")
                    st.rerun()
