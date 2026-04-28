import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # LEER EXCEL DIRECTAMENTE
        # Usamos engine='openpyxl' para archivos .xlsx
        df = pd.read_excel(
            'CATALOGO 2026 GLOP.xlsx', 
            engine='openpyxl'
        )
        
        # Limpieza de columnas y filas vacías
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # Normalizar nombres de columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Limpiar espacios en los datos
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error al abrir el Excel: {e}")
        st.info("Nota: Asegúrate de tener 'openpyxl' en tu archivo requirements.txt")
        return pd.DataFrame()

# --- REQUISITO IMPORTANTE ---
# En tu archivo 'requirements.txt' de GitHub DEBES tener:
# streamlit
# pandas
# openpyxl

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Buscador
    busqueda = st.sidebar.text_input("Buscar vino o bodega...")

    # Identificar columnas
    c_vino = next((c for c in df.columns if 'VINO' in c), df.columns[0])
    c_bodega = next((c for c in df.columns if 'BODEGA' in c), df.columns[1])
    c_url = next((c for c in df.columns if 'URL' in c), None)

    df_f = df.copy()
    if busqueda:
        df_f = df_f[
            df_f[c_vino].str.contains(busqueda, case=False, na=False) |
            df_f[c_bodega].str.contains(busqueda, case=False, na=False)
        ]

    # Mostrar catálogo
    cols = st.columns(3)
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 3]:
            # Imagen
            if c_url and str(row[c_url]).startswith("http"):
                st.image(row[c_url], use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x400?text=Vino", use_container_width=True)
            
            st.subheader(row[c_vino])
            st.write(f"🏠 **Bodega:** {row[c_bodega]}")
            
            # Precio (Buscamos cualquier columna que diga HORECA o PRECIO)
            c_precio = next((c for c in df.columns if 'HORECA' in c or 'PRECIO' in c), None)
            if c_precio:
                st.info(f"💰 Precio: {row[c_precio]}€")
            st.divider()
