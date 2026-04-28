import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # Cargamos el archivo (ahora sin skiprows porque ya borraste la columna/fila vacía)
        # Si sigue habiendo una fila vacía arriba, usa skiprows=1
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx - Hoja1.csv', 
            encoding='latin1', 
            sep=',',
            on_bad_lines='skip',
            engine='python'
        )

        # 1. Limpieza básica
        df = df.dropna(how='all', axis=0) # Quitar filas vacías
        
        # 2. Normalizar nombres de columnas (quitar espacios y a MAYÚSCULAS)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 3. Limpiar los datos de las celdas
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Buscador en la barra lateral
    st.sidebar.header("Filtros")
    busqueda = st.sidebar.text_input("Buscar vino o bodega...")

    # Filtrado (buscamos en las columnas VINO y BODEGA)
    df_final = df.copy()
    if busqueda:
        df_final = df_final[
            df_final['VINO'].str.contains(busqueda, case=False, na=False) |
            df_final['BODEGA'].str.contains(busqueda, case=False, na=False)
        ]

    if df_final.empty:
        st.warning("No se encontraron resultados.")
    else:
        # Mostrar catálogo en 3 columnas
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_final.iterrows()):
            with cols[i % 3]:
                # Gestión de la imagen
                url = row.get('URL', '')
                if url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Vino", use_container_width=True)
                
                # Datos del vino
                st.subheader(row.get('VINO', 'Vino'))
                st.write(f"🏠 **Bodega:** {row.get('BODEGA', 'N/A')}")
                st.write(f"🌍 **Origen:** {row.get('ORIGEN', 'N/A')}")
                st.write(f"🍇 **Uvas:** {row.get('UVAS', 'N/A')}")
                
                # Precio destacado
                precio = row.get('PRECIO HORECA', '')
                if precio:
                    st.info(f"💰 Precio Horeca: {precio}€")
                st.divider()

else:
    st.warning("Por favor, asegúrate de que el archivo CSV esté subido a GitHub con el nombre correcto.")
