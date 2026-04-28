import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# Estilo CSS personalizado para forzar el tamaño de las imágenes
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 350px;
        object-fit: contain;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Intentamos leer como Excel dado que el archivo parece ser un binario .xlsx
        # Si fallara, cambiar a pd.read_csv con los parámetros anteriores
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        
        # Limpieza de columnas y filas vacías
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # Normalizar nombres de columnas (Mayúsculas y sin espacios)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Limpiar espacios en los datos
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception:
        # Si no es un Excel real, lo leemos como CSV con la limpieza de comas
        df = pd.read_csv('CATALOGO 2026 GLOP.xlsx - Hoja1.csv', encoding='latin1', skiprows=1, on_bad_lines='skip')
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Buscador lateral
    busqueda = st.sidebar.text_input("Buscar vino o bodega...")

    # Identificación de columnas críticas
    c_vino = next((c for c in df.columns if 'VINO' in c), None)
    c_bodega = next((c for c in df.columns if 'BODEGA' in c), None)
    c_url = next((c for c in df.columns if 'URL' in c), None)
    c_horeca = next((c for c in df.columns if 'HORECA' in c and 'COMPRA' not in c), None)

    df_f = df.copy()
    if busqueda and c_vino and c_bodega:
        df_f = df_f[
            df_f[c_vino].str.contains(busqueda, case=False, na=False) |
            df_f[c_bodega].str.contains(busqueda, case=False, na=False)
        ]

    # Mostrar catálogo
    if df_f.empty:
        st.warning("No se han encontrado resultados.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                # Imagen con tamaño controlado por el CSS de arriba
                url = row.get(c_url, "") if c_url else ""
                if str(url).startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Sin+Imagen", use_container_width=True)
                
                # Datos del vino
                st.subheader(row.get(c_vino, "Vino"))
                st.write(f"🏠 **Bodega:** {row.get(c_bodega, 'N/A')}")
                
                # Mostrar SOLO precio Horeca si existe
                if c_horeca:
                    precio = row.get(c_horeca, "")
                    if precio and precio != "0":
                        st.info(f"💰 Precio Horeca: {precio}€")
                
                st.divider()
