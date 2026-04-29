import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import requests
import os
from tempfile import NamedTemporaryFile

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 250px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
    }
    .stButton>button { width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al cargar Excel: {e}")
        return pd.DataFrame()

# 3. VENTANA EMERGENTE (MODAL)
@st.dialog("Ficha Técnica")
def mostrar_detalles(row):
    col_img, col_info = st.columns([1, 1.2])
    with col_img:
        st.image(row.get('URL', "https://via.placeholder.com/400x600"), use_container_width=True)
    with col_info:
        st.subheader(row['VINO'])
        st.write(f"**Bodega:** {row.get('BODEGA', 'N/A')}")
        st.write(f"**Origen:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"**Uvas:** {row.get('UVAS', 'N/A')}")
        st.write(f"**Añada:** {row.get('AÑADA', row.get('AÑO', 'N/A'))}")
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]} €")

# 4. FUNCIÓN GENERAR PDF (CON ORIGEN, UVAS Y PRECIO)
def generar_pdf(vinos_seleccionados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(114, 47, 55) 
    pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=1, align='C')
    pdf.ln(10)
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for _, row in vinos_seleccionados.iterrows():
        y_inicial = pdf.get_y()
        url_img = str(row.get('URL', ""))
        tmp_path = None

        # Imagen
        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, headers=headers, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    pdf.image(tmp_path, x=10, y=y_inicial, h=25)
            except: pass
            finally:
                if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)

        # Información (Posición X=45 para dejar espacio a la imagen)
        pdf.set_xy(45, y_inicial)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(114, 47, 55)
        nombre = str(row.get('VINO', 'Vino')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, nombre, ln=1)
        
        pdf.set_x(45)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        
        # Bodega y Añada
        bodega = str(row.get('BODEGA', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Bodega: {bodega}", ln=1)
        
        # --- NUEVAS LÍNEAS: ORIGEN Y UVAS ---
        pdf.set_x(45)
        origen = str(row.get('ORIGEN', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        uvas = str(row.get('UVAS', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Origen: {origen} | Uvas: {uvas}", ln=1)
        
        # --- NUEVA LÍNEA: PRECIO HORECA ---
        pdf.set_x(45)
        pdf.set_font("Helvetica", "B", 10)
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"
        pdf.cell(0, 6, f"Precio Horeca: {precio}", ln=1)

        # Separador
        y_final = max(pdf.get_y(), y_inicial + 32)
        pdf.set_y(y_final)
        pdf.line(10, y_final, 200, y_final)
        pdf.ln(5)
        
        if pdf.get_y() > 250: pdf.add_page()

    return bytes(pdf.output())

# 5. LÓGICA PRINCIPAL
df = load_data()
if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# Sidebar
with st.sidebar:
    st.title("🍷 GLOP")
    busqueda = st.text_input("🔍 Buscar vino...")
    if st.session_state.seleccionados:
        df_export = df[df.index.isin(st.session_state.seleccionados)]
        if st.download_button("📥 Descargar PDF", data=generar_pdf(df_export), file_name="catalogo.pdf", mime="application/pdf"):
            pass
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = []
            st.rerun()

# Catálogo
if not df.empty:
    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | df_f['BODEGA'].str.contains(busqueda, case=False)]

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

                st.image(row.get('URL', "https://via.placeholder.com/200x300"), use_container_width=True)
                st.markdown(f"**{row['VINO']}**")
                if st.button("🔍 Detalles", key=f"btn_{idx}"):
                    mostrar_detalles(row)
