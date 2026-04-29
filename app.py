import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import requests
import os
from tempfile import NamedTemporaryFile

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# Estilos personalizados para mejorar la visualización de las tarjetas
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 250px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
    }
    .stButton>button { width: 100%; border-radius: 10px; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        # Intenta leer el archivo Excel
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        # Normalizar nombres de columnas a mayúsculas y sin espacios
        df.columns = [str(c).strip().upper() for c in df.columns]
        # Limpiar espacios en los datos
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al abrir el archivo Excel: {e}")
        return pd.DataFrame()

# 3. FUNCIÓN: VENTANA EMERGENTE (MODAL)
@st.dialog("Ficha Técnica")
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
        st.write(f"**Añada:** {row.get('AÑADA', row.get('AÑO', 'N/A'))}")
        
        # Lógica dinámica para encontrar la columna de precio HORECA
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]} €")
        
        st.divider()
        st.caption("Información extraída del catálogo oficial GLOP 2026. Los precios no incluyen IVA.")

# 4. FUNCIÓN: GENERAR PDF
def generar_pdf(vinos_seleccionados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título del documento
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(114, 47, 55) 
    pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=1, align='C')
    pdf.ln(10)
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for _, row in vinos_seleccionados.iterrows():
        y_inicial = pdf.get_y()
        url_img = str(row.get('URL', ""))
        tmp_path = None

        # Gestión de imagen en el PDF
        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, headers=headers, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    pdf.image(tmp_path, x=10, y=y_inicial, h=25)
            except:
                pass
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)

        # Información del vino
        pdf.set_xy(45, y_inicial)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(114, 47, 55)
        nombre = str(row.get('VINO', 'Vino')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, nombre, ln=1)
        
        pdf.set_x(45)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        bodega = str(row.get('BODEGA', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        anada = str(row.get('AÑADA', row.get('AÑO', 'N/A'))).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Bodega: {bodega} | Añada: {anada}", ln=1)

        # Línea divisoria
        y_final = max(pdf.get_y(), y_inicial + 28)
        pdf.set_y(y_final)
        pdf.line(10, y_final, 200, y_final)
        pdf.ln(5)
        
        if pdf.get_y() > 260:
            pdf.add_page()

    # Retorno de bytes optimizado para fpdf2
    return bytes(pdf.output())

# 5. LÓGICA DE LA APLICACIÓN
df = load_data()

# Inicializar el carrito de selección si no existe
if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🍷 GLOP DYD")
    st.divider()
    busqueda = st.text_input("🔍 Buscar por vino o bodega")
    
    st.subheader("📄 Exportación")
    if st.session_state.seleccionados:
        st.write(f"Has seleccionado **{len(st.session_state.seleccionados)}** vinos.")
        
        df_export = df[df.index.isin(st.session_state.seleccionados)]
        pdf_bytes = generar_pdf(df_export)
        
        st.download_button(
            label="📥 Descargar PDF",
            data=pdf_bytes,
            file_name="catalogo_seleccion_glop.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = []
            st.rerun()
    else:
        st.info("Selecciona vinos en el catálogo para generar un PDF.")

# --- CUERPO PRINCIPAL (CATÁLOGO) ---
if not df.empty:
    # Filtrado de búsqueda
    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 
                    df_f['BODEGA'].str.contains(busqueda, case=False)]

    st.title("Catálogo Digital 2026")
    
    # Crear cuadrícula de 4 columnas
    cols = st.columns(4)
    
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                # Checkbox de selección rápida
                is_selected = idx in st.session_state.seleccionados
                seleccion = st.checkbox("Seleccionar", key=f"sel_{idx}", value=is_selected)
                
                # Actualizar estado de selección
                if seleccion and idx not in st.session_state.seleccionados:
                    st.session_state.seleccionados.append(idx)
                    st.rerun()
                elif not seleccion and idx in st.session_state.seleccionados:
                    st.session_state.seleccionados.remove(idx)
                    st.rerun()

                # Imagen del producto
                img_path = row.get('URL', "https://via.placeholder.com/200x300?text=Vino")
                st.image(img_path, use_container_width=True)
                
                # Nombre y bodega (truncado para estética)
                st.markdown(f"**{row['VINO'][:25]}...**" if len(row['VINO']) > 28 else f"**{row['VINO']}**")
                st.caption(f"{row['BODEGA']}")
                
                # Botón para abrir la ventana de detalles
                if st.button("🔍 Ver detalles", key=f"btn_{idx}"):
                    mostrar_detalles(row)
else:
    st.warning("No se encontró el archivo Excel o está vacío.")
