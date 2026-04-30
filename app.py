import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import requests
import os
from tempfile import NamedTemporaryFile

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# Estilos CSS para tarjetas uniformes y botones redondeados
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 250px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
    }
    .stButton>button { width: 100%; border-radius: 10px; }
    .stCheckbox { margin-bottom: -15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (Cache para velocidad)
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()

# 3. VENTANA EMERGENTE (DETALLES COMPLETOS)
@st.dialog("Ficha Técnica del Producto")
def mostrar_detalles(row):
    col_img, col_info = st.columns([1, 1.2])
    
    with col_img:
        url = row.get('URL', "")
        img_url = url if str(url).startswith("http") else "https://via.placeholder.com/400x600?text=Sin+Imagen"
        st.image(img_url, use_container_width=True)
    
    with col_info:
        st.subheader(row['VINO'])
        st.write(f"**Bodega:** {row.get('BODEGA', 'N/A')}")
        st.write(f"**Origen:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"**Uvas:** {row.get('UVAS', 'N/A')}")
        st.write(f"**Añada:** {row.get('AÑADA', row.get('AÑO', 'N/A'))}")
        
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]} €")
        
        st.divider()
        st.caption("Información técnica para uso comercial. Precios válidos para 2026.")

# 4. FUNCIÓN GENERAR PDF
def generar_pdf(vinos_seleccionados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(114, 47, 55) 
    pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=1, align='C')
    pdf.ln(10)
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for _, row in vinos_seleccionados.iterrows():
        y_inicial = pdf.get_y()
        url_img = str(row.get('URL', ""))
        tmp_path = None

        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, headers=headers, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    pdf.image(tmp_path, x=10, y=y_inicial, h=28)
            except: pass
            finally:
                if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)

        pdf.set_xy(45, y_inicial)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(114, 47, 55)
        nombre = str(row.get('VINO', 'Vino')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, nombre, ln=1)
        
        pdf.set_x(45)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        bodega = str(row.get('BODEGA', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Bodega: {bodega}", ln=1)
        
        pdf.set_x(45)
        origen = str(row.get('ORIGEN', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        uvas = str(row.get('UVAS', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Origen: {origen} | Uvas: {uvas}", ln=1)
        
        pdf.set_x(45)
        pdf.set_font("Helvetica", "B", 10)
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"
        pdf.cell(0, 6, f"Precio Horeca: {precio}", ln=1)

        y_final = max(pdf.get_y(), y_inicial + 32)
        pdf.set_y(y_final)
        pdf.line(10, y_final, 200, y_final)
        pdf.ln(5)
        
        if pdf.get_y() > 250: pdf.add_page()

    return bytes(pdf.output())

# 5. LÓGICA PRINCIPAL DE LA APP
df = load_data()

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# --- BARRA LATERAL (SIDEBAR) CON LOGO ---
with st.sidebar:
    # AÑADIMOS EL LOGO AQUÍ
    try:
        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)
    except:
        st.error("No se encontró el archivo de logo 'LOGO GLOP DYD.jpeg'")
    
    st.title("Catálogo Vinos")
    st.divider()
    busqueda = st.text_input("🔍 Buscar por vino o bodega...")
    
    if st.session_state.seleccionados:
        st.subheader("Selección actual")
        st.write(f"Vinos seleccionados: {len(st.session_state.seleccionados)}")
        
        df_export = df[df.index.isin(st.session_state.seleccionados)]
        pdf_data = generar_pdf(df_export)
        
        st.download_button(
            label="📥 Descargar Catálogo PDF",
            data=pdf_data,
            file_name="seleccion_glop_2026.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = []
            st.rerun()
    else:
        st.info("Selecciona vinos para generar el PDF.")

# --- CUERPO DEL CATÁLOGO ---
if not df.empty:
    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 
                    df_f['BODEGA'].str.contains(busqueda, case=False)]

    st.title("Catálogo Digital 2026")
    
    cols = st.columns(4)
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                is_selected = idx in st.session_state.seleccionados
                if st.checkbox("Seleccionar", key=f"sel_{idx}", value=is_selected):
                    if idx not in st.session_state.seleccionados:
                        st.session_state.seleccionados.append(idx)
                        st.rerun()
                elif is_selected:
                    st.session_state.seleccionados.remove(idx)
                    st.rerun()

                img_url = row.get('URL', "https://via.placeholder.com/200x300")
                st.image(img_url, use_container_width=True)
                
                st.markdown(f"**{row['VINO']}**")
                st.caption(f"{row['BODEGA']}")
                
                if st.button("🔍 Ver detalles", key=f"btn_{idx}"):
                    mostrar_detalles(row)
else:
    st.error("Por favor, asegúrate de que el archivo 'CATALOGO 2026 GLOP.xlsx' esté en la carpeta raíz.")
