import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo de Vinos GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # Cargamos el archivo ignorando líneas malas y detectando el separador
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx - Hoja1.csv', 
            skiprows=1, 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None
        )
        
        # 1. Eliminamos columnas y filas que estén completamente vacías
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # 2. LIMPIEZA CRÍTICA DE COLUMNAS: Quitamos espacios y pasamos a mayúsculas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 3. Limpiamos los textos dentro de las celdas
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Error al procesar el CSV: {e}")
        return pd.DataFrame()

try:
    df = load_data()

    if df.empty:
        st.error("El archivo está vacío o no se pudo leer correctamente.")
    else:
        st.title("🍷 Catálogo de Vinos GLOP 2026")

        # Nombres de columnas normalizados (ahora todos están en MAYÚSCULAS y sin espacios)
        col_vino = 'VINO'
        col_bodega = 'BODEGA'
        col_origen = 'ORIGEN'
        col_url = 'URL'

        # Barra lateral
        st.sidebar.header("Filtros")
        busqueda = st.sidebar.text_input("Buscar vino o bodega...")
        
        opciones_origen = df[col_origen].unique() if col_origen in df.columns else []
        filtro_origen = st.sidebar.multiselect("Filtrar por Origen", options=opciones_origen)

        # Filtrado inteligente
        df_final = df.copy()
        if busqueda:
            mask = df_final[col_vino].str.contains(busqueda, case=False, na=False) | \
                   df_final[col_bodega].str.contains(busqueda, case=False, na=False)
            df_final = df_final[mask]
        
        if filtro_origen:
            df_final = df_final[df_final[col_origen].isin(filtro_origen)]

        # Mostrar resultados
        if df_final.empty:
            st.warning("No hay resultados para esta búsqueda.")
        else:
            cols = st.columns(3)
            for i, (index, row) in enumerate(df_final.iterrows()):
                with cols[i % 3]:
                    # Gestión de imagen
                    url_img = row.get(col_url, '')
                    if url_img and str(url_img).startswith('http'):
                        st.image(url_img, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x400?text=Vino+sin+foto", use_container_width=True)
                    
                    st.subheader(row.get(col_vino, 'Sin nombre'))
                    st.write(f"🏠 **Bodega:** {row.get(col_bodega, 'N/A')}")
                    st.write(f"🌍 **Origen:** {row.get(col_origen, 'N/A')}")
                    
                    # Precio (buscamos la columna de precio horeca)
                    precio = row.get('PRECIO HORECA', 'Consulte')
                    st.info(f"💰 Precio Horeca: {precio}€")
                    st.divider()

except Exception as e:
    st.error(f"Se ha producido un error inesperado: {e}")
