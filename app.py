import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
import os
from tempfile import NamedTemporaryFile

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide", page_icon="🍷")

# Estilos CSS para tarjetas uniformes y diseño profesional
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 250px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
        padding: 5px;
    }
    .stButton>button { width: 100%; border-radius: 10px; }
    .stCheckbox { margin-bottom: -15px; }
    .vino-title {
        height: 50px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        font-weight: bold;
        font-size: 1.1rem;
        color: #4A1016;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    file_path = 'CATALOGO 2026 GLOP.xlsx'
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al leer Excel: {e}")
        return pd.DataFrame()

# 3. VENTANA EMERGENTE (FICHA TÉCNICA)
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
        st.caption("Información válida para temporada 2026.")

# 4. FUNCIÓN GENERAR PDF
import io  # Asegúrate de tener este import al principio del archivo

def generar_pdf(vinos_seleccionados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def clean_txt(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    for _, row in vinos_seleccionados.iterrows():
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(114, 47, 55)
        pdf.cell(190, 10, clean_txt("GLOP - CATÁLOGO SELECCIONADO 2026"), ln=1, align='C')
        pdf.ln(10)

        y_img = pdf.get_y()
        url_img = str(row.get('URL', ""))
        
        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    pdf.image(tmp_path, x=15, y=y_img, h=60)
                    os.remove(tmp_path)
            except:
                pdf.rect(15, y_img, 40, 60)

        pdf.set_xy(70, y_img)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, clean_txt(row.get('VINO', 'Vino')), ln=1)
        pdf.set_x(70)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 7, clean_txt(row.get('BODEGA', 'N/A')), ln=1)
        pdf.ln(5)
        pdf.set_x(70)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        
        info = f"Origen: {row.get('ORIGEN', 'N/A')}\nUvas: {row.get('UVAS', 'N/A')}\nAñada: {row.get('AÑADA', row.get('AÑO', 'N/A'))}"
        pdf.multi_cell(0, 6, clean_txt(info))
        
        pdf.ln(5)
        pdf.set_x(70)
        pdf.set_font("Helvetica", "B", 12)
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"
        pdf.cell(0, 8, clean_txt(f"Precio Horeca: {precio}"), ln=1)

    # --- LA PARTE CRÍTICA ---
    # Obtenemos el output como bytes y lo metemos en un buffer compatible con Streamlit
    pdf_output = pdf.output() 
    if isinstance(pdf_output, str): # Para versiones viejas de fpdf
        return pdf_output.encode('latin-1')
    return bytes(pdf_output) # Para fpdf2

# 5. LÓGICA DE LA APP
df = load_data()

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = set()

with st.sidebar:
    try:
        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)
    except:
        st.title("🍷 GLOP DYD")
    
    st.divider()
    
    # Filtro por Origen
    filtro_origen = []
    if not df.empty:
        lista_origenes = sorted(df['ORIGEN'].unique())
        filtro_origen = st.multiselect("📍 Filtrar por Origen:", options=lista_origenes)
    
    busqueda = st.text_input("🔍 Buscar vino o bodega...")
    
    if st.session_state.seleccionados:
        st.success(f"Seleccionados: {len(st.session_state.seleccionados)}")
        df_export = df[df.index.isin(list(st.session_state.seleccionados))]
        if st.download_button("📥 Descargar PDF", data=generar_pdf(df_export), file_name="catalogo_glop.pdf", mime="application/pdf"):
            st.toast("Generando archivo...")
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = set()
            st.rerun()
    else:
        st.info("Selecciona productos para exportar.")

# CUERPO PRINCIPAL
if not df.empty:
    st.title("Catálogo Digital 2026")
    df_f = df.copy()
    
    if filtro_origen:
        df_f = df_f[df_f['ORIGEN'].isin(filtro_origen)]
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 
                    df_f['BODEGA'].str.contains(busqueda, case=False)]

    if df_f.empty:
        st.warning("No hay resultados para esta búsqueda.")
    else:
        cols = st.columns(4)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 4]:
                with st.container(border=True):
                    # Lógica de Checkbox
                    is_checked = idx in st.session_state.seleccionados
                    if st.checkbox("Seleccionar", key=f"c_{idx}", value=is_checked):
                        if idx not in st.session_state.seleccionados:
                            st.session_state.seleccionados.add(idx)
                            st.rerun()
                    elif is_checked:
                        st.session_state.seleccionados.remove(idx)
                        st.rerun()

                    img_url = row.get('URL', "") if str(row.get('URL', "")).startswith("http") else "https://via.placeholder.com/200x300?text=Vino"
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"<div class='vino-title'>{row['VINO']}</div>", unsafe_allow_html=True)
                    st.caption(f"📍 {row['ORIGEN']} | {row['BODEGA']}")
                    if st.button("Ficha técnica", key=f"b_{idx}"):
                        mostrar_detalles(row)
else:
    st.error("Error: Sube el archivo 'CATALOGO 2026 GLOP.xlsx' a la raíz del repositorio.")
