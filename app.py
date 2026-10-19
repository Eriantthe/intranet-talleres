import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pytz
import time
import requests
import json

# === ENLACE OFICIAL DE LA BASE DE DATOS EN GOOGLE SHEETS ===
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbwoJ1ELyLOwr1ORFcWUcnwrcQpsyKj-6_0obweEBnq9P8HqdLlNQCAe8IDMdk8R4nIR/exec"
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
        
    return pd.DataFrame(columns=[
        "Día", "Horario", "Profesor", "Ambientes", 
        "Equipos", "Materiales", "Operario", "Fecha/Hora Registro"
    ])

def guardar_reservas_en_nube(df):
    try:
        registros = df.to_dict(orient='records')
        payload = {
            "action": "save", 
            "reservas": registros
        }
        requests.post(
            URL_APPS_SCRIPT, 
            data=json.dumps(payload), 
            headers={'Content-Type': 'application/json'}, 
            timeout=10
        )
        return True
    except:
        return False

# --- VARIABLES DE ESTADO ---
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "form_key" not in st.session_state:
    st.session_state.form_key = 0

if "mostrar_exito" not in st.session_state:
    st.session_state.mostrar_exito = False

if "reservas" not in st.session_state or st.session_state.reservas.empty:
    st.session_state.reservas = cargar_reservas()

tz_lima = pytz.timezone('America/Lima')
ahora = datetime.now(tz_lima)
dias_para_lunes = 7 - ahora.weekday()
lunes_obj = ahora + timedelta(days=dias_para_lunes)
viernes_obj = lunes_obj + timedelta(days=4)
str_semana = f"Semana del {lunes_obj.strftime('%d/%m')} al {viernes_obj.strftime('%d/%m')}"

formulario_cerrado = False 

dias = [
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"
]

horas = [
    "08:00 am - 09:50 am", 
    "11:00 am - 12:50 pm", 
    "02:00 pm - 03:50 pm", 
    "04:00 pm - 05:50 pm"
]

ambientes_base = [
    "Soldadura", "Metalmecánica", "Motores", "Pool", "Patio", "Rejas", "Campo"
]

equipos_base = [
    "Ningún Equipo en particular", "NH TD5.80", "NH TD5.100", "NH TD90", "JD 3050B", 
    "JD 1040", "NH B110B", "NH L223", "SOLD ELECTRODO MANUAL", "SOLD OXI", 
    "SOLD TIG", "SOLD MIG/MAG", "TORNO", "FRESADORA", "ESMERIL", "PRENSA HIDRAULICA", 
    "REMACHADORA", "FRAGUA", "MAQUETA MOTOR"
]

profesores_lista = [
    "ROJAS ALEJANDRO, FRANCISCO", "GARCIA ARMAS, JUVENAL", "ALTAMIRANO CHUNGA, LUIS", 
    "CACERES GUERRERO, FREDY", "CHEVARRIA MOSCOSO, MARGARITA", "REBAZA PINO, ALFREDO", 
    "ZINGG ROSELL, AUGUSTO", "VASQUEZ CACERES, JAIME", "ORELLANA PARDAVE, JOSE", 
    "SALAS PEÑA, CARLO", "RUBIO VALLE, ALEXIS", "YARIN ACHACHAGUA, ANWAR", "SALAS PINTO, DIONISIO"
]

colores_prof = {
    "ROJAS ALEJANDRO, FRANCISCO": "#D7BDE2", "GARCIA ARMAS, JUVENAL": "#A3E4D7", 
    "ALTAMIRANO CHUNGA, LUIS": "#FAD7A0", "CACERES GUERRERO, FREDY": "#F9E79F", 
    "CHEVARRIA MOSCOSO, MARGARITA": "#F5B7B1", "REBAZA PINO, ALFREDO": "#B4CDE6", 
    "ZINGG ROSELL, AUGUSTO": "#C5E0B4", "VASQUEZ CACERES, JAIME": "#D2B4DE", 
    "ORELLANA PARDAVE, JOSE": "#AED6F1", "SALAS PEÑA, CARLO": "#F5CBA7", 
    "RUBIO VALLE, ALEXIS": "#A9DFBF", "YARIN ACHACHAGUA, ANWAR": "#FADBD8", 
    "SALAS PINTO, DIONISIO": "#E6B0AA"
}

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
    
    .tarjeta-fluido { background-color: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border-bottom: 5px solid #006b3f; margin-bottom: 10px;}
    .icono-fluido { font-size: 40px; margin-bottom: 5px; }
    .valor-fluido { font-size: 24px; font-weight: bold; color: #2c3e50; margin: 0; }
    .titulo-fluido { font-size: 12px; color: #7f8c8d; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;}
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #006b3f !important; 
        color: white !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
st.sidebar.markdown("### 🚜 Talleres y Equipos")
st.sidebar.markdown("Sistema Oficial de Separación.")
st.sidebar.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

if st.session_state.admin_mode:
    st.sidebar.success("✅ Modo Admin Activo")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.admin_mode = False
        st.rerun()
else:
    with st.sidebar.expander("🔑 Acceso Administrador"):
        clave = st.text_input("Contraseña", type="password")
        if st.button("Entrar") and clave == "orellana2026":
            st.session_state.admin_mode = True
            st.rerun()

# ==========================================
# VISTA 1: ADMINISTRADOR
# ==========================================
if st.session_state.admin_mode:
    st.title("⚙️ Panel de Control Administrativo")
    
    # --- CARGA CENTRALIZADA DE DATOS DE MAQUINARIA ---
    sheet_id = "13e2p-qGmZrcUNERjJR9j-BUyGakT0Xsp1pffwZUfreM"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=58572181"
    df_datos = pd.DataFrame()
    tractores = []
    cols_fechas = []
    error_excel = None
    
    try:
        df_crudo = pd.read_csv(csv_url, header=None)
        
        fila_encabezado = 0
        for idx, fila in df_crudo.iterrows():
            textos = [str(x).strip().lower() for x in fila.values]
            if any("tipo de tractor" in t for t in textos) or any("registro" in t for t in textos):
                fila_encabezado = idx
                break
        
        fila_cols = df_crudo.iloc[fila_encabezado].copy()
        
        if (fila_encabezado + 1) < len(df_crudo):
            fila_fechas = df_crudo.iloc[fila_encabezado + 1]
        else:
            fila_fechas = fila_cols
        
        columnas_finales = []
        for col_i in range(len(fila_cols)):
            val_c = str(fila_cols[col_i]).strip()
            val_f = str(fila_fechas[col_i]).strip()
            
            if col_i == 0: 
                columnas_finales.append("Tractor")
            elif col_i == 1: 
                columnas_finales.append("Registro")
            elif col_i == 2: 
                columnas_finales.append("UN")
            else:
                if val_f and val_f != "nan":
                    nombre_fecha = val_f
                else:
                    nombre_fecha = val_c
                columnas_finales.append(nombre_fecha)
        
        df_datos = df_crudo.iloc[fila_encabezado + 2:].copy()
        df_datos.columns = columnas_finales
        df_datos["Tractor"] = df_datos["Tractor"].replace("", None).ffill()
        df_datos = df_datos.dropna(subset=["Registro"])
        df_datos["Registro"] = df_datos["Registro"].astype(str).str.strip().str.lower()
        
        tractores = df_datos["Tractor"].dropna().unique().tolist()
        cols_fechas = [c for c in df_datos.columns if c not in ["Tractor", "Registro", "UN"]]
        
    except Exception as e:
        error_excel = e

    # --- PESTAÑAS DEL PANEL ---
    tab_maquinaria, tab_evidencias, tab_reservas, tab_horario = st.tabs([
        "🚜 Control Visual", 
        "📸 Evidencias",
        "🗑️ Gestionar Reservas", 
        "🖨️ Exportar Horario"
    ])
    
    # ----------------------------------------------------
    # PESTAÑA 1: CONTROL VISUAL
    # ----------------------------------------------------
    with tab_maquinaria:
        st.subheader("Estado Analítico e Historial de Maquinaria")
        
        if error_excel:
            st.error(f"⚠️ Error procesando la hoja de registros: {error_excel}")
        elif tractores:
            tractor_sel = st.selectbox("🚜 Seleccione el equipo para inspeccionar:", tractores)
            df_trac = df_datos[df_datos["Tractor"] == tractor_sel].copy()
            
            def mapear_nivel(val):
                if pd.isna(val): 
                    return 0.0
                
                txt = str(val).strip().lower()
                
                if txt == "max": return 100.0
                if "3/4" in txt and "max" in txt: return 87.5
                if txt == "3/4": return 75.0
                if "2/4" in txt and "3/4" in txt: return 62.5
                if txt in ["2/4", "1/2"]: return 50.0
                if "1/4" in txt and "2/4" in txt: return 37.5
                if txt == "1/4": return 25.0
                if txt == "min": return 15.0
                    
                try: 
                    return float(txt.replace('%', '').replace(',', ''))
                except: 
                    return 0.0

            if cols_fechas:
                ultima_col_fecha = cols_fechas[-1]
            else:
                ultima_col_fecha = None
            
            def obtener_valor_actual(parametro):
                fila = df_trac[df_trac["Registro"].str.contains(parametro, na=False)]
                if not fila.empty and ultima_col_fecha:
                    v = fila[ultima_col_fecha].values[0]
                    return str(v)
                return "Sin dato"

            comb_txt = obtener_valor_actual("combustible")
            refri_txt = obtener_valor_actual("refrigerante")
            aceite_m_txt = obtener_valor_actual("aceite de motor")
            aceite_h_txt = obtener_valor_actual("hidráulico")
            horo_txt = obtener_valor_actual("horometro")
            
            if horo_txt == "Sin dato": 
                horo_txt = obtener_valor_actual("horómetro")

            val_comb = mapear_nivel(comb_txt)
            val_refri = mapear_nivel(refri_txt)
            val_aceite_m = mapear_nivel(aceite_m_txt)
            val_aceite_h = mapear_nivel(aceite_h_txt)
            
            if ultima_col_fecha:
                fecha_etiqueta = f" ({ultima_col_fecha})"
            else:
                fecha_etiqueta = ""
                
            st.markdown(f"### 📌 Nivel Más Reciente: **{tractor_sel}**{fecha_etiqueta}")
            
            c1, c2, c3, c4, c5 = st.columns(5)
            
            with c1:
                st.markdown(f"""<div class="tarjeta-fluido"><div class="icono-fluido">⛽</div><div class="titulo-fluido">Combustible</div><p class="valor-fluido">{comb_txt}</p></div>""", unsafe_allow_html=True)
                st.progress(min(max(int(val_comb), 0), 100) / 100)
                
            with c2:
                st.markdown(f"""<div class="tarjeta-fluido"><div class="icono-fluido">🏺</div><div class="titulo-fluido">Refrigerante</div><p class="valor-fluido">{refri_txt}</p></div>""", unsafe_allow_html=True)
                st.progress(min(max(int(val_refri), 0), 100) / 100)
                
            with c3:
                st.markdown(f"""<div class="tarjeta-fluido"><div class="icono-fluido">🛢️</div><div class="titulo-fluido">A. Motor</div><p class="valor-fluido">{aceite_m_txt}</p></div>""", unsafe_allow_html=True)
                st.progress(min(max(int(val_aceite_m), 0), 100) / 100)
                
            with c4:
                st.markdown(f"""<div class="tarjeta-fluido"><div class="icono-fluido">⚙️</div><div class="titulo-fluido">A. Hidráulico</div><p class="valor-fluido">{aceite_h_txt}</p></div>""", unsafe_allow_html=True)
                st.progress(min(max(int(val_aceite_h), 0), 100) / 100)
                
            with c5:
                st.markdown(f"""<div class="tarjeta-fluido"><div class="icono-fluido">⏱️</div><div class="titulo-fluido">Horómetro</div><p class="valor-fluido">{horo_txt} <span style="font-size:16px;">hrs</span></p></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📈 Análisis Histórico de Rendimiento")
            
            metrica_grafico = st.selectbox(
                "Seleccione el indicador que desea graficar a lo largo de las fechas:", 
                ["Combustible", "Refrigerante", "Aceite de Motor", "Aceite Hidráulico", "Horómetro"]
            )
            
            if metrica_grafico == "Combustible": 
                clave_param = "combustible"
            elif metrica_grafico == "Refrigerante": 
                clave_param = "refrigerante"
            elif metrica_grafico == "Aceite de Motor": 
                clave_param = "aceite de motor"
            elif metrica_grafico == "Aceite Hidráulico": 
                clave_param = "hidráulico"
            elif metrica_grafico == "Horómetro": 
                clave_param = "horometro"
            
            fila_metrica = df_trac[df_trac["Registro"].str.contains(clave_param, na=False)]
            
            if not fila_metrica.empty and cols_fechas:
                valores_temporales = []
                for f in cols_fechas:
                    val_crudo = fila_metrica[f].values[0]
                    
                    if metrica_grafico == "Horómetro":
                        try: 
                            v_num = float(str(val_crudo).replace(',', ''))
                        except: 
                            v_num = None
                    else:
                        v_num = mapear_nivel(val_crudo)
                        
                    valores_temporales.append({
                        "Fecha": f, 
                        "Valor": v_num, 
                        "Texto": str(val_crudo)
                    })
                
                df_historico_plot = pd.DataFrame(valores_temporales)
                
                if metrica_grafico == "Horómetro":
                    fig = px.area(
                        df_historico_plot, 
                        x="Fecha", 
                        y="Valor", 
                        markers=True, 
                        title=f"Horómetro Acumulado (hrs) - {tractor_sel}", 
                        hover_data={"Texto": True, "Valor": False}
                    )
                    fig.update_traces(
                        line_color="#ff5722", 
                        fillcolor="rgba(255, 87, 34, 0.25)", 
                        marker=dict(size=8, color="#006b3f")
                    )
                else:
                    fig = px.line(
                        df_historico_plot, 
                        x="Fecha", 
                        y="Valor", 
                        markers=True, 
                        title=f"Evolución de {metrica_grafico} (%) - {tractor_sel}", 
                        hover_data={"Texto": True, "Valor": True}, 
                        line_shape="spline"
                    )
                    fig.update_traces(
                        line_color="#006b3f", 
                        marker=dict(size=8, color="#ff5722")
                    )
                    fig.update_layout(yaxis=dict(range=[0, 105], title="Nivel Estimado (%)"))
                    
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No se registraron datos para {metrica_grafico} en este equipo.")
            
            with st.expander("Ver tabla completa de este equipo"):
                st.dataframe(df_trac, use_container_width=True)
        else:
            st.error("No se encontraron nombres de tractores en el archivo.")

    # ----------------------------------------------------
    # PESTAÑA 2: BUSCADOR AUTOMÁTICO DE EVIDENCIAS EN DRIVE
    # ----------------------------------------------------
    with tab_evidencias:
        st.subheader("📸 Buscador Automático de Evidencias en Google Drive")
        st.write("Selecciona el equipo, la fecha y el fluido para extraer la foto directamente desde tus carpetas organizadas.")
        
        if error_excel:
            st.error(f"⚠️ Error cargando datos base: {error_excel}")
        elif tractores:
            c_trac, c_fec, c_flu = st.columns(3)
            
            with c_trac:
                tractor_ev = st.selectbox("🚜 Seleccione Tractor", tractores, key="ev_trac")
                
            with c_fec:
                if cols_fechas:
                    fechas_inversas = list(reversed(cols_fechas))
                else:
                    fechas_inversas = []
                fecha_ev = st.selectbox("📅 Fecha de Inspección", fechas_inversas, key="ev_fec")
                
            with c_flu:
                opciones_fluidos = ["Combustible", "Refrigerante", "Aceite de Motor", "Aceite Hidráulico", "Horómetro"]
                fluido_ev = st.selectbox("💧 Tipo de Fluido", opciones_fluidos, key="ev_flu")
            
            if fluido_ev == "Combustible": 
                clave_param_ev = "combustible"
            elif fluido_ev == "Refrigerante": 
                clave_param_ev = "refrigerante"
            elif fluido_ev == "Aceite de Motor": 
                clave_param_ev = "aceite de motor"
            elif fluido_ev == "Aceite Hidráulico": 
                clave_param_ev = "hidráulico"
            elif fluido_ev == "Horómetro": 
                clave_param_ev = "horometro"
            
            df_trac_ev = df_datos[df_datos["Tractor"] == tractor_ev]
            fila_metrica_ev = df_trac_ev[df_trac_ev["Registro"].str.contains(clave_param_ev, na=False)]
            
            valor_registrado = "No registrado en Excel"
            if not fila_metrica_ev.empty and fecha_ev in fila_metrica_ev.columns:
                valor_registrado = str(fila_metrica_ev[fecha_ev].values[0])
            
            st.markdown(f"**Nivel reportado en Excel:** `{valor_registrado}`")
            st.markdown("---")
            
            if st.button("🔍 Buscar y Mostrar Fotografía en Google Drive", type="primary"):
                with st.spinner("Conectando con Google Drive y buscando evidencia..."):
                    try:
                        params = {
                            "action": "getFoto",
                            "tractor": tractor_ev,
                            "fecha": fecha_ev,
                            "fluido": fluido_ev
                        }
                        res = requests.get(URL_APPS_SCRIPT, params=params, timeout=20)
                        datos_foto = res.json()
                        
                        if "url" in datos_foto:
                            st.image(
                                datos_foto["url"], 
                                caption=f"Evidencia: {fluido_ev} - {tractor_ev} ({fecha_ev})", 
                                width=600
                            )
                        else:
                            st.error(f"❌ {datos_foto.get('error', 'No se encontró la foto en la ruta especificada de Drive.')}")
                    except Exception as e:
                        st.error(f"Error de conexión con Google Drive: Revise que los permisos de Apps Script estén activos. Detalle: {e}")
        else:
            st.error("No hay tractores disponibles.")

    # ----------------------------------------------------
    # PESTAÑA 3: GESTIONAR RESERVAS
    # ----------------------------------------------------
    with tab_reservas:
        st.subheader("Borrador de Reservas Activas")
        st.write("Marca la casilla '❌ Borrar' en las filas que desees eliminar y presiona el botón inferior para borrar de la nube.")
        
        df_admin = st.session_state.reservas.copy()
        columnas_orden = [
            "Fecha/Hora Registro", "Día", "Horario", "Profesor", 
            "Ambientes", "Equipos", "Materiales", "Operario"
        ]
        
        columnas_presentes = []
        for c in columnas_orden:
            if c in df_admin.columns:
                columnas_presentes.append(c)
                
        df_admin = df_admin[columnas_presentes]
        
        df_admin.insert(0, "❌ Borrar", False)
        df_editado = st.data_editor(df_admin, hide_index=True, use_container_width=True)
        
        if st.button("🗑️ Procesar Eliminaciones en la Nube"):
            with st.spinner('⏳ Borrando registros en la nube... por favor espere'):
                df_limpio = df_editado[df_editado["❌ Borrar"] == False].drop(columns=["❌ Borrar"])
                st.session_state.reservas = df_limpio
                guardar_reservas_en_nube(st.session_state.reservas)
                st.success("Reservas borradas del sistema satisfactoriamente.")
                time.sleep(2)
                st.rerun()
            
    # ----------------------------------------------------
    # PESTAÑA 4: EXPORTAR HORARIO
    # ----------------------------------------------------
    with tab_horario:
        st.subheader(f"Generar Horario Coloreado para PDF ({str_semana})")
        
        html_table = f"""<html><head><meta charset="utf-8">
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 12px; }}
            th {{ background-color: #006b3f; color: white; border: 1px solid #000; padding: 10px; text-align: center; }}
            td {{ border: 1px solid #000; padding: 8px; vertical-align: top; width: 16%; }}
            .hora {{ background-color: #f2f2f2; font-weight: bold; text-align: center; vertical-align: middle; }}
        </style></head><body>
        <h2 style="text-align: center; color: #006b3f; font-family: Arial;">CRONOGRAMA DE USO DE TALLERES Y EQUIPOS</h2>
        <h4 style='text-align: center; color: #333; font-family: Arial;'>{str_semana}</h4>
        <table><tr><th>Hora</th>"""
        
        for d in dias: 
            html_table += f"<th>{d}</th>"
            
        html_table += "</tr>"
        
        for h in horas:
            html_table += f"<tr><td class='hora'>{h}</td>"
            for d in dias:
                reserva = st.session_state.reservas[
                    (st.session_state.reservas["Día"] == d) & 
                    (st.session_state.reservas["Horario"] == h)
                ]
                
                if not reserva.empty:
                    contenido = ""
                    bg_color = "#ffffff"
                    for _, r in reserva.iterrows():
                        prof = r["Profesor"]
                        
                        if prof in colores_prof:
                            bg_color = colores_prof[prof]
                        else:
                            bg_color = "#ffffff"
                            
                        if r.get('Fecha/Hora Registro', ''):
                            fecha_reg = f"<small style='color:#555;'>({r['Fecha/Hora Registro']})</small><br>"
                        else:
                            fecha_reg = ""
                            
                        if r.get("Operario", "") == "Sí":
                            op_tag = " <b style='color:#b71c1c;'>[Requiere Operario]</b>"
                        else:
                            op_tag = ""
                            
                        contenido += f"<b>{prof}</b>{op_tag}<br>{fecha_reg}<i>Amb.:</i> {r['Ambientes']}<br><i>Eq.:</i> {r['Equipos']}<br><hr style='margin:4px 0;'>"
                        
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
    
    if st.session_state.mostrar_exito:
        st.balloons()
        st.success("✅ ¡Guardado satisfactoriamente! El formulario se ha reiniciado y está listo para otra reserva.")
        st.session_state.mostrar_exito = False
    
    if formulario_cerrado:
        st.error("🔒 **SISTEMA CERRADO.** El plazo venció el jueves a las 10:00 p.m.")
    else:
        st.info(f"✅ **SISTEMA ABIERTO.** Actualmente está separando recursos para la **{str_semana}**.")
        
        if st.button("🔄 Actualizar Disponibilidad"):
            with st.spinner("🔄 Obteniendo datos actualizados de la nube..."):
                st.session_state.reservas = cargar_reservas()
            st.rerun()
            
        st.subheader("📊 Recursos Ocupados en Tiempo Real")
        matriz = pd.DataFrame(index=horas, columns=dias)
        matriz.fillna("🟢 Libre", inplace=True)
        
        for d in dias:
            for h in horas:
                acts = st.session_state.reservas[
                    (st.session_state.reservas["Día"] == d) & 
                    (st.session_state.reservas["Horario"] == h)
                ]
                
                if not acts.empty:
                    ocupados = []
                    for _, r in acts.iterrows():
                        if str(r["Ambientes"]) != "(Ninguno)": 
                            ocupados.append(str(r["Ambientes"]))
                        if str(r["Equipos"]) != "(Ninguno)": 
                            ocupados.append(str(r["Equipos"]))
                    matriz.at[h, d] = f"🔴 SEPARADO:\n{', '.join(ocupados)}"
                    
        st.dataframe(matriz, use_container_width=True)
        st.markdown("---")
        
        st.subheader("📝 Registrar Separación")
        
        profesor = st.selectbox(
            "Docente Responsable", 
            profesores_lista, 
            key=f"prof_{st.session_state.form_key}"
        )
        
        dias_sel = st.multiselect(
            "1. Seleccione los días de práctica:", 
            dias, 
            key=f"dias_main_{st.session_state.form_key}"
        )
        
        reservas_temporales = []
        
        if dias_sel:
            st.markdown("##### 2. Requerimientos por Bloque Horario")
            
            for d in dias_sel:
                st.markdown(f'<div class="bloque-dia"><div class="titulo-dia">🗓️ {d.upper()}</div>', unsafe_allow_html=True)
                
                h_sel = st.multiselect(
                    f"⏰ Seleccione los horarios para el {d}:", 
                    horas, 
                    key=f"h_{d}_{st.session_state.form_key}"
                )
                
                if h_sel:
                    for h in h_sel:
                        st.markdown(f'<div class="bloque-hora"><div class="titulo-hora">⏱️ Bloque: {h}</div>', unsafe_allow_html=True)
                        
                        ocupados_en_bloque = st.session_state.reservas[
                            (st.session_state.reservas["Día"] == d) & 
                            (st.session_state.reservas["Horario"] == h)
                        ]
                        
                        amb_ya_ocupados = set()
                        eq_ya_ocupados = set()
                        
                        for _, fila_o in ocupados_en_bloque.iterrows():
                            for a in str(fila_o["Ambientes"]).split(","):
                                a_str = a.strip()
                                if a_str and a_str not in ["(Ninguno)", "Campo"]: 
                                    amb_ya_ocupados.add(a_str)
                            for e in str(fila_o["Equipos"]).split(","):
                                e_str = e.strip()
                                if e_str and e_str not in ["(Ninguno)", "Ningún Equipo en particular"]: 
                                    eq_ya_ocupados.add(e_str)

                        def formatear_amb(nombre): 
                            if nombre in amb_ya_ocupados:
                                return f"🔴 [OCUPADO] {nombre}"
                            return nombre
                            
                        def formatear_eq(nombre): 
                            if nombre in eq_ya_ocupados:
                                return f"🔴 [OCUPADO] {nombre}"
                            return nombre

                        col_a, col_e = st.columns(2)
                        
                        with col_a: 
                            a_sel = st.multiselect(
                                f"🏢 Ambientes", 
                                ambientes_base, 
                                format_func=formatear_amb, 
                                key=f"a_{d}_{h}_{st.session_state.form_key}"
                            )
                            
                        with col_e: 
                            e_sel = st.multiselect(
                                f"🚜 Equipos", 
                                equipos_base, 
                                format_func=formatear_eq, 
                                key=f"e_{d}_{h}_{st.session_state.form_key}"
                            )
                            
                        cruces_inmediatos_a = [a for a in a_sel if a in amb_ya_ocupados]
                        cruces_inmediatos_e = [e for e in e_sel if e in eq_ya_ocupados]
                        
                        if cruces_inmediatos_a or cruces_inmediatos_e:
                            msgs = []
                            if cruces_inmediatos_a: 
                                msgs.append(f"Ambiente(s): {', '.join(cruces_inmediatos_a)}")
                            if cruces_inmediatos_e: 
                                msgs.append(f"Equipo(s): {', '.join(cruces_inmediatos_e)}")
                            st.warning(f"⚠️ **Atención:** Ya se encuentra ocupado en este horario: {' | '.join(msgs)}")
                            
                        col_mat, col_op = st.columns([3, 1])
                        
                        with col_mat: 
                            m_sel = st.text_input(
                                f"🛠️ Materiales extra", 
                                key=f"m_{d}_{h}_{st.session_state.form_key}"
                            )
                            
                        with col_op:
                            st.write("")
                            st.write("")
                            req_operario = st.checkbox(
                                "👷 Requiere Operario", 
                                key=f"op_{d}_{h}_{st.session_state.form_key}"
                            )
                            
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        timestamp_actual = datetime.now(tz_lima).strftime("%d/%m/%Y %I:%M %p")
                        
                        if a_sel:
                            ambientes_guardar = ", ".join(a_sel)
                        else:
                            ambientes_guardar = "(Ninguno)"
                            
                        if e_sel:
                            equipos_guardar = ", ".join(e_sel)
                        else:
                            equipos_guardar = "(Ninguno)"
                            
                        if m_sel:
                            materiales_guardar = m_sel
                        else:
                            materiales_guardar = "(Ninguno)"
                            
                        if req_operario:
                            operario_guardar = "Sí"
                        else:
                            operario_guardar = "No"
                            
                        reservas_temporales.append({
                            "Día": d, 
                            "Horario": h, 
                            "Profesor": profesor, 
                            "Ambientes": ambientes_guardar, 
                            "Equipos": equipos_guardar, 
                            "Materiales": materiales_guardar, 
                            "Operario": operario_guardar,
                            "Fecha/Hora Registro": timestamp_actual,
                            "List_Amb": a_sel, 
                            "List_Eq": e_sel
                        })
                        
                st.markdown('</div>', unsafe_allow_html=True)
            
            if reservas_temporales:
                st.markdown("---")
                st.markdown("### 👁️ Previsualización de su Horario")
                st.info("Verifique su horario. Lo reservado por otros aparece en ROJO. Su separación actual resalta en AZUL.")
                
                df_horario_visual = matriz.copy()
                
                for res in reservas_temporales:
                    if res["Operario"] == "Sí":
                        tag_op = " [Operario: SÍ]"
                    else:
                        tag_op = ""
                        
                    texto_celda_azul = f"🔵 SU SELECCIÓN:\nAmb: {res['Ambientes']}\nEq: {res['Equipos']}{tag_op}"
                    actual = df_horario_visual.at[res["Horario"], res["Día"]]
                    
                    if "🟢" in str(actual): 
                        df_horario_visual.at[res["Horario"], res["Día"]] = texto_celda_azul
                    else: 
                        df_horario_visual.at[res["Horario"], res["Día"]] = str(actual) + "\n\n" + texto_celda_azul
                        
                st.table(df_horario_visual)
                
                placeholder_exito = st.empty()
                
                if st.button("✅ Confirmar Separación Definitiva", use_container_width=True):
                    with st.spinner("⏳ Procesando y guardando su reserva en la nube... por favor espere"):
                        cruces = []
                        st.session_state.reservas = cargar_reservas()
                        
                        for res in reservas_temporales:
                            d = res["Día"]
                            h = res["Horario"]
                            amb_nuevos = set(res["List_Amb"])
                            eq_nuevos = set(res["List_Eq"])
                            
                            actuales_dh = st.session_state.reservas[
                                (st.session_state.reservas["Día"] == d) & 
                                (st.session_state.reservas["Horario"] == h)
                            ]
                            
                            for _, act in actuales_dh.iterrows():
                                amb_act = set([a.strip() for a in str(act["Ambientes"]).split(",") if a.strip() and a.strip() != "(Ninguno)"])
                                eq_act = set([e.strip() for e in str(act["Equipos"]).split(",") if e.strip() and e.strip() != "(Ninguno)"])
                                
                                cruce_amb = [a for a in amb_nuevos if a in amb_act and a != "Campo"]
                                cruce_eq = [e for e in eq_nuevos if e in eq_act and e != "Ningún Equipo en particular"]
                                
                                if cruce_amb or cruce_eq:
                                    motivo = []
                                    if cruce_amb: 
                                        motivo.append(f"Ambiente: {', '.join(cruce_amb)}")
                                    if cruce_eq: 
                                        motivo.append(f"Equipo: {', '.join(cruce_eq)}")
                                    cruces.append(f"{d} a las {h} ({' / '.join(motivo)})")
                        
                        if cruces: 
                            st.error(f"⚠️ **Cruce detectado:** Otros docentes acaban de separar estos recursos: {', '.join(cruces)}. Por favor actualice la página.")
                        else:
                            timestamp_envio = datetime.now(tz_lima).strftime("%d/%m/%Y %I:%M %p")
                            
                            for r in reservas_temporales:
                                r["Fecha/Hora Registro"] = timestamp_envio
                                del r["List_Amb"]
                                del r["List_Eq"]
                                
                            df_final = pd.concat([st.session_state.reservas, pd.DataFrame(reservas_temporales)], ignore_index=True)
                            exito = guardar_reservas_en_nube(df_final)
                            
                            if exito:
                                st.session_state.reservas = df_final
                                st.toast("✅ ¡Guardado satisfactoriamente!", icon="🎉")
                                placeholder_exito.success("✅ ¡Guardado permanentemente en la Nube! La pantalla se limpiará automáticamente en 5 segundos.")
                                time.sleep(5)
                                st.session_state.form_key += 1
                                st.session_state.mostrar_exito = True
                                st.rerun()
                            else: 
                                st.error("Hubo un error guardando en Google Sheets. Revisa el enlace y tu conexión.")
