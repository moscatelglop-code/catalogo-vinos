import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# Estilo para imágenes uniformes y tarjetas
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
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Intentamos leer el archivo (ajusta el nombre si lo cambiaste)
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx - Hoja1.csv', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except:
        # Fallback si el archivo se lee como CSV
        df = pd.read_csv('CATALOGO 2026 GLOP.xlsx', encoding='latin1', on_bad_lines='skip')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df

# Función que define la "hoja" de características (Ventana emergente)
@st.dialog("Detalles del Vino")
def mostrar_detalles(row):
    col1, col2 = st.columns([1, 2])
    
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
        
        # Lista de todas las características disponibles
        st.write(f"📍 **Origen/D.O.:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"🍇 **Variedades:** {row.get('UVAS', 'N/A')}")
        st.write(f"📅 **Añada:** {row.get('AÑADA', 'N/A')}")
        
        # Mostrar precio solo si no es compra
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Horeca", value=f"{row[c_horeca]}€")
        
        # Si tienes columnas de notas de cata o descripción, aparecerán aquí
        if 'NOTAS' in row.index and row['NOTAS']:
            st.write(f"📝 **Notas de cata:** {row['NOTAS']}")

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")
    busqueda = st.sidebar.text_input("🔍 Buscar vino o bodega...")

    # Identificar columnas básicas
    c_vino = next((c for c in df.columns if 'VINO' in c), df.columns[0])
    c_bodega = next((c for c in df.columns if 'BODEGA' in c), df.columns[1])
    c_url = next((c for c in df.columns if 'URL' in c), None)

    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f[c_vino].str.contains(busqueda, case=False, na=False) | 
                    df_f[c_bodega].str.contains(busqueda, case=False, na=False)]

    # Cuadrícula principal
    cols = st.columns(4) # 4 columnas para que se vea más tipo catálogo
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            # Imagen pequeña para la vista general
            url = row.get(c_url, "")
            if str(url).startswith("http"):
                st.image(url, use_container_width=True)
            else:
                st.image("https://via.placeholder.com/200x300?text=Vino", use_container_width=True)
            
            st.markdown(f"**{row[c_vino]}**")
            st.caption(f"{row[c_bodega]}")
            
            # El botón que dispara la "hoja" de características
            if st.button("Ver detalles", key=f"btn_{idx}"):
                mostrar_detalles(row)
            st.write("") # Espaciado
else:
    st.info("Cargando base de datos...")
