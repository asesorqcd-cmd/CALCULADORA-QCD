import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Reporte Técnico de Lubricación Industrial - QCD DE MEXICO", 
    page_icon="⚙️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- IDENTIDAD CORPORATIVA ---
logo_path = 'Logo-QCD (2).png' 
logo_exists = os.path.exists(logo_path)

st.divider()
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if logo_exists:
        st.image(Image.open(logo_path), width=150)
    else:
        st.caption("⚠️ Sube el archivo: Logo-QCD (2).png")

with col_title:
    st.markdown("<h1 style='color: #003366; margin-top: -15px;'>REPORTE TÉCNICO DE LUBRICACIÓN INDUSTRIAL</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #E30613; font-style: italic;'>Una decisión ejecutiva para la eficiencia industrial.</h4>", unsafe_allow_html=True)
st.divider()

# --- LÓGICA TÉCNICA ---
def calcular_cantidad_grasa(d_ext, ancho):
    return round(d_ext * ancho * 0.005, 2)

def calcular_frecuencia(rpm, d_int, temp):
    dn = rpm * d_int
    if dn <= 0: return 0
    base_horas = 14000000 / (dn + 1)
    if temp > 70:
        reducciones = (temp - 70) / 15
        base_horas = base_horas / (2 ** reducciones)
    return int(base_horas)

def verificar_compatibilidad(esp_a, esp_n, h1_solicitado):
    matriz = {
        "Litio": {"Litio": 1, "Comp. Litio": 1, "Alum. Comp.": 0, "Bario": -1, "Sodio": -1, "Bentonita": -1, "Poliurea": -1, "Sulf. Calcio": 0},
        "Comp. Litio": {"Litio": 1, "Comp. Litio": 1, "Alum. Comp.": 1, "Bario": 0, "Sodio": 1, "Bentonita": -1, "Poliurea": 1, "Sulf. Calcio": 1},
        "Alum. Comp.": {"Litio": -1, "Comp. Litio": 0, "Alum. Comp.": 1, "Bario": 0, "Sodio": -1, "Bentonita": -1, "Poliurea": 0, "Sulf. Calcio": 0},
        "Bario": {"Litio": -1, "Comp. Litio": -1, "Alum. Comp.": -1, "Bario": 1, "Sodio": -1, "Bentonita": -1, "Poliurea": -1, "Sulf. Calcio": -1},
        "Sodio": {"Litio": -1, "Comp. Litio": -1, "Alum. Comp.": -1, "Bario": -1, "Sodio": 1, "Bentonita": -1, "Poliurea": -1, "Sulf. Calcio": -1},
        "Bentonita": {"Litio": -1, "Comp. Litio": -1, "Alum. Comp.": -1, "Bario": -1, "Sodio": -1, "Bentonita": 1, "Poliurea": -1, "Sulf. Calcio": -1},
        "Poliurea": {"Litio": -1, "Comp. Litio": 1, "Alum. Comp.": 0, "Bario": -1, "Sodio": -1, "Bentonita": -1, "Poliurea": 1, "Sulf. Calcio": 1},
        "Sulf. Calcio": {"Litio": 0, "Comp. Litio": 1, "Alum. Comp.": 0, "Bario": -1, "Sodio": -1, "Bentonita": -1, "Poliurea": 1, "Sulf. Calcio": 1}
    }
    res = matriz.get(esp_a, {}).get(esp_n, 0)
    alerta_h1 = ""
    if h1_solicitado and esp_n not in ["Alum. Comp.", "Sulf. Calcio"]:
        alerta_h1 = "\n⚠️ NOTA: El espesante QCD elegido no es comúnmente H1. Verificar ficha técnica."
    elif h1_solicitado:
        alerta_h1 = "\n✅ PRODUCTO H1: Apto para industria alimentaria."

    if res == 1: return "COMPATIBLE", f"Mezcla segura.{alerta_h1}", "#28a745"
    if res == 0: return "MEZCLA LIMITADA", f"Riesgo de ablandamiento. Purga necesaria.{alerta_h1}", "#ffc107"
    return "INCOMPATIBLE", f"¡PELIGRO! Limpieza total requerida.{alerta_h1}", "#dc3545"

# --- GENERADOR DE PDF ---
def generar_pdf_profesional(datos, contacto, logo_exists):
    pdf = FPDF()
    pdf.add_page()
    if logo_exists:
        pdf.image(logo_path, 10, 8, 33)
    pdf.set_font("Arial", 'B', 15)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(200, 10, txt="REPORTE TÉCNICO DE LUBRICACIÓN INDUSTRIAL", ln=True, align='R')
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(200, 5, txt="QCD DE MEXICO - Una decisión ejecutiva", ln=True, align='R')
    pdf.set_draw_color(227, 6, 19)
    pdf.line(10, 42, 200, 42)
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=9)
    pdf.cell(190, 5, txt=f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    for titulo, contenido in datos.items():
        pdf.ln(4)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(227, 6, 19)
        pdf.cell(0, 7, txt=titulo, ln=True, fill=True)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(0, 0, 0)
        for k, v in contenido.items():
            pdf.cell(0, 6, txt=f" > {k}: {v}", ln=True)
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(95, 10, txt="_______________________", ln=0, align='C')
    pdf.cell(95, 10, txt="_______________________", ln=1, align='C')
    pdf.cell(95, 5, txt="Asesor Técnico QCD", ln=0, align='C')
    pdf.cell(95, 5, txt="Recibido Planta", ln=1, align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.sidebar.header("Datos de contacto")
info_contacto = st.sidebar.text_area("Contacto:", "Amatlán de los Reyes, Ver. | ventas@qcdmexico.com")

col1, col2 = st.columns(2)
with col1:
    st.markdown("<h3 style='color: #003366;'>⚙️ Datos del Rodamiento</h3>", unsafe_allow_html=True)
    equipo = st.text_input("Equipo", "Motor Principal")
    d_ext = st.number_input("Diámetro Exterior (mm)", value=110)
    d_int = st.number_input("Diámetro Interior (mm)", value=45)
    ancho = st.number_input("Ancho (mm)", value=20)
    rpm = st.number_input("RPM", value=1750)
    temp = st.slider("Temp. Operación (°C)", 20, 160, 60)

with col2:
    st.markdown("<h3 style='color: #003366;'>✅ Diagnóstico y Grado</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: es_h1 = st.toggle("¿Grado Alimenticio H1?")
    with c2: grado_nlgi = st.select_slider("Grado NLGI", options=["000", "00", "0", "1", "2", "3"], value="2")
    
    esp_lista = ["Litio", "Comp. Litio", "Alum. Comp.", "Bario", "Sodio", "Bentonita", "Poliurea", "Sulf. Calcio"]
    esp_a = st.selectbox("Grasa Actual", esp_lista)
    esp_n = st.selectbox("Grasa QCD", esp_lista)
    
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg, color = verificar_compatibilidad(esp_a, esp_n, es_h1)
    
    st.metric("Dosis", f"{g_cant} g")
    st.metric("Frecuencia", f"{f_hrs} h")
    st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;'>{status}: {msg}</div>", unsafe_allow_html=True)

st.divider()
if st.button("📄 GENERAR PDF"):
    h1_val = "SÍ (NSF H1)" if es_h1 else "NO"
    payload = {
        "DIAGNÓSTICO": {"ID": equipo, "RPM": f"{rpm}", "Temp": f"{temp} C"},
        "ESPECIFICACIONES": {"NLGI": grado_nlgi, "Grado H1": h1_val},
        "RECOMENDACIÓN": {"Dosis": f"{g_cant} g", "Frecuencia": f"{f_hrs} h"},
        "SEGURIDAD": {"Actual": esp_a, "Nuevo QCD": esp_n, "Resultado": status}
    }
    pdf_bytes = generar_pdf_profesional(payload, info_contacto, logo_exists)
    st.download_button("📥 Descargar Reporte", data=pdf_bytes, file_name=f"Reporte_{equipo}.pdf", mime="application/pdf")
