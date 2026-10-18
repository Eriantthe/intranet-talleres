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
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE FECHAS Y CIERRE ---
tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
dia_semana = ahora.weekday() 
hora = ahora.hour

# NOTA: Está en "False" temporalmente para que puedas hacer pruebas este fin de semana.
# Cuando quieras que el bloqueo funcione, borra el "False" y descomenta las líneas de abajo.
formulario_cerrado = False 
# if dia_semana == 3 and hora >= 22:
#     formulario_cerrado = True
# elif dia_semana == 4 and hora < 8:
#     formulario_cerrado = True

if "reservas" not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos"])

# --- 3. MENÚ OCULTO ---
st.sidebar.markdown("### 🚜 Talleres y Equipos")
st.sidebar.markdown("Sistema Oficial de Separación de Ambientes.")
st.sidebar.markdown("---")
clave_secreta = st.sidebar.text_input("Acceso Admin", type="password", help="Exclusivo Jefatura")

# ==========================================
# VISTA DE ADMINISTRADOR (CLAVE: orellana2026)
# ==========================================
if clave_secreta == "orellana2026":
    st.title("⚙️ Panel de Administración")
    st.success("Modo Administrador Activo.")
    
    tab1, tab2 = st.tabs(["⛽ Combustible (Excel)", "🗑️ Gestionar Reservas"])
    
    with tab1:
        st.subheader("Estado de Maquinaria en Tiempo Real")
        # Conexión directa a tu Excel de Google Sheets
        sheet_id = "13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        try:
            df_excel = pd.read_csv(csv_url)
            st.dataframe(df_excel, use_container_width=True)
            
            # Si tu Excel tiene columnas llamadas 'Máquina' y 'Combustible', generamos el gráfico:
            if 'Máquina' in df_excel.columns and 'Combustible' in df_excel.columns:
                fig = px.bar(df_excel, x="Combustible", y="Máquina", orientation='h', 
                             color="Combustible", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning("⚠️ No se pudo leer el Excel. Asegúrate de que el enlace del Google Sheet tenga los permisos en: 'Cualquier usuario con el enlace puede leer'.")
            
    with tab2:
        st.subheader("Editar o Eliminar Reservas")
        st.markdown("Haz clic en cualquier celda para editarla. Selecciona una fila a la izquierda y presiona la tecla `Suprimir` (Delete) para borrar un registro de prueba.")
        # Editor interactivo que actualiza los datos en vivo
        st.session_state.reservas = st.data_editor(st.session_state.reservas, num_rows="dynamic", use_container_width=True)

# ==========================================
# VISTA PÚBLICA PARA PROFESORES
# ==========================================
else:
    st.title("🗓️ Separación Semanal de Ambientes y Equipos")
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.** El plazo para separar equipos venció el jueves a las 10:00 p.m.")
    else:
        st.info("✅ **SISTEMA ABIERTO.** Puede separar en bloque para la próxima semana.")
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        horas = ["08:00 am - 10:45 am", "11:00 am - 12:45 pm", "01:00 pm - 02:00 pm", "02:00 pm - 03:50 pm", "04:00 pm - 06:00 pm"]
        
        # MATRIZ MAIPI
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        for _, row in st.session_state.reservas.iterrows():
            matriz.at[row["Horario"], row["Día"]] = f"🔴 {row['Profesor']}"
            
        st.dataframe(matriz, use_container_width=True)
        
        # FORMULARIO DE SELECCIÓN MÚLTIPLE
        st.subheader("📝 Registrar Separación")
        with st.form("registro_docentes"):
            profesor = st.selectbox("Docente Responsable", [
                "Prof. Alfredo Rebaza Pino", "Prof. Francisco Rojas Alejandro", 
                "Prof. Juvenal García Armas", "Prof. Luis Altamirano Chunga", 
                "Prof. Fredy Cáceres Guerrero", "Prof. Augusto Zingg Rosell", "Prof. Margarita Chevarría"
            ])
            
            st.markdown("---")
            st.markdown("**Seleccione todos los días y horarios que requiera en una sola tanda:**")
            col_d, col_h = st.columns(2)
            with col_d:
                dias_sel = st.multiselect("Días de Práctica", dias)
            with col_h:
                horas_sel = st.multiselect("Horarios de Práctica", horas)
                
            st.markdown("---")
            col_a, col_e = st.columns(2)
            with col_a:
                ambientes = st.multiselect("Ambientes requeridos", ["Motores", "Pool", "Patio", "Rejas", "Campo", "Metalmecánica", "Soldadura"])
            with col_e:
                equipos = st.multiselect("Equipos requeridos", ["NH TD5.80", "NH TD90", "NH TD5.100", "JD 3050B", "Retroexcavadora NH B110B", "MAQUETA MOTOR"])
            
            materiales = st.text_area("¿Qué materiales o herramientas aparte necesitará?")
            enviado = st.form_submit_button("Confirmar Separación Múltiple")
            
            if enviado:
                if not dias_sel or not horas_sel:
                    st.error("⚠️ Debe seleccionar al menos un día y un horario.")
                else:
                    cruces = []
                    # Revisar si hay cruces antes de guardar
                    for d in dias_sel:
                        for h in horas_sel:
                            if "🔴" in matriz.at[h, d]:
                                cruces.append(f"{d} a las {h}")
                    
                    if cruces:
                        st.error(f"⚠️ **Cruce detectado:** Los siguientes bloques ya están ocupados: {', '.join(cruces)}. Desmárquelos e intente de nuevo.")
                    else:
                        # Guardar todas las combinaciones en bloque
                        nuevas_filas = []
                        for d in dias_sel:
                            for h in horas_sel:
                                nuevas_filas.append({
                                    "Día": d, "Horario": h, "Profesor": profesor.split(" ")[1], 
                                    "Ambientes": ", ".join(ambientes), "Equipos": ", ".join(equipos)
                                })
                        st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame(nuevas_filas)], ignore_index=True)
                        st.success("✅ ¡Separación en bloque registrada exitosamente!")
                        st.rerun()
