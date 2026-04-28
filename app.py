import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo de Vinos GLOP 2026", layout="wide")

# Función para cargar datos de forma segura
@st.cache_data
def load_data():
    # Parámetros añadidos para evitar el error de tokenización:
    # 1. on_bad_lines='skip' -> Si una línea está mal, se la salta en lugar de romper la app.
    # 2. engine='python' -> Permite una lectura más flexible que el motor estándar de C.
    try:
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            skiprows=1, 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None  # Detecta automáticamente si es coma o punto y coma
        )
        
        # Eliminamos columnas totalmente vacías
        df = df.dropna(how='all', axis=1)
        
        # Limpiamos nombres de columnas y textos
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(['object']).columns:
            df[col] = df[col].str.strip()
            
        return df
    except Exception as e:
        st.error(f"Error al procesar el CSV: {e}")
        return pd.DataFrame() # Devuelve un dataframe vacío para que no explote la app
try:
    df = load_data()

    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # --- BUSCADOR Y FILTROS EN LA BARRA LATERAL ---
    st.sidebar.header("Filtros")
    busqueda = st.sidebar.text_input("Buscar vino o bodega...")
    
    # Usamos .get() o verificamos si la columna existe para evitar el NameError
    opciones_origen = df['ORIGEN'].unique() if 'ORIGEN' in df.columns else []
    filtro_origen = st.sidebar.multiselect("Filtrar por Origen", options=opciones_origen)

    # --- LÓGICA DE FILTRADO ---
    df_final = df.copy()
    
    if busqueda:
        df_final = df_final[
            df_final['VINO'].str.contains(busqueda, case=False, na=False) | 
            df_final['BODEGA'].str.contains(busqueda, case=False, na=False)
        ]
    
    if filtro_origen:
        df_final = df_final[df_final['ORIGEN'].isin(filtro_origen)]

    # --- MOSTRAR CATÁLOGO ---
    if df_final.empty:
        st.warning("No se encontraron vinos con esos filtros.")
    else:
        # Creamos una cuadrícula de 3 columnas
        cols = st.columns(3)
        for i, (index, row) in enumerate(df_final.iterrows()):
            with cols[i % 3]:
                # Mostrar imagen desde la URL del Excel
                url_img = row.get('URL', '')
                if pd.notna(url_img) and str(url_img).startswith('http'):
                    st.image(url_img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Sin+Foto", use_container_width=True)
                
                st.subheader(row['VINO'])
                st.caption(f"{row.get('BODEGA', '')} | {row.get('AÑADA', '')}")
                st.write(f"🍇 **Uvas:** {row.get('UVAS', 'N/A')}")
                st.write(f"📍 **Origen:** {row.get('ORIGEN', 'N/A')}")
                st.write(f"💰 **PVP Horeca:** {row.get('PRECIO HORECA', '0')}€")
                st.divider()

except Exception as e:
    st.error(f"Error crítico: {e}")
    st.info("Asegúrate de que el archivo CSV esté en la misma carpeta que app.py en GitHub.")
