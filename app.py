import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# CSS para unificar tamaños de imagen y diseño de tarjetas
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 300px;
        object-fit: contain;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # CAMBIO CLAVE: Usamos read_excel en lugar de read_csv
        # No necesita encoding='latin1' porque Excel ya gestiona los caracteres
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        
        # Limpieza de filas y columnas vacías
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # Normalizar nombres de columnas a MAYÚSCULAS
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Limpiar espacios en blanco en los textos
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error al abrir el archivo Excel: {e}")
        return pd.DataFrame()

# Función para la ventana emergente de detalles
@st.dialog("Ficha Técnica del Vino")
def mostrar_detalles(row):
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        url = row.get('URL', '')
        if str(url).startswith("http"):
            st.image(url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/300x450?text=Sin+Foto", use_container_width=True)
    
    with col2:
        st.header(row.get('VINO', 'Vino'))
        st.subheader(f"🏠 {row.get('BODEGA', 'Bodega')}")
        st.divider()
        
        # Características detalladas
        st.write(f"📍 **Origen:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"🍇 **Uvas:** {row.get('UVAS', 'N/A')}")
        st.write(f"📅 **Añada:** {row.get('AÑADA', 'N/A')}")
        
        # Buscamos el precio horeca (excluyendo el de compra)
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Horeca", value=f"{row[c_horeca]}€")
        
        if 'NOTAS' in row.index and row['NOTAS']:
            st.info(f"**Nota de cata:** {row['NOTAS']}")

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")
    
    # Buscador
    busqueda = st.sidebar.text_input("🔍 Buscar vino o bodega...")

    # Identificar columnas para la vista principal
    c_vino = next((c for c in df.columns if 'VINO' in c), df.columns[0])
    c_bodega = next((c for c in df.columns if 'BODEGA' in c), df.columns[1])
    c_url = next((c for c in df.columns if 'URL' in c), None)

    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f[c_vino].str.contains(busqueda, case=False, na=False) | 
                    df_f[c_bodega].str.contains(busqueda, case=False, na=False)]

    # Cuadrícula de 4 columnas
    cols = st.columns(4)
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            url = row.get(c_url, "")
            if str(url).startswith("http"):
                st.image(url, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/200x300?text=Vino", use_container_width=True)
            
            st.markdown(f"**{row[c_vino]}**")
            st.caption(f"{row[c_bodega]}")
            
            if st.button("Ver detalles", key=f"btn_{idx}"):
                mostrar_detalles(row)
            st.write("") 
else:
    st.info("Asegúrate de que el archivo 'CATALOGO 2026 GLOP.xlsx' esté en la raíz de tu GitHub.")
