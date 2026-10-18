import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pytz
import time
import requests
import json

# === PEGA TU ENLACE QUE TERMINA EN /exec AQUÍ ABAJO ===
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbxihm1pF6Z3bJ5LaHIGTv8m-HFDEl1B3hgWemaeS4W4tWbwI0wGvbx6lF7YScjTWkOL/exec"
# ========================================================

st.set_page_config(page_title="Intranet Talleres UNALM", layout="wide")

# --- FUNCIONES DE BASE DE DATOS (NUBE) ---
def cargar_reservas():
    try:
        r = requests.get(URL_APPS_SCRIPT, timeout=10)
        data = r.json()
        if len(data) > 0:
            return pd.DataFrame(data)
    except Exception as e:
        st.sidebar.error("Problema de conexión con Google Sheets.")
    return pd.DataFrame(columns=["Día", "Horario", "Profesor", "Ambientes", "Equipos", "Materiales"])

def guardar_reservas_en_nube(df):
    try:
        registros = df.to_dict(orient='records')
        payload = {"action": "save", "reservas": registros}
        requests.post(URL_APPS_SCRIPT, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, timeout=10)
        return True
    except:
        return False

# --- VARIABLES DE ESTADO ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "form_key" not in st.session_state: st.session_state.form_key = 0

# Carga las reservas reales desde tu pestaña "reservas" del Excel
if "reservas" not in st.session_state or st.session_state.reservas.empty:
    st.session_state.reservas = cargar_reservas()

tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
dias_para_lunes = 7 - ahora.weekday()
lunes_obj = ahora + timedelta(days=dias_para_lunes)
str_semana = f"Semana del {lunes_obj.strftime('%d/%m')} al {(lunes_obj + timedelta(days=4)).strftime('%d/%m')}"

formulario_cerrado = False 

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
horas = ["08:00 am - 09:50 am", "11:00 am - 12:50 pm", "02:00 pm - 03:50 pm", "04:00 pm - 05:50 pm"]
ambientes_opciones = ["Soldadura", "Metalmecánica", "Motores", "Pool", "Patio", "Rejas", "Campo"]
equipos_opciones = ["Ningún Equipo en particular", "NH TD5.80", "NH TD5.100", "NH TD90", "JD 3050B", "JD 1040", "NH B110B", "NH L223", "SOLD ELECTRODO MANUAL", "SOLD OXI", "SOLD TIG", "SOLD MIG/MAG", "TORNO", "FRESADORA", "ESMERIL", "PRENSA HIDRAULICA", "REMACHADORA", "FRAGUA", "MAQUETA MOTOR"]
profesores_lista = ["ROJAS ALEJANDRO, FRANCISCO", "GARCIA ARMAS, JUVENAL", "ALTAMIRANO CHUNGA, LUIS", "CACERES GUERRERO, FREDY", "CHEVARRIA MOSCOSO, MARGARITA", "REBAZA PINO, ALFREDO", "ZINGG ROSELL, AUGUSTO", "VASQUEZ CACERES, JAIME", "ORELLANA PARDAVE, JOSE", "SALAS PEÑA, CARLO", "RUBIO VALLE, ALEXIS", "YARIN ACHACHAGUA, ANWAR", "SALAS PINTO, DIONISIO"]
colores_prof = {"ROJAS ALEJANDRO, FRANCISCO": "#D7BDE2", "GARCIA ARMAS, JUVENAL": "#A3E4D7", "ALTAMIRANO CHUNGA, LUIS": "#FAD7A0", "CACERES GUERRERO, FREDY": "#F9E79F", "CHEVARRIA MOSCOSO, MARGARITA": "#F5B7B1", "REBAZA PINO, ALFREDO": "#B4CDE6", "ZINGG ROSELL, AUGUSTO": "#C5E0B4", "VASQUEZ CACERES, JAIME": "#D2B4DE", "ORELLANA PARDAVE, JOSE": "#AED6F1", "SALAS PEÑA, CARLO": "#F5CBA7", "RUBIO VALLE, ALEXIS": "#A9DFBF", "YARIN ACHACHAGUA, ANWAR": "#FADBD8", "SALAS PINTO, DIONISIO": "#E6B0AA"}

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #006b3f !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; }
    [data-testid="stSidebar"] label p { color: white !important; }
    input { color: black !important; background-color: white !important; }
    .stDataFrame { border: 2px solid #e6e6e6; border-radius: 8px; }
    div.stButton > button:first-child { background-color: #006b3f; color: white; border-color: #006b3f; font-weight: bold; }
    .bloque-dia { background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin-top: 15px; margin-bottom: 15px; border-left: 6px solid #006b3f;}
    .titulo-dia { font-size: 18px; font-weight: bold; color: #006b3f; margin-bottom: 10px;}
    .bloque-hora { background-color: #ffffff; padding: 12px; border-radius: 5px; margin-top: 15px; margin-bottom: 5px; border-left: 4px solid #4CAF50; border: 1px solid #dcdcdc;}
    .titulo-hora { font-size: 15px; font-weight: bold; color: #333333; margin-bottom: 8px;}
    .tarjeta-fluido { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border-bottom: 5px solid #006b3f; margin-bottom: 10px;}
    .icono-fluido { font-size: 45px; margin-bottom: 5px; }
    .valor-fluido { font-size: 30px; font-weight: bold; color: #2c3e50; margin: 0; }
    .titulo-fluido { font-size: 14px; color: #7f8c8d; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;}
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
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
    opcion_admin = st.radio("Seleccione el módulo:", ["🚜 Control Visual de Maquinaria", "🗑️ Gestionar Reservas", "🖨️ Exportar Horario"])
    st.markdown("---")
    
    if opcion_admin == "🚜 Control Visual de Maquinaria":
        st.subheader("Estado de Fluidos y Horómetro en Tiempo Real")
        sheet_id = "13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM"
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=58572181"
        try:
            df_excel = pd.read_csv(csv_url)
            df_excel.columns = df_excel.columns.str.strip()
            
            # Buscador flexible de columnas (ignora tildes y mayúsculas)
            def encontrar_columna(df, opciones):
                for col in df.columns:
                    col_limpia = str(col).upper().replace('Á','A').replace('Ó','O').strip()
                    opciones_limpias = [opt.upper().replace('Á','A').replace('Ó','O').strip() for opt in opciones]
                    if col_limpia in opciones_limpias: return col
                return None
            
            # Intenta buscar varias variaciones de nombres para no fallar
            col_maq = encontrar_columna(df_excel, ['Máquina', 'Maquina', 'Equipo', 'Tractor', 'Tipo de Tractor'])
            if not col_maq and len(df_excel.columns) > 0: col_maq = df_excel.columns[0]
                
            if col_maq:
                maquinas_disponibles = df_excel[col_maq].dropna().unique()
                maquina_sel = st.selectbox("Seleccione el equipo para inspeccionar:", maquinas_disponibles)
                datos_maq = df_excel[df_excel[col_maq] == maquina_sel].iloc[0]
                
                # Función segura para extraer el número
                def limpiar_num(valor, default):
                    if pd.isna(valor): return default
                    try: return float(str(valor).replace('%', '').strip())
                    except: return default

                # Busca las columnas
                col_comb = encontrar_columna(df_excel, ['Combustible', 'Gasolina', 'Petroleo', 'Diesel', 'Registro'])
                col_refri = encontrar_columna(df_excel, ['Refrigerante', 'Agua'])
                col_aceite = encontrar_columna(df_excel, ['Aceite', 'Motor'])
                col_horo = encontrar_columna(df_excel, ['Horómetro', 'Horometro', 'Horas', 'Reloj'])

                # Extrae los valores
                val_comb = limpiar_num(datos_maq[col_comb] if col_comb else None, 75)
                val_refri = limpiar_num(datos_maq[col_refri] if col_refri else None, 90)
                val_aceite = limpiar_num(datos_maq[col_aceite] if col_aceite else None, 85)
                val_horo = str(datos_maq[col_horo]) if col_horo and not pd.isna(datos_maq[col_horo]) else "1,245.5"

                st.markdown(f"### Reporte Técnico: {maquina_sel}")
                
                # Tarjetas Visuales (Dashboard)
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.markdown(f"""
                    <div class="tarjeta-fluido">
                        <div class="icono-fluido">⛽</div>
                        <div class="titulo-fluido">Combustible (Tanque)</div>
                        <p class="valor-fluido">{int(val_comb)}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(max(int(val_comb), 0), 100) / 100)

                with c2:
                    st.markdown(f"""
                    <div class="tarjeta-fluido">
                        <div class="icono-fluido">🏺</div>
                        <div class="titulo-fluido">Refrigerante (Radiador)</div>
                        <p class="valor-fluido">{int(val_refri)}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(max(int(val_refri), 0), 100) / 100)

                with c3:
                    st.markdown(f"""
                    <div class="tarjeta-fluido">
                        <div class="icono-fluido">🛢️</div>
                        <div class="titulo-fluido">Aceite de Motor</div>
                        <p class="valor-fluido">{int(val_aceite)}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(max(int(val_aceite), 0), 100) / 100)

                with c4:
                    st.markdown(f"""
                    <div class="tarjeta-fluido">
                        <div class="icono-fluido">⏱️</div>
                        <div class="titulo-fluido">Horómetro (Reloj)</div>
                        <p class="valor-fluido">{val_horo} <span style='font-size:16px;'>hrs</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                with st.expander("Ver tabla completa de datos de Google Sheets"):
                    st.dataframe(df_excel, use_container_width=True)
            else:
                st.error("No se encontró ninguna columna válida en el Excel para identificar las máquinas.")
        except Exception:
            st.error("⚠️ No se pudo cargar el Excel de Registro. Revisa los permisos en Drive.")
            
    elif opcion_admin == "🗑️ Gestionar Reservas":
        st.subheader("Borrador de Reservas Activas")
        st.write("Marca la casilla '❌ Borrar' en las filas que desees eliminar y presiona el botón inferior para borrar de la nube.")
        df_admin = st.session_state.reservas.copy()
        df_admin.insert(0, "❌ Borrar", False)
        df_editado = st.data_editor(df_admin, hide_index=True, use_container_width=True)
        
        if st.button("🗑️ Procesar Eliminaciones en la Nube"):
            st.session_state.reservas = df_editado[df_editado["❌ Borrar"] == False].drop(columns=["❌ Borrar"])
            guardar_reservas_en_nube(st.session_state.reservas)
            st.success("Reservas borradas del sistema satisfactoriamente.")
            time.sleep(2)
            st.rerun()
            
    elif opcion_admin == "🖨️ Exportar Horario":
        st.subheader(f"Generar Horario Coloreado para PDF ({str_semana})")
        html_table = f"""
        <html><head><meta charset="utf-8">
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 12px; }}
            th {{ background-color: #006b3f; color: white; border: 1px solid #000; padding: 10px; text-align: center; }}
            td {{ border: 1px solid #000; padding: 8px; vertical-align: top; width: 16%; }}
            .hora {{ background-color: #f2f2f2; font-weight: bold; text-align: center; vertical-align: middle; }}
        </style></head><body>
        <h2 style="text-align: center; color: #006b3f; font-family: Arial;">CRONOGRAMA DE USO DE TALLERES Y EQUIPOS</h2>
        <h4 style='text-align: center; color: #333; font-family: Arial;'>{str_semana}</h4>
        <table><tr><th>Hora</th>
        """
        for d in dias: html_table += f"<th>{d}</th>"
        html_table += "</tr>"
        for h in horas:
            html_table += f"<tr><td class='hora'>{h}</td>"
            for d in dias:
                reserva = st.session_state.reservas[(st.session_state.reservas["Día"] == d) & (st.session_state.reservas["Horario"] == h)]
                if not reserva.empty:
                    contenido = ""
                    bg_color = "#ffffff"
                    for _, r in reserva.iterrows():
                        prof = r["Profesor"]
                        bg_color = colores_prof.get(prof, "#ffffff")
                        contenido += f"<b>{prof}</b><br><i>Amb.:</i> {r['Ambientes']}<br><i>Eq.:</i> {r['Equipos']}<br><hr style='margin:4px 0;'>"
                    html_table += f"<td style='background-color: {bg_color};'>{contenido}</td>"
                else:
                    html_table += "<td></td>"
            html_table += "</tr>"
        html_table += "</table></body></html>"
        
        st.components.v1.html(html_table, height=600, scrolling=True)
        st.download_button("📄 Descargar Horario (PDF)", html_table, "Horario_Coloreado.html", "text/html")

# ==========================================
# VISTA 2: PÚBLICA PARA PROFESORES
# ==========================================
else:
    st.title("🗓️ Separación Semanal de Ambientes y Equipos")
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.** El plazo venció el jueves a las 10:00 p.m.")
    else:
        st.info(f"✅ **SISTEMA ABIERTO.** Actualmente está separando recursos para la **{str_semana}**.")
        
        if st.button("🔄 Actualizar Disponibilidad"):
            st.session_state.reservas = cargar_reservas()
            st.rerun()
            
        st.subheader("📊 Recursos Ocupados en Tiempo Real")
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        
        for d in dias:
            for h in horas:
                acts = st.session_state.reservas[(st.session_state.reservas["Día"] == d) & (st.session_state.reservas["Horario"] == h)]
                if not acts.empty:
                    ocupados = []
                    for _, r in acts.iterrows():
                        if r["Ambientes"] != "(Ninguno)": ocupados.append(r["Ambientes"])
                        if r["Equipos"] != "(Ninguno)": ocupados.append(r["Equipos"])
                    matriz.at[h, d] = f"🔴 SEPARADO:\n{', '.join(ocupados)}"
                    
        st.dataframe(matriz, use_container_width=True)
        st.markdown("---")
        
        st.subheader("📝 Registrar Separación")
        
        profesor = st.selectbox("Docente Responsable", profesores_lista, key=f"prof_{st.session_state.form_key}")
        dias_sel = st.multiselect("1. Seleccione los días de práctica:", dias, key=f"dias_main_{st.session_state.form_key}")
        reservas_temporales = []
        
        if dias_sel:
            st.markdown("##### 2. Requerimientos por Bloque Horario")
            for d in dias_sel:
                st.markdown(f'<div class="bloque-dia"><div class="titulo-dia">🗓️ {d.upper()}</div>', unsafe_allow_html=True)
                h_sel = st.multiselect(f"⏰ Seleccione los horarios para el {d}:", horas, key=f"h_{d}_{st.session_state.form_key}")
                
                if h_sel:
                    for h in h_sel:
                        st.markdown(f'<div class="bloque-hora"><div class="titulo-hora">⏱️ Bloque: {h}</div>', unsafe_allow_html=True)
                        col_a, col_e = st.columns(2)
                        with col_a: a_sel = st.multiselect(f"🏢 Ambientes", ambientes_opciones, key=f"a_{d}_{h}_{st.session_state.form_key}")
                        with col_e: e_sel = st.multiselect(f"🚜 Equipos", equipos_opciones, key=f"e_{d}_{h}_{st.session_state.form_key}")
                        m_sel = st.text_input(f"🛠️ Materiales extra", key=f"m_{d}_{h}_{st.session_state.form_key}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        reservas_temporales.append({
                            "Día": d, "Horario": h, "Profesor": profesor, 
                            "Ambientes": ", ".join(a_sel) if a_sel else "(Ninguno)", 
                            "Equipos": ", ".join(e_sel) if e_sel else "(Ninguno)",
                            "Materiales": m_sel if m_sel else "(Ninguno)",
                            "List_Amb": a_sel, "List_Eq": e_sel
                        })
                st.markdown('</div>', unsafe_allow_html=True)
            
            if reservas_temporales:
                st.markdown("---")
                st.markdown("### 👁️ Previsualización de su Horario")
                st.info("Verifique su horario. Lo reservado por otros aparece en ROJO. Su separación actual resalta en AZUL.")
                
                df_horario_visual = matriz.copy()
                
                for res in reservas_temporales:
                    texto_celda_azul = f"🔵 SU SELECCIÓN:\nAmb: {res['Ambientes']}\nEq: {res['Equipos']}"
                    actual = df_horario_visual.at[res["Horario"], res["Día"]]
                    
                    if "🟢" in str(actual):
                        df_horario_visual.at[res["Horario"], res["Día"]] = texto_celda_azul
                    else:
                        df_horario_visual.at[res["Horario"], res["Día"]] = str(actual) + "\n\n" + texto_celda_azul
                    
                st.table(df_horario_visual)
                
                placeholder_exito = st.empty()
                
                if st.button("✅ Confirmar Separación Definitiva", use_container_width=True):
                    cruces = []
                    st.session_state.reservas = cargar_reservas()
                    
                    for res in reservas_temporales:
                        d, h = res["Día"], res["Horario"]
                        amb_nuevos = set(res["List_Amb"])
                        eq_nuevos = set(res["List_Eq"])
                        
                        actuales_dh = st.session_state.reservas[(st.session_state.reservas["Día"] == d) & (st.session_state.reservas["Horario"] == h)]
                        
                        for _, act in actuales_dh.iterrows():
                            amb_act = set([a.strip() for a in act["Ambientes"].split(",") if a.strip() and a.strip() != "(Ninguno)"])
                            eq_act = set([e.strip() for e in act["Equipos"].split(",") if e.strip() and e.strip() != "(Ninguno)"])
                            
                            cruce_amb = [a for a in amb_nuevos if a in amb_act and a != "Campo"]
                            cruce_eq = [e for e in eq_nuevos if e in eq_act and e != "Ningún Equipo en particular"]
                            
                            if cruce_amb or cruce_eq:
                                motivo = []
                                if cruce_amb: motivo.append(f"Ambiente: {', '.join(cruce_amb)}")
                                if cruce_eq: motivo.append(f"Equipo: {', '.join(cruce_eq)}")
                                cruces.append(f"{d} a las {h} ({' / '.join(motivo)})")
                    
                    if cruces:
                        st.error(f"⚠️ **Cruce detectado:** Otros docentes acaban de separar estos recursos: {', '.join(cruces)}. Por favor actualice la página.")
                    else:
                        for r in reservas_temporales:
                            del r["List_Amb"]
                            del r["List_Eq"]
                        
                        df_final = pd.concat([st.session_state.reservas, pd.DataFrame(reservas_temporales)], ignore_index=True)
                        exito = guardar_reservas_en_nube(df_final)
                        
                        if exito:
                            st.session_state.reservas = df_final
                            st.balloons()
                            st.toast("✅ ¡Guardado satisfactoriamente!", icon="🎉")
                            placeholder_exito.success("✅ ¡Guardado permanentemente en la Nube! La pantalla se limpiará automáticamente en 5 segundos.")
                            time.sleep(5)
                            st.session_state.form_key += 1
                            st.rerun()
                        else:
                            st.error("Hubo un error guardando en Google Sheets. Revisa el enlace.")
