import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Reporte Técnico QCD DE MÉXICO", 
    page_icon="⚙️", 
    layout="wide"
)

# --- IDENTIDAD CORPORATIVA ---
logo_path = 'Logo-QCD (2).png' 
logo_exists = os.path.exists(logo_path)

col_logo, col_title = st.columns([1, 4])
with col_logo:
    if logo_exists:
        st.image(Image.open(logo_path), width=100) # Logo más chico en la app
with col_title:
    st.markdown("<h2 style='color: #003366; margin-bottom: 0;'>REPORTE TÉCNICO DE LUBRICACIÓN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #E30613; font-style: italic; margin-top: 0;'>QCD DE MÉXICO - Ingeniería de Alto Desempepeño</p>", unsafe_allow_html=True)

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

def verificar_compatibilidad(esp_a, esp_n, h1):
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
    msg_h1 = " / Grado H1" if h1 else ""
    if res == 1: return "COMPATIBLE", f"Mezcla Segura{msg_h1}", "#28a745"
    if res == 0: return "LIMITADA", f"Purga Necesaria{msg_h1}", "#ffc107"
    return "INCOMPATIBLE", f"Limpieza Total{msg_h1}", "#dc3545"

# --- PDF REDISEÑADO (1 SOLA HOJA) ---
def generar_pdf_ultra_compacto(equipo, rpm, temp, nlgi, h1, g_cant, f_hrs, esp_a, esp_n, status, obs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(12, 10, 12)
    pdf.set_auto_page_break(auto=True, margin=10)
    
    # Encabezado Compacto
    if logo_exists:
        pdf.image(logo_path, 12, 10, 25) # Logo muy pequeño
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 7, txt="REPORTE TÉCNICO DE LUBRICACIÓN", ln=True, align='R')
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(227, 6, 19)
    pdf.cell(0, 5, txt="QCD DE MÉXICO", ln=True, align='R')
    
    pdf.set_draw_color(227, 6, 19)
    pdf.set_line_width(0.4)
    pdf.line(12, 30, 198, 30)
    pdf.ln(8)
    
    # Bloque 1: Datos Operativos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 6, txt="  ESPECIFICACIONES DEL EQUIPO", ln=True, fill=True)
    pdf.ln(1)
    
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(93, 6, txt=f" > Equipo: {equipo}", ln=0)
    pdf.cell(93, 6, txt=f" > Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(93, 6, txt=f" > Velocidad: {rpm} RPM", ln=0)
    pdf.cell(93, 6, txt=f" > Temperatura: {temp} C", ln=1)
    pdf.cell(93, 6, txt=f" > Consistencia NLGI: {nlgi}", ln=0)
    pdf.cell(93, 6, txt=f" > Certificación H1: {'SÍ (Alimenticio)' if h1 else 'No'}", ln=1)
    pdf.ln(4)

    # Bloque 2: Recomendación QCD
    pdf.set_fill_color(0, 51, 102)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, txt="  DIAGNÓSTICO Y PROPUESTA QCD", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(227, 6, 19)
    pdf.cell(93, 8, txt=f" DOSIS: {g_cant} g", ln=0)
    pdf.cell(93, 8, txt=f" FRECUENCIA: {f_hrs} Horas", ln=1)
    
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, txt=f" > Grasa en Uso: {esp_a}", ln=True)
    pdf.cell(0, 6, txt=f" > Producto QCD Sugerido: {esp_n}", ln=True)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 6, txt=f" > Resultado de Compatibilidad: {status}", ln=True)
    pdf.ln(4)

    # Bloque 3: Observaciones
    if obs:
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, txt="  NOTAS TÉCNICAS DE CAMPO", ln=True, fill=True)
        pdf.ln(1)
        pdf.set_font("Arial", '', 8)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 4, txt=obs[:500])
        pdf.ln(4)

    # Bloque 4: Firmas y Contacto (Diseño Integrado)
    pdf.set_y(-45)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(93, 8, txt="_______________________", ln=0, align='C')
    pdf.cell(93, 8, txt="_______________________", ln=1, align='C')
    
    # Datos de ventas debajo del asesor
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(93, 4, txt="Asesor Técnico QCD", ln=0, align='C')
    pdf.set_font("Arial", '', 8)
    pdf.cell(93, 4, txt="Firma de Recibido (Planta)", ln=1, align='C')
    
    pdf.set_text_color(100, 100, 100)
    pdf.cell(93, 4, txt="Tel: 271 114 3337", ln=0, align='C')
    pdf.cell(93, 4, txt="", ln=1)
    pdf.cell(93, 4, txt="ventas.qcdmexico@gmail.com", ln=0, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ APP ---
col1, col2 = st.columns(2)
with col1:
    equipo = st.text_input("Equipo", "Motor Principal")
    d_ext = st.number_input("D. Exterior (mm)", value=110)
    d_int = st.number_input("D. Interior (mm)", value=45)
    ancho = st.number_input("Ancho (mm)", value=20)
    rpm = st.number_input("RPM", value=1750)
    temp = st.slider("Temp. (°C)", 20, 150, 60)

with col2:
    es_h1 = st.toggle("¿Grado Alimenticio H1?")
    grado_nlgi = st.select_slider("Grado NLGI", options=["000", "00", "0", "1", "2", "3"], value="2")
    esp_a = st.selectbox("Grasa Actual", ["Litio", "Comp. Litio", "Alum. Comp.", "Bario", "Sodio", "Bentonita", "Poliurea", "Sulf. Calcio"])
    esp_n = st.selectbox("Producto QCD", ["Litio", "Comp. Litio", "Alum. Comp.", "Bario", "Sodio", "Bentonita", "Poliurea", "Sulf. Calcio"])
    
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg, color = verificar_compatibilidad(esp_a, esp_n, es_h1)
    
    st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center;'><b>{status}: {msg}</b><br>{g_cant}g cada {f_hrs}h</div>", unsafe_allow_html=True)

obs = st.text_area("Observaciones para el reporte:")

if st.button("🚀 GENERAR REPORTE FINAL"):
    pdf_bytes = generar_pdf_ultra_compacto(equipo, rpm, temp, grado_nlgi, es_h1, g_cant, f_hrs, esp_a, esp_n, status, obs)
    st.download_button("📥 Descargar Reporte PDF", data=pdf_bytes, file_name=f"QCD_Reporte_{equipo}.pdf", mime="application/pdf")
