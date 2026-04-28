import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # 1. Leemos el archivo con sep=None para que Pandas adivine si es , o ;
        # Usamos engine='python' para que la autodetección funcione
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            encoding='latin1', 
            sep=None, 
            engine='python',
            on_bad_lines='skip'
        )

        # 2. Si la primera columna no tiene nombre (Unnamed), la eliminamos
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 3. Eliminamos filas totalmente vacías
        df = df.dropna(how='all', axis=0)

        # 4. Limpiamos los nombres de las columnas (Quitar espacios y a Mayúsculas)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 5. Convertimos todo el contenido a texto limpio
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error cargando el archivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # --- SISTEMA DE SEGURIDAD PARA COLUMNAS ---
    # Buscamos las columnas por nombre, si no existen, usamos la primera que encontre
    def get_col(name, default_idx):
        if name in df.columns:
            return name
        return df.columns[default_idx] if len(df.columns) > default_idx else df.columns[0]

    c_vino = get_col('VINO', 1)
    c_bodega = get_col('BODEGA', 0)
    c_url = get_col('URL', -1)
    c_horeca = get_col('PRECIO HORECA', 7) # Intentamos buscar el precio

    # Buscador
    st.sidebar.header("Filtros")
    termino = st.sidebar.text_input("Buscar vino o bodega...")

    df_f = df.copy()
    if termino:
        df_f = df_f[
            df_f[c_vino].str.contains(termino, case=False, na=False) |
            df_f[c_bodega].str.contains(termino, case=False, na=False)
        ]

    if df_f.empty:
        st.warning("No se encontraron resultados.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                # Imagen
                url = row.get(c_url, "")
                if str(url).startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Vino", use_container_width=True)
                
                # Datos
                st.subheader(row[c_vino])
                st.write(f"🏠 **Bodega:** {row[c_bodega]}")
                
                # Buscamos el precio si existe
                if c_horeca in row:
                    st.info(f"💰 Precio Horeca: {row[c_horeca]}€")
                st.divider()
else:
    st.info("Sube el archivo a GitHub para visualizar el catálogo.")
