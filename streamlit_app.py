import streamlit as st
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="QCD DE MEXICO - Lubricación Pro", layout="wide")

# --- LÓGICA TÉCNICA ---
def calcular_cantidad_grasa(d_exterior, ancho):
    return round(d_exterior * ancho * 0.005, 2)

def calcular_frecuencia(rpm, d_interno, temp):
    dn = rpm * d_interno
    if dn == 0: return 0
    base_horas = 14000000 / (dn + 1)
    if temp > 70:
        reducciones = (temp - 70) / 15
        base_horas = base_horas / (2 ** reducciones)
    return int(base_horas)

def verificar_compatibilidad(esp_actual, esp_nuevo):
    matriz = {
        "Litio": {"Litio": 1, "Comp. Litio": 1, "Calcio": 0, "Aluminio": -1, "Poliurea": -1, "Arcilla": -1},
        "Comp. Litio": {"Litio": 1, "Comp. Litio": 1, "Calcio": 0, "Aluminio": 0, "Poliurea": 0, "Arcilla": -1},
        "Sulfonato de Calcio": {"Litio": 0, "Comp. Litio": 1, "Calcio": 1, "Aluminio": -1, "Poliurea": 0, "Arcilla": -1},
        "Poliurea": {"Litio": -1, "Comp. Litio": 0, "Calcio": -1, "Aluminio": -1, "Poliurea": 1, "Arcilla": -1},
        "Arcilla": {"Litio": -1, "Comp. Litio": -1, "Calcio": -1, "Aluminio": -1, "Poliurea": -1, "Arcilla": 1}
    }
    res = matriz.get(esp_actual, {}).get(esp_nuevo, 0)
    if res == 1: return "COMPATIBLE", "Mezcla segura. Seguir plan de mantenimiento."
    if res == 0: return "MEZCLA LIMITADA", "Riesgo de ablandamiento. Se recomienda purga constante."
    return "INCOMPATIBLE", "¡PELIGRO! Requiere limpieza mecánica total antes de aplicar."

# --- GENERADOR DE PDF PROFESIONAL ---
def generar_pdf_profesional(datos, contacto):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado con Identidad Corporativa
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 51, 102) # Azul oscuro profesional
    pdf.cell(200, 10, txt="QCD DE MEXICO", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="REPORTE TÉCNICO DE LUBRICACIÓN INDUSTRIAL", ln=True, align='C')
    
    pdf.set_draw_color(0, 51, 102)
    pdf.line(10, 32, 200, 32)
    
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Fecha de Emisión: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
    
    # Bloques de Información
    for titulo, contenido in datos.items():
        pdf.ln(5)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, txt=titulo, ln=True, fill=True)
        pdf.set_font("Arial", size=10)
        for k, v in contenido.items():
            pdf.cell(0, 7, txt=f" - {k}: {v}", ln=True)
            
    # Bloque de Firma y Contacto
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 10, txt="__________________________", ln=0, align='C')
    pdf.cell(95, 10, txt="__________________________", ln=1, align='C')
    pdf.cell(95, 5, txt="Firma del Asesor Técnico", ln=0, align='C')
    pdf.cell(95, 5, txt="Sello de Recibido (Planta)", ln=1, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, txt=f"Contacto QCD DE MEXICO: {contacto}\nAmatlán de los Reyes, Veracruz. Especialistas en Lubricantes Industriales.", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.title("🏭 QCD DE MEXICO - Soluciones en Lubricación")
st.sidebar.header("Datos de Contacto (Para el PDF)")
info_contacto = st.sidebar.text_area("Información de contacto:", "ventas@qcdmexico.com | Tel: (271) XXX-XXXX")

c1, c2 = st.columns(2)

with c1:
    st.subheader("⚙️ Especificaciones Técnicas")
    equipo = st.text_input("Nombre del Equipo", "Motor Extrusora")
    d_ext = st.number_input("Diámetro Exterior (mm)", value=110)
    d_int = st.number_input("Diámetro Interior (mm)", value=45)
    ancho = st.number_input("Ancho (mm)", value=20)
    rpm = st.number_input("RPM de Trabajo", value=1750)
    temp = st.slider("Temp. de Operación (°C)", 20, 150, 65)

with c2:
    st.subheader("🧪 Análisis de Grasa")
    esp_a = st.selectbox("Espesante Actual", ["Litio", "Comp. Litio", "Sulfonato de Calcio", "Poliurea", "Arcilla"])
    esp_n = st.selectbox("Espesante Nuevo (QCD)", ["Litio", "Comp. Litio", "Sulfonato de Calcio", "Poliurea", "Arcilla"])
    h1_req = st.toggle("¿Requiere Grado Alimenticio H1?")
    
    st.markdown("---")
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg = verificar_compatibilidad(esp_a, esp_n)
    
    st.metric("Dosis Recomendada", f"{g_cant} g")
    st.metric("Frecuencia de Re-lubricación", f"{f_hrs} Horas")
    
    if status == "COMPATIBLE": st.success(status)
    elif status == "MEZCLA LIMITADA": st.warning(status)
    else: st.error(status)

st.markdown("---")
if st.button("📄 GENERAR REPORTE TÉCNICO QCD"):
    datos_finales = {
        "DATOS DEL EQUIPO": {"Identificación": equipo, "Velocidad": f"{rpm} RPM", "Temperatura": f"{temp} C"},
        "DIMENSIONES FÍSICAS": {"D. Exterior": f"{d_ext} mm", "D. Interior": f"{d_int} mm", "Ancho": f"{ancho} mm"},
        "RECOMENDACIÓN DE INGENIERÍA": {"Cantidad de Grasa": f"{g_cant} g", "Frecuencia Sugerida": f"{f_hrs} horas"},
        "PROTOCOLO DE SEGURIDAD": {"Espesante Anterior": esp_a, "Espesante Nuevo": esp_n, "Compatibilidad": status, "Acción": msg}
    }
    pdf_bytes = generar_pdf_profesional(datos_finales, info_contacto)
    st.download_button("📥 Descargar Reporte PDF", data=pdf_bytes, file_name=f"Reporte_Tecnico_{equipo}.pdf")

st.sidebar.write("---")
st.sidebar.caption("Basado en normas DIN 51502 / ISO 6743-9")
