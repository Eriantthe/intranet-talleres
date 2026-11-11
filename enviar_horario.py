import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import smtplib
from email.message import EmailMessage
import os
import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

# 1. LÓGICA DE TIEMPO Y SEMANA
tz_lima = pytz.timezone('America/Lima')
ahora_utc = datetime.utcnow()
ahora = ahora_utc.replace(tzinfo=pytz.utc).astimezone(tz_lima)

wd = ahora.weekday() 
hora_actual = ahora.hour

# Asume ejecución Jueves a las 11:50pm -> próxima semana = +4 días
dias_al_lunes = 7 - wd if wd < 4 else 14 - wd
lunes_obj = ahora + timedelta(days=dias_al_lunes)
viernes_obj = lunes_obj + timedelta(days=4)
str_semana = f"Semana del {lunes_obj.strftime('%d/%m')} al {viernes_obj.strftime('%d/%m')}"

fechas_semana = {
    "Lunes": lunes_obj.strftime("%d/%m/%Y"),
    "Martes": (lunes_obj + timedelta(days=1)).strftime("%d/%m/%Y"),
    "Miércoles": (lunes_obj + timedelta(days=2)).strftime("%d/%m/%Y"),
    "Jueves": (lunes_obj + timedelta(days=3)).strftime("%d/%m/%Y"),
    "Viernes": viernes_obj.strftime("%d/%m/%Y")
}

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
horas = ["08:00 am - 09:50 am", "09:50 am - 11:00 am", "11:00 am - 12:50 pm", "02:00 pm - 03:50 pm", "04:00 pm - 05:50 pm"]

def obtener_color_profesor(prof_nombre):
    prof_upper = str(prof_nombre).upper()
    if "APOYO" in prof_upper or "REVISIÓN SEMANAL" in prof_upper: return "#e0e0e0"
    if "VISITA" in prof_upper: return "#fff9c4" 
    if "ROJAS" in prof_upper: return "#FFD1DC"          
    if "GARCIA" in prof_upper or "GARCÍA" in prof_upper: return "#B5EAD7" 
    if "ALTAMIRANO" in prof_upper: return "#FFEAA7"     
    if "CACERES" in prof_upper or "CÁCERES" in prof_upper: return "#DFCCF1" 
    if "CHEVARRIA" in prof_upper or "CHEVARRÍA" in prof_upper: return "#FFD8B1" 
    if "REBAZA" in prof_upper: return "#C7CEEA"         
    if "ZINGG" in prof_upper: return "#E2F0CB"          
    if "ORELLANA" in prof_upper: return "#A0C4FF"       
    if "SALAS PEÑA" in prof_upper: return "#FDFFB6"     
    if "SALAS PINTO" in prof_upper: return "#FF9AA2"    
    if "RUBIO" in prof_upper: return "#CAFFBF"          
    if "YARIN" in prof_upper or "YARÍN" in prof_upper: return "#FFC6FF" 
    if "NORELLY" in prof_upper: return "#FFB703"        
    if "ALATA" in prof_upper: return "#9BF6FF"   
    return "#ffffff"

# 2. DESCARGAR Y FILTRAR DATOS
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbwodCUKKTc0M1zY23bzMN3TZbsrH4BzwV32JcrSuUpv6_YTTuswbmhlk1IU8Dk4jA77/exec"
r = requests.get(URL_APPS_SCRIPT, timeout=15)
data = r.json()
df_crudo = pd.DataFrame(data)
df_validas = df_crudo[(df_crudo["Estado"] != "Eliminado") & (df_crudo["Semana"] == str_semana)].copy()

def obtener_contenido_y_color(reserva_df):
    if reserva_df.empty: return None, "#ffffff"
    
    profesores_en_bloque = reserva_df["Profesor"].tolist()
    hay_sujeli = any("SUJELI" in str(p).upper() for p in profesores_en_bloque)
    hay_jesus = any("JESÚS" in str(p).upper() or "JESUS" in str(p).upper() for p in profesores_en_bloque)
    hay_leansy = any("LEANSY" in str(p).upper() for p in profesores_en_bloque)
    es_revision_total = (hay_sujeli and hay_jesus and hay_leansy)
    
    if es_revision_total:
        equipos_agrupados = set()
        for _, r in reserva_df.iterrows():
            if "APOYO" in str(r["Profesor"]).upper() or "REVISIÓN" in str(r["Profesor"]).upper():
                for eq in str(r["Equipos"]).split(","):
                    if eq.strip() and eq.strip() != "(Ninguno)": equipos_agrupados.add(eq.strip())
        return f"<b>REVISIÓN SEMANAL</b><br/><i>Amb:</i> Pool<br/><i>Eq:</i> {', '.join(equipos_agrupados)}", "#e0e0e0"
    else:
        # Se toma el color del primer profesor para el fondo de la celda
        color_fondo = obtener_color_profesor(reserva_df.iloc[0]["Profesor"])
        textos = []
        for _, r in reserva_df.iterrows():
            prof = r["Profesor"]
            op_pdf = " <font color='#b71c1c'>[C/ Operario]</font>" if str(r.get("Operario")) == "Sí" else ""
            mat = str(r.get('Materiales', '-'))
            if not mat or mat.lower() == "nan" or mat == "(Ninguno)": mat = "-"
            textos.append(f"<b>{prof}</b>{op_pdf}<br/><i>Amb:</i> {r['Ambientes']}<br/><i>Eq:</i> {r['Equipos']}<br/><i>Mat:</i> <b>{mat}</b>")
        return "<br/><br/>".join(textos), color_fondo

# 3. GENERAR EL PDF CON REPORTLAB (IDÉNTICO A LA WEB)
buffer = io.BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
elements = []

styles = getSampleStyleSheet()
style_title = styles['Title']
style_title.textColor = colors.HexColor("#006b3f")

# Forzamos que las celdas interpreten HTML básico como <b> y <br/>
style_cell = ParagraphStyle(
    'CellNormal',
    parent=styles['Normal'],
    alignment=TA_CENTER,
    fontSize=8,
    leading=10
)

style_header = ParagraphStyle(
    'CellHeader',
    parent=styles['Normal'],
    alignment=TA_CENTER,
    fontSize=10,
    textColor=colors.whitesmoke,
    leading=12
)

elements.append(Paragraph(f"<b>CRONOGRAMA DE USO DE TALLERES Y EQUIPOS - SIMA ({str_semana})</b>", style_title))
elements.append(Paragraph("<br/>", styles['Normal']))

# Armar cabeceras con fechas
cabecera = [Paragraph("<b>Hora</b>", style_header)]
for d in dias:
    cabecera.append(Paragraph(f"<b>{d}</b><br/><font size=7>{fechas_semana[d]}</font>", style_header))

datos_tabla = [cabecera]
comandos_fondo = []

for idx_row, h in enumerate(horas, start=1):
    row = [Paragraph(f"<b>{h}</b>", style_cell)]
    for idx_col, d in enumerate(dias, start=1):
        reserva = df_validas[(df_validas["Día"] == d) & (df_validas["Horario"] == h)]
        txt_pdf, color_fondo = obtener_contenido_y_color(reserva)
        
        if txt_pdf: 
            row.append(Paragraph(txt_pdf, style_cell))
            comandos_fondo.append(('BACKGROUND', (idx_col, idx_row), (idx_col, idx_row), colors.HexColor(color_fondo)))
        else: 
            row.append(Paragraph("Libre", style_cell))
            
    datos_tabla.append(row)

t = Table(datos_tabla, colWidths=[80, 130, 130, 130, 130, 130])

# Estilo base de la tabla
estilo_base = [
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#006b3f")),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('BACKGROUND', (0,1), (0,-1), colors.lightgrey),
]

# Unimos el estilo base con los colores dinámicos de cada celda
t.setStyle(TableStyle(estilo_base + comandos_fondo))
elements.append(t)
doc.build(elements)
pdf_bytes = buffer.getvalue()

# 4. ENVIAR EL CORREO ELECTRÓNICO
email_user = os.environ.get('EMAIL_USER')
email_pass = os.environ.get('EMAIL_PASS')

msg = EmailMessage()
msg['Subject'] = f"🚜 Horario SIMA Oficial: {str_semana}"
msg['From'] = email_user
msg['To'] = email_user 
msg.set_content(f"Hola Norelly,\n\nEl horario se ha cerrado por esta semana. Adjunto el PDF oficial generado automáticamente con formato web.\n\nSaludos,\nBot del SIMA")
msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=f"Horario_SIMA_{lunes_obj.strftime('%d_%m')}.pdf")

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(email_user, email_pass)
    smtp.send_message(msg)

print("¡PDF generado a color y correo enviado con éxito!")
