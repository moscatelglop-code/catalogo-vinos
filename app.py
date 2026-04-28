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
        
        # 1. Eliminamos la primera columna si es la 'Unnamed' (la que tiene comas vacías)
        if df.columns[0].startswith('Unnamed'):
            df = df.iloc[:, 1:]
        
        # 2. Eliminamos filas y columnas totalmente vacías
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
        # 3. Limpiamos espacios en blanco en todo el dataframe
        df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Sidebar para filtros
    st.sidebar.header("Buscador")
    busqueda = st.sidebar.text_input("Filtrar por nombre o bodega...")

    # Filtrado por posición: Columna 0 es BODEGA, Columna 1 es VINO
    df_f = df.copy()
    if busqueda:
        mask = (df_f.iloc[:, 1].str.contains(busqueda, case=False, na=False)) | \
               (df_f.iloc[:, 0].str.contains(busqueda, case=False, na=False))
        df_f = df_f[mask]

    if df_f.empty:
        st.warning("No se encontraron resultados para tu búsqueda.")
    else:
        # Cuadrícula de 3 columnas
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                # --- GESTIÓN SEGURA DE LA URL (Evita el AttributeError) ---
                # La URL está en la última columna (índice 9 o -1)
                url_raw = row.iloc[-1]
                url_str = str(url_raw) if pd.notnull(url_raw) else ""
                
                if url_str.startswith("http"):
                    st.image(url_str, use_container_width=True)
                else:
                    # Imagen de reemplazo si no hay URL válida
                    st.image("https://via.placeholder.com/300x400?text=Vino+sin+foto", use_container_width=True)
                
                # --- MOSTRAR DATOS POR POSICIÓN ---
                st.subheader(row.iloc[1]) # VINO
                st.write(f"🏠 **Bodega:** {row.iloc[0]}")
                st.write(f"🌍 **Origen:** {row.iloc[5]}") # ORIGEN
                
                # Precio Horeca (Índice 7)
                precio = row.iloc[7]
                st.info(f"💰 Precio Horeca: {precio}€")
                st.divider()
else:
    st.error("El archivo CSV no tiene el formato esperado o está vacío.")