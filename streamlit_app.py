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
        st.warning("⚠️ Logo no detectado: Logo-QCD (2).png")

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
        alerta_h1 = " / Verificar registro NSF H1."
    elif h1_solicitado:
        alerta_h1 = " / Producto Grado H1 Confirmado."

    if res == 1: return "COMPATIBLE", f"Mezcla segura{alerta_h1}", "#28a745"
    if res == 0: return "MEZCLA LIMITADA", f"Riesgo de ablandamiento. Purga necesaria{alerta_h1}", "#ffc107"
    return "INCOMPATIBLE", f"¡PELIGRO! Limpieza total requerida{alerta_h1}", "#dc3545"

# --- DISEÑO COMPACTO (UNA SOLA HOJA) ---
def generar_pdf_compacto(equipo, rpm, temp, nlgi, h1_val, g_cant, f_hrs, esp_a, esp_n, status, contacto, logo_on, observaciones):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    
    # 1. ENCABEZADO
    if logo_on:
        pdf.image(logo_path, 10, 10, 35)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, txt="REPORTE TÉCNICO DE INGENIERÍA", ln=True, align='R')
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(227, 6, 19)
    pdf.cell(0, 5, txt="QCD DE MÉXICO", ln=True, align='R')
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, txt="Una decisión ejecutiva para la eficiencia industrial.", ln=True, align='R')
    
    pdf.set_draw_color(227, 6, 19)
    pdf.set_line_width(0.5)
    pdf.line(10, 35, 200, 35)
    pdf.ln(8)
    
    # 2. INFORMACIÓN GENERAL
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 6, txt="  DATOS OPERATIVOS DEL EQUIPO", ln=True, fill=True)
    pdf.ln(1)
    
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(0, 0, 0)
    col_width = 90
    pdf.cell(col_width, 6, txt=f" > Equipo: {equipo}", ln=0)
    pdf.cell(col_width, 6, txt=f" > Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=1)
    pdf.cell(col_width, 6, txt=f" > Velocidad: {rpm} RPM", ln=0)
    pdf.cell(col_width, 6, txt=f" > Temperatura: {temp} C", ln=1)
    pdf.cell(col_width, 6, txt=f" > Consistencia NLGI: {nlgi}", ln=0)
    pdf.cell(col_width, 6, txt=f" > Grado Alimenticio H1: {h1_val}", ln=1)
    pdf.ln(4)

    # 3. RECOMENDACIÓN QCD (TABLA COMPACTA)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, txt="  RECOMENDACIÓN TÉCNICA QCD", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(227, 6, 19)
    pdf.cell(col_width, 8, txt=f" DOSIS: {g_cant} g", ln=0)
    pdf.cell(col_width, 8, txt=f" FRECUENCIA: {f_hrs} Horas", ln=1)
    
    pdf.set_font("Arial", '', 9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, txt=f" > Grasa Actual: {esp_a}", ln=True)
    pdf.cell(0, 6, txt=f" > Producto QCD Sugerido: {esp_n}", ln=True)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 6, txt=f" > Compatibilidad: {status}", ln=True)
    pdf.ln(4)

    # 4. OBSERVACIONES (Limitado para asegurar una hoja)
    if observaciones:
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 6, txt="  NOTAS TÉCNICAS", ln=True, fill=True)
        pdf.ln(1)
        pdf.set_font("Arial", '', 8)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 4, txt=observaciones[:400]) # Límite de caracteres para no desbordar
        pdf.ln(4)

    # 5. FIRMAS (Compactas)
    pdf.set_y(-40) # Ajustado más arriba para evitar salto de página
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(95, 8, txt="_______________________", ln=0, align='C')
    pdf.cell(95, 8, txt="_______________________", ln=1, align='C')
    pdf.cell(95, 4, txt="Asesor Técnico QCD", ln=0, align='C')
    pdf.cell(95, 4, txt="Firma / Sello Planta", ln=1, align='C')
    
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 4, txt=f"{contacto}", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ STREAMLIT ---
st.sidebar.header("Configuración de Reporte")
info_contacto = st.sidebar.text_area("Datos contacto:", "QCD DE MÉXICO | Amatlán de los Reyes, Ver. | ventas@qcdmexico.com")

col1, col2 = st.columns(2)
with col1:
    st.markdown("<h3 style='color: #003366;'>⚙️ Datos Técnicos</h3>", unsafe_allow_html=True)
    equipo = st.text_input("Equipo", "Motor Extrusora #1")
    d_ext = st.number_input("D. Exterior (mm)", value=110)
    d_int = st.number_input("D. Interior (mm)", value=45)
    ancho = st.number_input("Ancho (mm)", value=20)
    rpm = st.number_input("RPM", value=1750)
    temp = st.slider("Temp. Operación (°C)", 20, 150, 60)

with col2:
    st.markdown("<h3 style='color: #003366;'>✅ Configuración QCD</h3>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca: es_h1 = st.toggle("H1 Alimenticio")
    with cb: grado_nlgi = st.select_slider("NLGI", options=["000", "00", "0", "1", "2", "3"], value="2")
    
    esp_lista = ["Litio", "Comp. Litio", "Alum. Comp.", "Bario", "Sodio", "Bentonita", "Poliurea", "Sulf. Calcio"]
    esp_a = st.selectbox("Espesante Actual", esp_lista)
    esp_n = st.selectbox("Espesante QCD", esp_lista)
    
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg, color = verificar_compatibilidad(esp_a, esp_n, es_h1)
    
    st.metric("Dosis", f"{g_cant} g")
    st.metric("Frecuencia", f"{f_hrs} h")
    st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;'>{status}: {msg}</div>", unsafe_allow_html=True)

st.divider()
obs = st.text_area("Observaciones técnicas (Aparecerán en el PDF):", placeholder="Ej: Se detectó contaminación por agua en el rodamiento...")

# --- GENERACIÓN ---
h1_status = "SÍ (NSF H1)" if es_h1 else "NO"
pdf_data = generar_pdf_compacto(equipo, rpm, temp, grado_nlgi, h1_status, g_cant, f_hrs, esp_a, esp_n, status, info_contacto, logo_exists, obs)

st.download_button(
    label="📥 DESCARGAR REPORTE (1 HOJA)",
    data=pdf_data,
    file_name=f"Reporte_{equipo}.pdf",
    mime="application/pdf"
)
