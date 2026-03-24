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

# --- IDENTIDAD CORPORATIVA (Logo y Título) ---
# Intentamos cargar el logo oficial
logo_path = 'Logo-QCD (2).png'
logo_exists = os.path.exists(logo_path)

st.divider()

col_logo, col_title = st.columns([1, 4])

with col_logo:
    if logo_exists:
        image = Image.open(logo_path)
        st.image(image, width=150)
    else:
        # Mensaje técnico para el desarrollador si no encuentra el logo
        st.caption("(Sube image_12.png a tu GitHub/Space)")

with col_title:
    # TÍTULO SOLICITADO
    st.markdown("<h1 style='color: #003366; margin-top: -15px;'>REPORTE TÉCNICO DE LUBRICACIÓN INDUSTRIAL</h1>", unsafe_allow_html=True)
    # LEMA Corporativo
    st.markdown("<h4 style='color: #E30613; font-style: italic;'>Una decisión ejecutiva para la eficiencia industrial.</h4>", unsafe_allow_html=True)
    st.caption("Desarrollado exclusivamente para QCD DE MEXICO")

st.divider()

# --- LÓGICA TÉCNICA (Cálculos y Matriz) ---
def calcular_cantidad_grasa(d_exterior, ancho):
    # Fórmula estándar: G = D * B * 0.005 (en gramos)
    return round(d_exterior * ancho * 0.005, 2)

def calcular_frecuencia(rpm, d_interno, temp):
    dn = rpm * d_interno
    if dn <= 0: return 0
    # Base de cálculo según norma técnica
    base_horas = 14000000 / (dn + 1)
    # Factor de corrección por temperatura (Regla de Arrhenius)
    if temp > 70:
        reducciones = (temp - 70) / 15
        base_horas = base_horas / (2 ** reducciones)
    return int(base_horas)

def verificar_compatibilidad(esp_actual, esp_nuevo):
    # Matriz técnica extendida (1: OK, 0: Riesgo, -1: Peligro)
    matriz = {
        "Litio": {"Litio": 1, "Comp. Litio": 1, "Aluminio Comp.": 0, "Bario": -1, "Sodio": -1, "Bentonita": -1, "Poliurea": -1},
        "Comp. Litio": {"Litio": 1, "Comp. Litio": 1, "Aluminio Comp.": 1, "Bario": 0, "Sodio": 1, "Bentonita": -1, "Poliurea": 1},
        "Aluminio Comp.": {"Litio": -1, "Comp. Litio": 0, "Aluminio Comp.": 1, "Bario": 0, "Sodio": -1, "Bentonita": -1, "Poliurea": 0},
        "Bario": {"Litio": -1, "Comp. Litio": -1, "Aluminio Comp.": -1, "Bario": 1, "Sodio": -1, "Bentonita": -1},
        "Sodio": {"Litio": -1, "Comp. Litio": -1, "Aluminio Comp.": -1, "Sodio": 1, "Bentonita": -1},
        "Bentonita": {"Litio": -1, "Comp. Litio": -1, "Aluminio Comp.": -1, "Sodio": -1, "Bentonita": 1, "Poliurea": -1},
        "Poliurea": {"Litio": -1, "Comp. Litio": 1, "Aluminio Comp.": 0, "Poliurea": 1, "Bentonita": -1}
    }
    res = matriz.get(esp_actual, {}).get(esp_nuevo, 0)
    
    if res == 1: return "COMPATIBLE", "La mezcla es segura. Se puede aplicar el producto QCD sobre la grasa anterior.", "#28a745"
    if res == 0: return "MEZCLA LIMITADA", "Existe riesgo de ablandamiento. Se recomienda purga constante durante la transición.", "#ffc107"
    return "INCOMPATIBLE", "¡PELIGRO QUÍMICO! Requiere limpieza mecánica total antes de aplicar el producto QCD.", "#dc3545"

# --- GENERADOR DE PDF CORPORATIVO CON LOGO ---
def generar_pdf_corporativo(datos, contacto, logo_exists):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado Corporativo
    if logo_exists:
        pdf.image(logo_path, 10, 8, 30) # Logo oficial
        
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 51, 102) # Azul corporativo
    pdf.cell(195, 10, txt="REPORTE TÉCNICO DE LUBRICACIÓN INDUSTRIAL", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128, 128, 128) # Gris
    pdf.cell(195, 5, txt="QCD DE MEXICO - \"Una decisión ejecutiva para la eficiencia industrial.\"", ln=True, align='C')
    
    pdf.set_draw_color(227, 6, 19) # Rojo QCD para la línea
    pdf.line(10, 35, 200, 35)
    
    pdf.ln(10)
    
    # Datos del Reporte
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(190, 8, txt=f"Fecha de Emisión: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    
    # Secciones del reporte
    for titulo, contenido in datos.items():
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240) # Fondo gris profesional
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(227, 6, 19) # Rojo QCD
        pdf.cell(0, 8, txt=titulo, ln=True, fill=True)
        
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        for k, v in contenido.items():
            pdf.cell(0, 7, txt=f" > {k}: {v}", ln=True)
            
    # Notas Legales y Firma
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 10, txt="__________________________", ln=0, align='C')
    pdf.cell(95, 10, txt="__________________________", ln=1, align='C')
    pdf.cell(95, 5, txt="Asesor Técnico QCD", ln=0, align='C')
    pdf.cell(95, 5, txt="Recibido Planta (Firma y Sello)", ln=1, align='C')
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, txt=f"Este documento es una guía técnica. Contacto: {contacto}", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO ---
# Sidebar profesional
st.sidebar.markdown(f"<div style='text-align: center;'><img src='https://cdn-icons-png.flaticon.com/512/933/933211.png' width='80'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; color: #003366;'>Ajustes del Reporte</h3>", unsafe_allow_html=True)
info_contacto = st.sidebar.text_area("Datos de Contacto (Para el PDF):", "Amatlán de los Reyes, Ver. | ventas@qcdmexico.com")
st.sidebar.write("---")
st.sidebar.caption("Normas técnicas de referencia: DIN 51502 / ISO 6743-9")

# Panel Principal
col1, col2 = st.columns(2)

with col1:
    # ICONO DE ENGRANES SOLICITADO
    st.markdown("<h3 style='color: #003366;'>⚙️ Especificaciones Técnicas del Rodamiento</h3>", unsafe_allow_html=True)
    equipo = st.text_input("Identificación / Tag del Equipo", "Motor Extrusora Principal")
    d_ext = st.number_input("Diámetro Exterior (mm)", value=110, help="D")
    d_int = st.number_input("Diámetro Interior (mm)", value=45, help="d")
    ancho = st.number_input("Ancho del Rodamiento (mm)", value=20, help="B")
    rpm = st.number_input("Régimen de Velocidad (RPM)", value=1750)
    temp = st.slider("Temperatura de Operación (°C)", 20, 160, 65)

with col2:
    # ICONO DE PALOMITA SOLICITADO
    st.markdown("<h3 style='color: #003366;'>✅ Diagnóstico y Recomendación QCD</h3>", unsafe_allow_html=True)
    esp_lista = ["Litio", "Comp. Litio", "Aluminio Comp.", "Bario", "Sodio", "Bentonita", "Poliurea"]
    esp_a = st.selectbox("Grasa Actual / Base", esp_lista)
    esp_n = st.selectbox("Grasa QCD Recomendada", esp_lista)
    
    st.markdown("---")
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg, color = verificar_compatibilidad(esp_a, esp_n)
    
    st.metric("Dosis de Re-lubricación Sugerida", f"{g_cant} g")
    st.metric("Frecuencia Recomendada", f"{f_hrs} Horas")
    
    st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;'>⚠️ {status}: {msg}</div>", unsafe_allow_html=True)

st.divider()

if st.button("📄 GENERAR REPORTE PROFESIONAL Y DESCARGAR PDF"):
    payload = {
        "DIAGNÓSTICO TÉCNICO DE LUBRICACIÓN": {"Identificación del Equipo": equipo, "Régimen": f"{rpm} RPM", "Temperatura": f"{temp} °C"},
        "ESPECIFICACIONES DEL RODAMIENTO": {"Diámetro Exterior": f"{d_ext} mm", "Diámetro Interior": f"{d_int} mm", "Ancho (Dimensiones)": f"{ancho} mm"},
        "RECOMENDACIONES DE INGENIERÍA QCD": {"Dosis de Grasa QCD": f"{g_cant} g", "Frecuencia Sugerida": f"{f_hrs} horas"},
        "ANÁLISIS DE SEGURIDAD OPERATIVA": {"Espesante Anterior": esp_a, "Espesante Nuevo QCD": esp_n, "Resultado": status, "Protocolo Técnico": msg}
    }
    pdf_out = generar_pdf_corporativo(payload, info_contacto, logo_exists)
    st.download_button("📥 Descargar Reporte PDF para Cliente", data=pdf_out, file_name=f"Reporte_Tecnico_{equipo}.pdf", mime="application/pdf")

st.divider()
st.caption("Herramienta de uso exclusivo para QCD DE MEXICO. © 2026. Basado en estándares de ingeniería.")
