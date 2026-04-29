import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

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
    .selected-card {
        border: 2px solid #722f37;
        padding: 10px;
        border-radius: 10px;
        background-color: #fff4f5;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
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
    # Usamos FPDF de fpdf2
    pdf = FPDF()
    pdf.add_page()
    
    # IMPORTANTE: Usamos 'helvetica' que es estándar, 
    # pero para símbolos raros como el € a veces es mejor usar 'EUR' o 'Euro'
    pdf.set_font("helvetica", "B", 16)
    
    # Título
    pdf.set_text_color(114, 47, 55) 
    pdf.cell(190, 10, "CATÁLOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    for _, row in vinos_seleccionados.iterrows():
        # Encabezado del vino (UTF-8 activado por defecto en fpdf2)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(190, 8, f"{row['VINO']}", ln=True, border='B')
        
        # Detalles
        pdf.set_font("helvetica", "", 10)
        pdf.cell(95, 7, f"Bodega: {row['BODEGA']}", ln=False)
        pdf.cell(95, 7, f"Origen: {row['ORIGEN']}", ln=True)
        
        pdf.cell(95, 7, f"Uvas: {row['UVAS']}", ln=False)
        
        # Precio - Reemplazamos el símbolo € por 'Euros' si da problemas de fuente
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        precio_val = row[c_horeca] if c_horeca else "N/A"
        
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(95, 7, f"Precio Horeca: {precio_val} Euros", ln=True)
        pdf.ln(5)
    
    # En fpdf2, output() ya devuelve los bytes directamente si no se pone nombre de archivo
    return pdf.output()
df = load_data()

# --- ESTADO DE SELECCIÓN ---
if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = []

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)
    except:
        st.title("🍷 GLOP DYD")
    
    st.divider()
    busqueda = st.text_input("🔍 Buscar vino o bodega...")
    
    # Botón de exportar
    st.subheader("📄 Exportación")
    if st.session_state.seleccionados:
        df_export = df[df.index.isin(st.session_state.seleccionados)]
        pdf_data = generar_pdf(df_export)
        st.download_button(
            label="📥 Descargar PDF Seleccionados",
            data=pdf_data,
            file_name="catalogo_seleccionado_glop.pdf",
            mime="application/pdf",
            type="primary"
        )
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = []
            st.rerun()
    else:
        st.info("Selecciona vinos en el catálogo para exportar.")

# --- CUADRÍCULA ---
if not df.empty:
    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 
                    df_f['BODEGA'].str.contains(busqueda, case=False)]

    st.title("🍷 Catálogo Digital")
    
    cols = st.columns(4)
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            # Checkbox de selección
            seleccionado = st.checkbox("Seleccionar", key=f"sel_{idx}", 
                                     value=idx in st.session_state.seleccionados)
            
            if seleccionado and idx not in st.session_state.seleccionados:
                st.session_state.seleccionados.append(idx)
            elif not seleccionado and idx in st.session_state.seleccionados:
                st.session_state.seleccionados.remove(idx)

            url = row.get('URL', "")
            img_url = url if str(url).startswith("http") else "https://via.placeholder.com/200x300?text=Vino"
            st.image(img_url, use_container_width=True)
            
            st.markdown(f"**{row['VINO']}**")
            st.caption(f"{row['BODEGA']}")
            
            # Mostrar precio rápido si existe
            c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
            if c_horeca:
                st.write(f"**{row[c_horeca]}€**")
