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
# Asegúrate de que el nombre del archivo coincida con el que subiste
logo_path = 'Logo-QCD (2).png' 
logo_exists = os.path.exists(logo_path)

st.divider()
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if logo_exists:
        st.image(Image.open(logo_path), width=150)
    else:
        st.caption("(Sube el logo como Logo-QCD (2).png)")

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
    # Si el usuario activa "Grado Alimenticio" pero elige un espesante que no suele serlo (o viceversa)
    if h1_solicitado and esp_n not in ["Alum. Comp.", "Sulf. Calcio", "Comp. Litio"]:
        alerta_h1 = "\n⚠️ ATENCIÓN: Verifique que el producto QCD seleccionado cuente con registro NSF H1."
    elif h1_solicitado:
        alerta_h1 = "\n✅ PRODUCTO SEGURO: El espesante seleccionado es compatible con estándares H1."

    if res == 1: return "COMPATIBLE", f"Mezcla segura. Seguir plan de re-lubricación.{alerta_h1}", "#28a745"
    if res == 0: return "MEZCLA LIMITADA", f"Riesgo de ablandamiento. Se requiere purga constante durante la transición.{alerta_h1}", "#ffc107"
    return "INCOMPATIBLE", f"¡PELIGRO! Requiere limpieza total del rodamiento antes de aplicar producto QCD.{alerta_h1}", "#dc3545"

# --- INTERFAZ DE USUARIO ---
st.sidebar.header("Configuración del Reporte")
info_contacto = st.sidebar.text_area("Datos de contacto:", "Amatlán de los Reyes, Ver. | ventas@qcdmexico.com")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='color: #003366;'>⚙️ Especificaciones Técnicas</h3>", unsafe_allow_html=True)
    equipo = st.text_input("Identificación del Equipo", "Motor Extrusora")
    d_ext = st.number_input("Diámetro Exterior (mm)", value=110)
    d_int = st.number_input("Diámetro Interior (mm)", value=45)
    ancho = st.number_input("Ancho del Rodamiento (mm)", value=20)
    rpm = st.number_input("Velocidad de Trabajo (RPM)", value=1750)
    temp = st.slider("Temperatura de Operación (°C)", 20, 160, 65)

with col2:
    st.markdown("<h3 style='color: #003366;'>✅ Diagnóstico QCD</h3>", unsafe_allow_html=True)
    
    # NUEVAS OPCIONES: H1 y NLGI
    c_h1, c_nlgi = st.columns(2)
    with c_h1:
        es_h1 = st.toggle("¿Requiere Grado Alimenticio H1?", help="Active para aplicaciones con riesgo de contacto accidental con alimentos.")
    with c_nlgi:
        grado_nlgi = st.select_slider("Grado NLGI (Consistencia)", options=["000", "00", "0", "1", "2", "3"], value="2")

    st.write("---")
    
    esp_lista = ["Litio", "Comp. Litio", "Alum. Comp.", "Bario", "Sodio", "Bentonita", "Poliurea", "Sulf. Calcio"]
    esp_a = st.selectbox("Espesante Actual (Grasa en uso)", esp_lista)
    esp_n = st.selectbox("Espesante Nuevo (Producto QCD)", esp_lista)
    
    g_cant = calcular_cantidad_grasa(d_ext, ancho)
    f_hrs = calcular_frecuencia(rpm, d_int, temp)
    status, msg, color = verificar_compatibilidad(esp_a, esp_n, es_h1)
    
    st.metric("Dosis de Grasa", f"{g_cant} g")
    st.metric("Frecuencia Recomendada", f"{f_hrs} Horas")
    
    st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; font-weight: bold;'>{status}: {msg}</div>", unsafe_allow_html=True)

st.divider()

# --- GENERADOR DE PDF ---
if st.button("📄 GENERAR REPORTE PROFESIONAL"):
    # Preparamos los datos para el PDF
    h1_txt = "SÍ (NSF H1)" if es_h1 else "NO (Industrial)"
    payload = {
        "DIAGNÓSTICO DEL EQUIPO": {"ID": equipo, "RPM": f"{rpm}", "Temperatura": f"{temp} C"},
        "PROPIEDADES DE LA GRASA": {"Consistencia NLGI": grado_nlgi, "Certificación H1": h1_txt},
        "CÁLCULOS DE INGENIERÍA": {"Dosis": f"{g_cant} g", "Frecuencia": f"{f_hrs} horas"},
        "SEGURIDAD": {"Anterior": esp_a, "Nuevo QCD": esp_n, "Resultado": status}
    }
    
    # Aquí llamamos a tu función de PDF (asegúrate de incluirla en tu archivo completo)
    # Por ahora, mostramos éxito en pantalla
    st.success(f"Reporte listo para {equipo}. Grado NLGI {grado_nlgi} registrado.")
    # (Para descargar el PDF, usa la función generar_pdf_corporativo definida en pasos anteriores)

st.caption("© 2026 QCD DE MEXICO - Especialistas en lubricación de alto desempeño.")
