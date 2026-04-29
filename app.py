import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import requests
import os
from tempfile import NamedTemporaryFile

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# --- ESTILOS CSS ---
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

@st.cache_data
def load_data():
    try:
        # Nota: Asegúrate de que el archivo esté en la misma carpeta que el script
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al abrir el archivo Excel: {e}")
        return pd.DataFrame()

# --- FUNCIÓN GENERAR PDF ---
def generar_pdf(vinos_seleccionados):
    # Usamos 'P' (Portrait), 'mm', 'A4'
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Título Principal
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(114, 47, 55) 
    pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=True, align='C')
    pdf.ln(10)
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for _, row in vinos_seleccionados.iterrows():
        y_inicial = pdf.get_y()
        url_img = str(row.get('URL', ""))
        img_h_final = 0
        tmp_path = None

        # --- GESTIÓN DE IMAGEN ---
        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, headers=headers, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    
                    # Insertar imagen (W=0 calcula proporcional)
                    info = pdf.image(tmp_path, x=10, y=y_inicial, h=25)
                    img_h_final = 25 # Forzamos el alto para mantener orden
            except:
                pass
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    os.remove(tmp_path)

        # --- TEXTO (Desplazado a la derecha de la imagen) ---
        pdf.set_xy(45, y_inicial)
        
        # Nombre del Vino (Limpieza de caracteres para Latin-1)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(114, 47, 55)
        nombre = row.get('VINO', 'Vino').encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, nombre, ln=True)
        
        # Detalles
        pdf.set_x(45)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        
        bodega = row.get('BODEGA', 'N/A').encode('latin-1', 'replace').decode('latin-1')
        anada = row.get('AÑADA', row.get('AÑO', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Bodega: {bodega} | Añada: {anada}", ln=True)
        
        pdf.set_x(45)
        c_horeca = next((c for c in row.index if 'HORECA' in c), None)
        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, f"Precio Horeca: {precio}", ln=True)

        # Espaciado y Línea
        y_final = max(pdf.get_y(), y_inicial + 28)
        pdf.set_y(y_final)
        pdf.line(10, y_final, 200, y_final)
        pdf.ln(5)

        # Salto de página preventivo
        if pdf.get_y() > 250:
            pdf.add_page()

    return pdf.output(dest='S').encode('latin-1')

df = load_data()

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("🍷 GLOP DYD")
    st.divider()
    busqueda = st.text_input("🔍 Buscar vino o bodega...")
    
    if st.session_state.seleccionados:
        st.subheader(f"✅ {len(st.session_state.seleccionados)} seleccionados")
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = []
            st.rerun()
            
        df_export = df[df.index.isin(st.session_state.seleccionados)]
        if not df_export.empty:
            pdf_bytes = generar_pdf(df_export)
            st.download_button(
                label="📥 Descargar Catálogo PDF",
                data=pdf_bytes,
                file_name="catalogo_glop_2026.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Selecciona vinos para generar el PDF.")

# --- GRID DE PRODUCTOS ---
if not df.empty:
    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 
                    df_f['BODEGA'].str.contains(busqueda, case=False)]

    cols = st.columns(4)
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            # Contenedor visual
            with st.container(border=True):
                url = row.get('URL', "")
                img_url = url if str(url).startswith("http") else "https://via.placeholder.com/200x300?text=Vino"
                st.image(img_url)
                
                st.markdown(f"**{row['VINO']}**")
                st.caption(f"{row['BODEGA']}")
                
                # Checkbox con lógica de estado
                is_selected = idx in st.session_state.seleccionados
                if st.checkbox("Seleccionar", key=f"check_{idx}", value=is_selected):
                    if idx not in st.session_state.seleccionados:
                        st.session_state.seleccionados.append(idx)
                        st.rerun()
                else:
                    if idx in st.session_state.seleccionados:
                        st.session_state.seleccionados.remove(idx)
                        st.rerun()
