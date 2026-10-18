import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz

st.set_page_config(page_title="Intranet Talleres UNALM", layout="wide")

# --- 1. ESTILO VISUAL (VERDE UNALM) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #006b3f !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stDataFrame { border: 2px solid #e6e6e6; border-radius: 8px; }
    /* Darle un color destacado al boton principal */
    div.stButton > button:first-child { background-color: #006b3f; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE FECHAS Y CIERRE ---
tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
dia_semana = ahora.weekday() 
hora = ahora.hour

# NOTA: Está en "False" temporalmente para que puedas hacer pruebas este fin de semana.
# Cuando quieras que el bloqueo funcione, borra el "False" y descomenta las dos líneas de abajo.
formulario_cerrado = False 
# if (dia_semana == 3 and hora >= 22) or (dia_semana == 4 and hora < 8):
#     formulario_cerrado = True

if "reservas" not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos", "Materiales"])

# --- 3. MENÚ OCULTO ---
st.sidebar.markdown("### 🚜 Talleres y Equipos")
st.sidebar.markdown("Sistema Oficial de Separación.")
st.sidebar.markdown("---")
clave_secreta = st.sidebar.text_input("Acceso Admin", type="password", help="Exclusivo Jefatura")

# ==========================================
# VISTA DE ADMINISTRADOR (CLAVE: orellana2026)
# ==========================================
if clave_secreta == "orellana2026":
    st.title("⚙️ Panel de Administración")
    st.success("Modo Administrador Activo.")
    
    # Reemplazamos los tabs por botones de radio para evitar errores de renderizado
    opcion_admin = st.radio("Navegación Admin:", ["⛽ Panel de Combustible (Excel)", "🗑️ Gestionar Reservas de Profesores"])
    st.markdown("---")
    
    if opcion_admin == "⛽ Panel de Combustible (Excel)":
        st.subheader("Estado de Maquinaria en Tiempo Real")
        sheet_id = "13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        try:
            df_excel = pd.read_csv(csv_url)
            st.dataframe(df_excel, use_container_width=True)
            
            # Generar gráfico solo si las columnas existen para evitar que la app colapse
            if 'Máquina' in df_excel.columns and 'Combustible' in df_excel.columns:
                fig = px.bar(df_excel, x="Combustible", y="Máquina", orientation='h', 
                             color="Combustible", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("⚠️ No se pudo cargar el Excel. Asegúrate de que el archivo de Google Sheets tenga los permisos en 'Cualquier usuario con el enlace puede leer'.")
            
    elif opcion_admin == "🗑️ Gestionar Reservas de Profesores":
        st.subheader("Borrador de Reservas Activas")
        st.write("Selecciona el recuadro a la izquierda de cualquier fila y presiona `Suprimir` (Delete) en tu teclado para borrarla.")
        if not st.session_state.reservas.empty:
            st.session_state.reservas = st.data_editor(st.session_state.reservas, num_rows="dynamic", use_container_width=True)
        else:
            st.info("Aún no hay reservas registradas en la memoria temporal.")

# ==========================================
# VISTA PÚBLICA PARA PROFESORES
# ==========================================
elif clave_secreta != "" and clave_secreta != "orellana2026":
    st.error("❌ Clave incorrecta.")
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
        
        # FORMULARIO REACTIVO (Muestra opciones dinámicamente)
        st.subheader("📝 Registrar Separación")
        
        profesor = st.selectbox("Docente Responsable", [
            "Prof. Alfredo Rebaza Pino", "Prof. Francisco Rojas Alejandro", 
            "Prof. Juvenal García Armas", "Prof. Luis Altamirano Chunga", 
            "Prof. Fredy Cáceres Guerrero", "Prof. Augusto Zingg Rosell", "Prof. Margarita Chevarría"
        ])
        
        st.markdown("##### 1. Elija los Días de Práctica")
        dias_sel = st.multiselect("Seleccione uno o varios días:", dias)
        
        # Generar selectores de hora ESPECÍFICOS para cada día seleccionado
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
        
        # SISTEMA DE PREVISUALIZACIÓN EN VIVO
        if dias_sel and any(horas_por_dia.values()):
            st.markdown("---")
            st.markdown("### 👁️ Previsualización de su Reserva")
            st.info("Revise su resumen. Si todo es correcto, presione Confirmar.")
            
            nuevas_filas = []
            for d in dias_sel:
                for h in horas_por_dia.get(d, []):
                    nuevas_filas.append({
                        "Día": d, "Horario": h, "Profesor": profesor.split(" ")[1], 
                        "Ambientes": ", ".join(ambientes) if ambientes else "(Ninguno)", 
                        "Equipos": ", ".join(equipos) if equipos else "(Ninguno)",
                        "Materiales": materiales if materiales else "(Ninguno)"
                    })
            
            df_preview = pd.DataFrame(nuevas_filas)
            st.dataframe(df_preview, use_container_width=True)
            
            # BOTÓN FINAL DE CONFIRMACIÓN
            if st.button("Confirmar Separación"):
                cruces = []
                for _, row_prev in df_preview.iterrows():
                    if "🔴" in matriz.at[row_prev["Horario"], row_prev["Día"]]:
                        cruces.append(f"{row_prev['Día']} a las {row_prev['Horario']}")
                
                if cruces:
                    st.error(f"⚠️ **Cruce detectado:** Los siguientes bloques ya fueron tomados por otro docente: {', '.join(cruces)}. Desmárquelos e intente de nuevo.")
                else:
                    st.session_state.reservas = pd.concat([st.session_state.reservas, df_preview], ignore_index=True)
                    st.success("✅ ¡Separación en bloque registrada exitosamente en el MAIPI!")
                    st.rerun()
