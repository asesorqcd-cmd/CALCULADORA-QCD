import streamlit as st
from fpdf import FPDF
import datetime
from PIL import Image
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Reporte Técnico - QCD DE MEXICO", 
    page_icon="⚙️", 
    layout="wide"
)

# --- IDENTIDAD CORPORATIVA ---
logo_path = 'Logo-QCD (2).png' 
logo_exists = os.path.exists(logo_path)

st.divider()
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if logo_exists:
        st.image(Image.open(logo_path), width=100)
    else:
        st.warning("⚠️ Logo no detectado")

with col_title:
    st.markdown("<h2 style='color: #003366; margin-top: -15px;'>REPORTE TÉCNICO DE LUBRICACIÓN INDUSTRIAL</h2>", unsafe_allow_html=True)
    st.markdown("<h5 style='color: #E30613; font-style: italic;'>QCD DE MÉXICO - Ingeniería de alto desempeño</h5>", unsafe_allow_html=True)

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
    alerta_h1 = " / H1 Confirmado" if h1 else ""
    if res == 1: return "COMPATIBLE", f"Mezcla segura{alerta_h1}", "#28a745"
    if res == 0: return "LIMITADA", f"Purga necesaria{alerta_h1}", "#ffc107"
    return "INCOMPATIBLE", f"Limpieza requerida{alerta_h1}", "#dc3545"

# --- GENERACIÓN DE PDF COMPACTO ---
def generar_pdf_ultra_compacto(equipo, rpm, temp, nlgi, h1, g_cant, f_hrs, esp_a, esp_n, status, obs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(12, 10, 12)
    
    # Encabezado Compacto
    if logo_exists:
        pdf.image(logo_path, 12, 10, 28)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 7, txt="REPORTE TÉCNICO DE LUBRICACIÓN", ln=True, align='R')
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(227, 6, 19)
    pdf.cell(0, 4, txt="QCD DE MÉXICO", ln=True, align='R')
    
    pdf.set_draw_color(227, 6, 19)
    pdf.line(12, 28, 198, 28)
    pdf.ln(6)
    
    # Bloque 1: Datos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 5, txt="  DATOS DEL EQUIPO", ln=True, fill=True)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(93, 5, txt=f" > Equipo: {equipo} | RPM: {rpm}", ln=0)
    pdf.cell(93, 5, txt=f" > Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(93, 5, txt=f" > Temp: {temp} C | NLGI: {nlgi}", ln=0)
    pdf.cell(93, 5, txt=f" > Grado H1: {'SÍ' if h1 else 'NO'}", ln=1)
    
    # Bloque 2: Recomendación
    pdf.ln(2)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 5, txt="  DIAGNÓSTICO QCD", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(227, 6, 19)
    pdf.cell(93, 7, txt=f" DOSIS: {g_cant} g", ln=0)
    pdf.cell(93, 7, txt=f" FRECUENCIA: {f_hrs} Horas", ln=1)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, txt=f" > Compatibilidad: {status} ({esp_a} >> {esp_n})", ln=True)

    # Bloque 3: Notas
    if obs:
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(0, 5, txt="  OBSERVACIONES:", ln=True)
        pdf.set_font("Arial", '', 7)
        pdf.multi_cell(0, 3.5, txt=obs[:600])

    # Bloque 4: FIRMAS SUBIDAS
    pdf.set_y(-35) # Posición más alta para asegurar una hoja
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(93, 5, txt="_______________________", ln=0, align='C')
    pdf.cell(93, 5, txt="_______________________", ln=1, align='C')
    pdf.cell(93, 4, txt="Asesor Técnico QCD", ln=0, align='C')
    pdf.cell(93, 4, txt="Firma de Planta", ln=1, align='C')
    
    # Información de contacto compacta bajo la firma
    pdf.set_font("Arial", '', 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(93, 3, txt="Tel: 271 114 3337", ln=0, align='C')
    pdf.cell(93, 3, txt="Amatlán de los Reyes, Ver.", ln=1, align='R')
    pdf.cell(93, 3, txt="ventas.qcdmexico@gmail.com", ln=0, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ APP ---
col1, col2 = st.columns(2)
with col1:
    equipo = st.text_input("Equipo", "Motor Principal")
    d_ext = st.number_input("D. Exterior (mm)", value=110)
    d_int = st.number_input("D. Interior (mm)", value=45)
    ancho = st.number_input("Ancho (mm)", value=20)
    rpm = st.number_input("RPM", value=1750)
    temp = st.slider("Temp. Operación (°C)", 20, 150, 60)

with col2:
    es_h1 = st.toggle("H1 Alimenticio")
    grado_nlgi = st.select_slider("NLGI", options=["000", "00", "0", "1", "2", "3"], value="2")
    esp_lista = ["Litio", "Comp. Litio", "Alum. Comp.", "Bario", "Sodio", "Bentonita", "Poliurea", "Sulf. Calcio"]
    esp_a = st.selectbox("Grasa Actual", esp_lista)
    esp_n = st.selectbox("Grasa QCD", esp_lista)
    
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg, color = verificar_compatibilidad(esp_a, esp_n, es_h1)
    
    st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center;'><b>{status}: {msg}</b></div>", unsafe_allow_html=True)

obs = st.text_area("Notas técnicas:")

if st.button("📥 GENERAR PDF "):
    pdf_bytes = generar_pdf_ultra_compacto(equipo, rpm, temp, grado_nlgi, es_h1, g_cant, f_hrs, esp_a, esp_n, status, obs)
    st.download_button("Descargar Reporte", data=pdf_bytes, file_name=f"QCD_{equipo}.pdf", mime="application/pdf")
