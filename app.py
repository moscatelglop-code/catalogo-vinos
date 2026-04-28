import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo de Vinos GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # Cargamos el archivo saltando la primera fila de comas vacías
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            skiprows=1, 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None
        )
        
        # ELIMINAR COLUMNAS VACÍAS (Esto quita la primera columna sin nombre que desplaza todo)
        df = df.dropna(how='all', axis=1)
        
        # Limpiar nombres de columnas: quitar espacios y pasar a MAYÚSCULAS
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Limpiar los datos de las celdas
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("No se han podido cargar los datos. Revisa el nombre del archivo en GitHub.")
else:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Identificar columnas dinámicamente por si acaso
    # Buscamos la que contenga la palabra VINO, BODEGA, etc.
    def find_col(name, columns):
        for c in columns:
            if name in c: return c
        return None

    c_vino = find_col('VINO', df.columns)
    c_bodega = find_col('BODEGA', df.columns)
    c_origen = find_col('ORIGEN', df.columns)
    c_url = find_col('URL', df.columns)
    c_precio = find_col('HORECA', df.columns)

    # BARRA LATERAL
    st.sidebar.header("Buscador")
    busqueda = st.sidebar.text_input("Vino o Bodega")
    
    filtro_origen = []
    if c_origen:
        opciones = sorted(df[c_origen].unique())
        filtro_origen = st.sidebar.multiselect("Origen", opciones)

    # FILTRADO
    df_f = df.copy()
    if busqueda:
        df_f = df_f[df_f[c_vino].str.contains(busqueda, case=False, na=False) | 
                    df_f[c_bodega].str.contains(busqueda, case=False, na=False)]
    if filtro_origen:
        df_f = df_f[df_f[c_origen].isin(filtro_origen)]

    # MOSTRAR VINOS
    if df_f.empty:
        st.info("No hay vinos que coincidan con la búsqueda.")
    else:
        # Cuadrícula de 3 columnas
        grid = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with grid[i % 3]:
                # Imagen
                url = row.get(c_url, "")
                if isinstance(url, str) and url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x450?text=Foto+no+disponible", use_container_width=True)
                
                # Info
                st.subheader(row[c_vino])
                st.write(f"**{row[c_bodega]}**")
                st.caption(f"📍 {row.get(c_origen, 'N/A')} | 📅 {row.get('AÑADA', '')}")
                
                if c_precio:
                    st.success(f"Precio Horeca: {row[c_precio]}€")
                st.divider()

    # DIAGNÓSTICO (Solo si quieres ver qué pasa por detrás, puedes borrar esto luego)
    with st.expander("Ver estructura técnica del archivo"):
        st.write("Columnas detectadas:", list(df.columns))
        st.dataframe(df.head())
