import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # Cargamos el CSV saltando la primera fila vacía
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            skiprows=1, 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None
        )
        # 1. Eliminamos la primera columna si está vacía (la que desplaza todo)
        if df.columns[0].startswith('Unnamed'):
            df = df.iloc[:, 1:]
        
        # 2. Eliminamos filas totalmente vacías
        df = df.dropna(how='all', axis=0)
        
        # 3. Limpiamos espacios en los datos
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Mapeo por posición para evitar errores de nombres (KeyError)
    # Según tu archivo: 0:BODEGA, 1:VINO, 2:AÑADA, 3:UVAS, 5:ORIGEN, 7:PRECIO, 9:URL
    
    st.sidebar.header("Buscador")
    busqueda = st.sidebar.text_input("Filtrar por nombre...")

    # Filtrado por posición (columna 1 es VINO, columna 0 es BODEGA)
    df_f = df.copy()
    if busqueda:
        df_f = df_f[
            df_f.iloc[:, 1].str.contains(busqueda, case=False, na=False) | 
            df_f.iloc[:, 0].str.contains(busqueda, case=False, na=False)
        ]

    if df_f.empty:
        st.warning("No se encontraron resultados.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                # URL de imagen está en la última columna (índice 9 o -1)
                url = row.iloc[-1] 
                if url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Vino", use_container_width=True)
                
                # Acceso por índice para evitar el KeyError
                st.subheader(row.iloc[1]) # VINO
                st.write(f"**Bodega:** {row.iloc[0]}")
                st.write(f"**Origen:** {row.iloc[5]}") # ORIGEN
                st.info(f"Precio Horeca: {row.iloc[7]}€") # PRECIO HORECA
                st.divider()
else:
    st.error("No se pudo leer el contenido del catálogo.")
