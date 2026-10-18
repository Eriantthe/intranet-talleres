import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="Intranet Talleres UNALM", layout="wide")

# 1. ESTILO VISUAL (VERDE UNALM Y MAIPI)
st.markdown("""
    <style>
    /* Color Verde UNALM para la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #006b3f !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Darle formato a la tabla para que parezca el MAIPI */
    .stDataFrame {
        border: 2px solid #e6e6e6;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. LÓGICA DE FECHAS (HORA DE LIMA)
tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
dia_semana = ahora.weekday() # 0=Lunes, 3=Jueves, 4=Viernes
hora = ahora.hour

# El sistema cierra estrictamente el Jueves a las 10pm y abre el Viernes a las 8am
formulario_cerrado = False
if dia_semana == 3 and hora >= 22:
    formulario_cerrado = True
elif dia_semana == 4 and hora < 8:
    formulario_cerrado = True

# Guardado temporal de reservas para que funcione la vista en vivo
if "reservas" not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos"])

# 3. SISTEMA OCULTO PARA EL ING. ORELLANA Y PARA TI
st.sidebar.markdown("### 🚜 Talleres y Equipos")
st.sidebar.markdown("Sistema Oficial de Separación de Ambientes.")
st.sidebar.markdown("---")

# Campo camuflado: Los profesores pensarán que es solo un login genérico
clave_secreta = st.sidebar.text_input("Acceso Admin", type="password", help="Exclusivo Jefatura")

# SI SE INGRESA LA CLAVE CORRECTA -> APARECE EL PANEL DE FLUIDOS
if clave_secreta == "orellana2026":
    st.title("⛽ Panel de Control de Maquinaria y Fluidos")
    st.success("✅ Acceso Autorizado. Modo Administrador Activo.")
    
    # Gráfico interactivo de combustible
    datos_fluidos = pd.DataFrame({
        "Máquina": ["NH TD5.80", "NH TD90", "NH TD5.100", "JD 3050B", "Retroexcavadora NH B110B"],
        "Combustible (%)": [85, 40, 90, 15, 60]
    })
    
    colores = ['red' if x < 25 else 'green' for x in datos_fluidos['Combustible (%)']]
    fig = px.bar(datos_fluidos, x="Combustible (%)", y="Máquina", orientation='h', 
                 color="Combustible (%)", color_continuous_scale="RdYlGn", range_x=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

# SI LA CLAVE ESTÁ VACÍA O ES INCORRECTA -> APARECE LA VISTA DE DOCENTES
else:
    st.title("🗓️ Separación Semanal de Ambientes y Equipos")
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.** El plazo para separar equipos de la próxima semana venció el jueves a las 10:00 p.m. El sistema se reabrirá automáticamente el viernes a las 8:00 a.m.")
    else:
        st.info("✅ **SISTEMA ABIERTO.** Puede separar los requerimientos para la próxima semana.")
        
        # --- MATRIZ INTERACTIVA ESTILO MAIPI ---
        st.subheader("📊 Disponibilidad en Tiempo Real")
        st.markdown("Revise la cuadrícula antes de reservar. Si el bloque está en **🔴 Ocupado**, deberá coordinar o elegir otro horario.")
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        horas = ["08:00 am - 10:45 am", "11:00 am - 12:45 pm", "01:00 pm - 02:00 pm", "02:00 pm - 03:50 pm", "04:00 pm - 06:00 pm"]
        
        # Crear la tabla base
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        
        # Pintar la matriz con las reservas hechas
        for _, row in st.session_state.reservas.iterrows():
            matriz.at[row["Horario"], row["Día"]] = f"🔴 Ocupado: {row['Profesor']} ({row['Ambientes']})"
            
        st.dataframe(matriz, use_container_width=True)
        
        st.markdown("---")
        
        # --- FORMULARIO OFICIAL BASADO EN TU GOOGLE FORMS ---
        st.subheader("📝 Registrar Separación")
        with st.form("registro_docentes"):
            col1, col2 = st.columns(2)
            with col1:
                profesor = st.selectbox("Docente Responsable", [
                    "Prof. Alfredo Rebaza Pino", "Prof. Francisco Rojas Alejandro", 
                    "Prof. Juvenal García Armas", "Prof. Luis Altamirano Chunga", 
                    "Prof. Fredy Cáceres Guerrero", "Prof. Augusto Zingg Rosell", 
                    "Prof. Margarita Chevarría"
                ])
                dia = st.selectbox("Día de Práctica", dias)
                hora = st.selectbox("Horario de Práctica", horas)
            with col2:
                ambientes = st.multiselect("Ambientes requeridos", [
                    "Motores", "Pool", "Patio", "Rejas", "Campo", "Metalmecánica", "Soldadura"
                ])
                equipos = st.multiselect("Equipos requeridos", [
                    "NH TD5.80", "NH TD90", "NH TD5.100", "JD 3050B", 
                    "Retroexcavadora NH B110B", "MAQUETA MOTOR"
                ])
            
            materiales = st.text_area("¿Qué materiales, instrumentos o herramientas aparte necesitará para completar su práctica?")
            enviado = st.form_submit_button("Confirmar Separación")
            
            if enviado:
                # Validar cruce estilo MAIPI
                if "🔴 Ocupado" in matriz.at[hora, dia]:
                    st.error(f"⚠️ **Cruce de Horarios:** El día {dia} en el bloque de {hora} ya fue separado. Revise la tabla superior.")
                else:
                    nueva_reserva = {
                        "Día": dia, "Horario": hora, "Profesor": profesor.split(" ")[1], # Solo el apellido
                        "Ambientes": ", ".join(ambientes), "Equipos": ", ".join(equipos)
                    }
                    st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame([nueva_reserva])], ignore_index=True)
                    st.success("✅ ¡Separación registrada exitosamente!")
                    st.rerun() # Actualiza la pantalla para que la celda se pinte de rojo al instante
