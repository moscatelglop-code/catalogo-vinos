import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# CSS optimizado
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 300px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #722f37; /* Color borgoña vino */
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Cargamos el Excel
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al abrir el archivo Excel: {e}")
        return pd.DataFrame()

@st.dialog("Ficha Técnica")
def mostrar_detalles(row):
    col1, col2 = st.columns([1, 1.5])
    with col1:
        url = row.get('URL', '')
        st.image(url if str(url).startswith("http") else "https://via.placeholder.com/300x450?text=Sin+Foto", use_container_width=True)
    with col2:
        st.header(row.get('VINO', 'Vino'))
        st.subheader(f"🍷 {row.get('BODEGA', 'Bodega')}")
        st.divider()
        st.write(f"📍 **Origen:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"🍇 **Uvas:** {row.get('UVAS', 'N/A')}")
        st.write(f"📅 **Añada:** {row.get('AÑADA', 'N/A')}")
        
        # Búsqueda dinámica de la columna de precio
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]}€")

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)
    except:
        st.title("🍷 GLOP DYD")
    
    st.separator()
    busqueda = st.text_input("🔍 Buscar vino o bodega...")
    
    # Filtro por Origen (D.O.)
    if not df.empty and 'ORIGEN' in df.columns:
        lista_origenes = ["Todos"] + sorted(df['ORIGEN'].unique().tolist())
        filtro_origen = st.selectbox("📍 Filtrar por Origen", lista_origenes)
    else:
        filtro_origen = "Todos"

# --- LÓGICA DE FILTRADO ---
if not df.empty:
    df_f = df.copy()
    
    # Aplicar búsqueda de texto
    if busqueda:
        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 
                    df_f['BODEGA'].str.contains(busqueda, case=False)]
    
    # Aplicar filtro de origen
    if filtro_origen != "Todos":
        df_f = df_f[df_f['ORIGEN'] == filtro_origen]

    st.title(f"🍷 Catálogo 2026 ({len(df_f)} productos)")

    # Cuadrícula de productos
    if len(df_f) > 0:
        cols = st.columns(4)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 4]:
                url = row.get('URL', "")
                img_url = url if str(url).startswith("http") else "https://via.placeholder.com/200x300?text=Vino"
                st.image(img_url, use_container_width=True)
                
                st.markdown(f"**{row['VINO']}**")
                st.caption(f"{row['BODEGA']} | {row['ORIGEN']}")
                
                if st.button("Ver ficha", key=f"btn_{idx}"):
                    mostrar_detalles(row)
    else:
        st.warning("No se encontraron vinos con esos filtros.")
else:
    st.info("Asegúrate de que el archivo 'CATALOGO 2026 GLOP.xlsx' esté en la misma carpeta.")
