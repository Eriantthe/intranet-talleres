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
    
    .stDataFrame { border: 2px solid #e6e6e6; border-radius: 8px; }
    div.stButton > button:first-child { background-color: #006b3f; color: white; border-color: #006b3f; font-weight: bold; }
    
    .bloque-dia { background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 15px; border-left: 6px solid #006b3f; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    .titulo-dia { font-size: 18px; font-weight: bold; color: #006b3f; margin-bottom: 10px;}
    
    .bloque-hora { background-color: #ffffff; padding: 12px; border-radius: 5px; margin-top: 15px; margin-bottom: 5px; border-left: 4px solid #4CAF50; border: 1px solid #dcdcdc;}
    .titulo-hora { font-size: 15px; font-weight: bold; color: #333333; margin-bottom: 8px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. VARIABLES Y DATOS OFICIALES ---
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "reservas" not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos", "Materiales"])

tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
formulario_cerrado = False 

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
horas = ["08:00 am - 09:50 am", "11:00 am - 12:50 pm", "02:00 pm - 03:50 pm", "04:00 pm - 05:50 pm"]

ambientes_opciones = ["Soldadura", "Metalmecánica", "Motores", "Pool", "Patio", "Rejas", "Campo"]
equipos_opciones = ["Ningún Equipo en particular", "NH TD5.80", "NH TD5.100", "NH TD90", "JD 3050B", "JD 1040", "NH B110B", "NH L223", "SOLD ELECTRODO MANUAL", "SOLD OXI", "SOLD TIG", "SOLD MIG/MAG", "TORNO", "FRESADORA", "ESMERIL", "PRENSA HIDRAULICA", "REMACHADORA", "FRAGUA", "MAQUETA MOTOR"]

# Lista oficial de docentes
profesores_lista = [
    "ROJAS ALEJANDRO, FRANCISCO", "GARCIA ARMAS, JUVENAL", "ALTAMIRANO CHUNGA, LUIS",
    "CACERES GUERRERO, FREDY", "CHEVARRIA MOSCOSO, MARGARITA", "REBAZA PINO, ALFREDO",
    "ZINGG ROSELL, AUGUSTO", "VASQUEZ CACERES, JAIME", "ORELLANA PARDAVE, JOSE",
    "SALAS PEÑA, CARLO", "RUBIO VALLE, ALEXIS", "YARIN ACHACHAGUA, ANWAR", "SALAS PINTO, DIONISIO"
]

# Paleta de colores para cada profesor
colores_prof = {
    "ROJAS ALEJANDRO, FRANCISCO": "#D7BDE2", "GARCIA ARMAS, JUVENAL": "#A3E4D7",
    "ALTAMIRANO CHUNGA, LUIS": "#FAD7A0", "CACERES GUERRERO, FREDY": "#F9E79F",
    "CHEVARRIA MOSCOSO, MARGARITA": "#F5B7B1", "REBAZA PINO, ALFREDO": "#B4CDE6",
    "ZINGG ROSELL, AUGUSTO": "#C5E0B4", "VASQUEZ CACERES, JAIME": "#D2B4DE",
    "ORELLANA PARDAVE, JOSE": "#AED6F1", "SALAS PEÑA, CARLO": "#F5CBA7",
    "RUBIO VALLE, ALEXIS": "#A9DFBF", "YARIN ACHACHAGUA, ANWAR": "#FADBD8",
    "SALAS PINTO, DIONISIO": "#E6B0AA"
}

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
    
    opcion_admin = st.radio("Seleccione el módulo:", ["⛽ Panel de Combustible", "🗑️ Gestionar Reservas", "🖨️ Exportar Horario"])
    st.markdown("---")
    
    if opcion_admin == "⛽ Panel de Combustible":
        st.subheader("Estado de Maquinaria en Tiempo Real")
        sheet_id = "13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        try:
            df_excel = pd.read_csv(csv_url)
            st.dataframe(df_excel, use_container_width=True)
            if 'Máquina' in df_excel.columns and 'Combustible' in df_excel.columns:
                fig = px.bar(df_excel, x="Combustible", y="Máquina", orientation='h', color="Combustible", color_continuous_scale="RdYlGn")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("⚠️ No se pudo cargar el Excel. Revisa los permisos en Drive.")
            
    elif opcion_admin == "🗑️ Gestionar Reservas":
        st.subheader("Borrador de Reservas Activas")
        st.session_state.reservas = st.data_editor(st.session_state.reservas, num_rows="dynamic", use_container_width=True)
        
    elif opcion_admin == "🖨️ Exportar Horario":
        st.subheader("Generar Horario Coloreado para PDF")
        st.write("Visualiza el horario codificado por colores según cada docente. Haz clic en el botón inferior para descargarlo y guardarlo como PDF.")
        
        # Generar código HTML del horario
        html_table = """
        <html><head><meta charset="utf-8">
        <style>
            table { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 12px; }
            th { background-color: #006b3f; color: white; border: 1px solid #000; padding: 10px; text-align: center; }
            td { border: 1px solid #000; padding: 8px; vertical-align: top; width: 16%; }
            .hora { background-color: #f2f2f2; font-weight: bold; text-align: center; vertical-align: middle; }
        </style></head><body>
        <h2 style="text-align: center; color: #006b3f; font-family: Arial;">CRONOGRAMA DE USO DE TALLERES Y EQUIPOS</h2>
        <table><tr><th>Hora</th>
        """
        for d in dias:
            html_table += f"<th>{d}</th>"
        html_table += "</tr>"
        
        for h in horas:
            html_table += f"<tr><td class='hora'>{h}</td>"
            for d in dias:
                # Buscar reserva para este día y hora
                reserva = st.session_state.reservas[(st.session_state.reservas["Día"] == d) & (st.session_state.reservas["Horario"] == h)]
                if not reserva.empty:
                    contenido = ""
                    bg_color = "#ffffff"
                    for _, r in reserva.iterrows():
                        prof = r["Profesor"]
                        bg_color = colores_prof.get(prof, "#ffffff")
                        contenido += f"<b>{prof}</b><br><i>Ambientes:</i> {r['Ambientes']}<br><i>Equipos:</i> {r['Equipos']}<br><hr style='margin:4px 0;'>"
                    html_table += f"<td style='background-color: {bg_color};'>{contenido}</td>"
                else:
                    html_table += "<td></td>"
            html_table += "</tr>"
            
        html_table += "</table></body></html>"
        
        # Mostrar el horario en la página
        st.components.v1.html(html_table, height=600, scrolling=True)
        
        # Botón para descargar
        st.download_button(
            label="📄 Descargar Horario para Imprimir (PDF)",
            data=html_table,
            file_name="Horario_Coloreado_Talleres.html",
            mime="text/html"
        )

# ==========================================
# VISTA 2: PÚBLICA PARA PROFESORES
# ==========================================
else:
    st.title("🗓️ Separación Semanal de Ambientes y Equipos")
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.** El plazo venció el jueves a las 10:00 p.m. Se reabrirá el viernes a las 8:00 a.m.")
    else:
        st.info("✅ **SISTEMA ABIERTO.** Siga los pasos para separar sus requerimientos de la próxima semana.")
        
        st.subheader("📊 Disponibilidad en Tiempo Real")
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        for _, row in st.session_state.reservas.iterrows():
            matriz.at[row["Horario"], row["Día"]] = f"🔴 Ocupado"
        st.dataframe(matriz, use_container_width=True)
        st.markdown("---")
        
        st.subheader("📝 Registrar Separación")
        
        profesor = st.selectbox("Docente Responsable", profesores_lista)
        
        st.markdown("##### 1. Elija los Días de Práctica")
        dias_sel = st.multiselect("Seleccione los días que desea separar:", dias)
        
        reservas_temporales = []
        
        if dias_sel:
            st.markdown("##### 2. Requerimientos por Bloque Horario")
            
            for d in dias_sel:
                st.markdown(f'<div class="bloque-dia"><div class="titulo-dia">🗓️ {d.upper()}</div>', unsafe_allow_html=True)
                
                h_sel = st.multiselect(f"⏰ Seleccione los horarios que utilizará el {d}:", horas, key=f"h_{d}")
                
                if h_sel:
                    for h in h_sel:
                        st.markdown(f'<div class="bloque-hora"><div class="titulo-hora">⏱️ Requerimientos para el bloque: {h}</div>', unsafe_allow_html=True)
                        
                        col_a, col_e = st.columns(2)
                        with col_a:
                            a_sel = st.multiselect(f"🏢 Ambientes", ambientes_opciones, key=f"a_{d}_{h}")
                        with col_e:
                            e_sel = st.multiselect(f"🚜 Equipos", equipos_opciones, key=f"e_{d}_{h}")
                        
                        m_sel = st.text_input(f"🛠️ Materiales extra", placeholder="Ej. Sembradoras...", key=f"m_{d}_{h}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        reservas_temporales.append({
                            "Día": d, "Horario": h, "Profesor": profesor, 
                            "Ambientes": ", ".join(a_sel) if a_sel else "(Ninguno)", 
                            "Equipos": ", ".join(e_sel) if e_sel else "(Ninguno)",
                            "Materiales": m_sel if m_sel else "(Ninguno)"
                        })
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            if reservas_temporales:
                st.markdown("---")
                st.markdown("### 👁️ Previsualización de su Horario")
                
                df_horario_visual = pd.DataFrame(index=horas, columns=dias)
                df_horario_visual.fillna("", inplace=True)
                
                for res in reservas_temporales:
                    texto_celda = f"Ambiente: {res['Ambientes']}\nEquipo: {res['Equipos']}"
                    df_horario_visual.at[res["Horario"], res["Día"]] = texto_celda
                    
                st.table(df_horario_visual)
                
                if st.button("✅ Confirmar Separación Definitiva", use_container_width=True):
                    cruces = []
                    for res in reservas_temporales:
                        if "🔴" in matriz.at[res["Horario"], res["Día"]]:
                            cruces.append(f"{res['Día']} a las {res['Horario']}")
                    
                    if cruces:
                        st.error(f"⚠️ **Cruce detectado:** Los siguientes bloques ya fueron tomados por otro profesor: {', '.join(cruces)}.")
                    else:
                        st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame(reservas_temporales)], ignore_index=True)
                        st.success("✅ ¡Horario registrado exitosamente en el MAIPI!")
                        st.rerun()
