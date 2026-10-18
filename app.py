import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

# Configurar zona horaria de Perú para el cierre automático
tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)

st.set_page_config(page_title="Intranet Talleres", layout="wide")

# --- MENÚ LATERAL ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e6/Escudo_UNALM.png", width=100)
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["🗓️ Reserva de Docentes", "⛽ Panel de Fluidos (Privado)"])

# ==========================================
# SECCIÓN 1: PROFESORES (PÚBLICO)
# ==========================================
if opcion == "🗓️ Reserva de Docentes":
    st.title("Separación Semanal de Ambientes y Equipos")
    st.markdown("Por favor, llene este formulario para separar sus equipos.")
    
    # Lógica de cierre: Jueves es el día 3 (Lunes es 0).
    # Bloquear si es Jueves (3) después de las 22:00, o Viernes (4), Sábado (5), Domingo (6).
    es_jueves_tarde = ahora.weekday() == 3 and ahora.hour >= 22
    fin_de_semana = ahora.weekday() in [4, 5, 6]
    
    if es_jueves_tarde or fin_de_semana:
        st.error("🔒 **FORMULARIO CERRADO.** El plazo máximo para separar equipos vence todos los jueves a las 10:00 p.m.")
    else:
        st.info("✅ El formulario está abierto para la próxima semana.")
        with st.form("registro_docentes"):
            col1, col2 = st.columns(2)
            with col1:
                profesor = st.selectbox("Docente", ["Prof. Alfredo Rebaza", "Prof. Francisco Rojas", "Prof. Juvenal García", "Prof. Luis Altamirano", "Prof. Fredy Cáceres", "Prof. Augusto Zingg", "Prof. Margarita Chevarría"])
                semana = st.text_input("Semana de solicitud (Ej. 08 semana del 26-Oct al 30-Oct)")
                dia = st.selectbox("Día de Práctica", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
            with col2:
                hora = st.selectbox("Horario", ["08:00 am - 10:45 am", "11:00 am - 12:45 pm", "01:00 pm - 02:00 pm", "02:00 pm - 03:50 pm", "04:00 pm - 06:00 pm"])
                ambientes = st.multiselect("Ambientes", ["Motores", "Pool", "Patio", "Rejas", "Campo", "Metalmecánica", "Soldadura"])
                equipos = st.text_input("Equipos (Ej. NH TD5.80, JD 3050B...)")
            
            materiales = st.text_area("¿Qué materiales o instrumentos aparte necesitará?")
            enviado = st.form_submit_button("Enviar Reserva")
            
            if enviado:
                st.success("Reserva registrada correctamente. (Aquí conectaremos con tu Google Sheets luego)")

# ==========================================
# SECCIÓN 2: ADMIN (PRIVADO CON CLAVE)
# ==========================================
elif opcion == "⛽ Panel de Fluidos (Privado)":
    st.title("Panel de Registro de Máquinas y Fluidos")
    
    # Sistema de contraseña
    st.sidebar.markdown("---")
    clave = st.sidebar.text_input("Clave de Administrador", type="password")
    
    if clave == "orellana2026": # Puedes cambiar esta contraseña por la que quieras
        st.success("Acceso Autorizado")
        
        # Dashboard Gráfico de ejemplo
        st.subheader("Nivel de Combustible por Tractor (%)")
        
        # Estos datos luego los jalaremos de tu excel
        datos_fluidos = pd.DataFrame({
            "Máquina": ["NH TD5.80", "NH TD90", "NH TD5.100", "JD 3050B", "Retroexcavadora"],
            "Combustible (%)": [85, 40, 90, 15, 60]
        })
        
        # Colores: Rojo si es menor a 25%, Verde si está bien
        colores = ['red' if x < 25 else 'green' for x in datos_fluidos['Combustible (%)']]
        fig = px.bar(datos_fluidos, x="Combustible (%)", y="Máquina", orientation='h', 
                     color="Combustible (%)", color_continuous_scale="RdYlGn", range_x=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        
    elif clave != "":
        st.error("❌ Clave incorrecta.")
