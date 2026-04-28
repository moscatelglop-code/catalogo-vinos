import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Catálogo GLOP 2026", layout="wide")

def limpiar_texto(texto):
    """Limpia el texto para facilitar la búsqueda de columnas"""
    texto = str(texto).upper()
    # Eliminar tildes y caracteres especiales
    texto = re.sub(r'[ÁÉÍÓÚ]', lambda x: {'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U'}[x.group()], texto)
    return re.sub(r'[^A-Z0-9]', '', texto)

@st.cache_data
def load_data():
    try:
        # Cargamos el archivo
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            skiprows=1, 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None
        )
        
        # 1. Quitar columnas vacías al principio y al final
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(how='all', axis=0)
        
        # 2. Limpiar datos de las celdas (usamos map para compatibilidad)
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error cargando el archivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- DETECCIÓN DINÁMICA DE COLUMNAS ---
    # Limpiamos los nombres de las columnas para encontrarlas sí o sí
    columnas_limpias = {limpiar_texto(col): col for col in df.columns}
    
    # Buscamos las claves simplificadas
    c_vino = columnas_limpias.get('VINO')
    c_bodega = columnas_limpias.get('BODEGA')
    c_url = columnas_limpias.get('URL')
    c_precio = columnas_limpias.get('PRECIOHORECA') or columnas_limpias.get('HORECA')
    c_origen = columnas_limpias.get('ORIGEN')

    # Si no encuentra 'VINO', usamos la segunda columna por defecto
    if not c_vino: c_vino = df.columns[1]
    if not c_bodega: c_bodega = df.columns[0]
    if not c_url: c_url = df.columns[-1]

    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Buscador
    st.sidebar.header("Buscador")
    termino = st.sidebar.text_input("Nombre del vino o bodega...")

    df_f = df.copy()
    if termino:
        # Filtrado ultra-seguro
        mask = df_f[c_vino].str.contains(termino, case=False, na=False) | \
               df_f[c_bodega].str.contains(termino, case=False, na=False)
        df_f = df_f[mask]

    if df_f.empty:
        st.warning("No hay resultados.")
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
                if c_origen: st.write(f"🌍 **Origen:** {row[c_origen]}")
                if c_precio: st.info(f"💰 Horeca: {row[c_precio]}€")
                st.divider()
else:
    st.info("Sube el archivo CSV a GitHub para empezar.")
