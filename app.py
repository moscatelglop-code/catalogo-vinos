 import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # 1. Intentamos leer el archivo. 
        # Si el nombre en GitHub es distinto, cámbialo aquí:
        nombre_archivo = 'CATALOGO 2026 GLOP.xlsx'
        
        df = pd.read_csv(
            nombre_archivo, 
            skiprows=1, 
            encoding='latin1', 
            on_bad_lines='skip', 
            engine='python',
            sep=None
        )
        
        # 2. Limpieza de columnas fantasma (las que crea Excel por las comas iniciales)
        # Eliminamos columnas que no tengan nombre o sean 'Unnamed'
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 3. Eliminar filas totalmente vacías
        df = df.dropna(how='all', axis=0)
        
        # 4. Convertir todo a texto y limpiar espacios (Usando .map para evitar el AttributeError)
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        
        # 5. Normalizar nombres de columnas para que el código las encuentre fácil
        df.columns = [str(c).strip().upper() for c in df.columns]
            
        return df
    except Exception as e:
        st.error(f"Error técnico al leer el CSV: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Identificar columnas críticas
    # Buscamos la columna que contenga "VINO", "BODEGA", "URL", etc.
    def buscar_col(lista, palabra):
        for c in lista:
            if palabra in c: return c
        return None

    c_vino = buscar_col(df.columns, 'VINO')
    c_bodega = buscar_col(df.columns, 'BODEGA')
    c_precio = buscar_col(df.columns, 'HORECA')
    c_url = buscar_col(df.columns, 'URL')
    c_origen = buscar_col(df.columns, 'ORIGEN')

    # Buscador lateral
    st.sidebar.header("Buscador")
    termino = st.sidebar.text_input("Escribe nombre o bodega...")

    df_mostrar = df.copy()
    if termino:
        # Filtrado flexible
        df_mostrar = df_mostrar[
            df_mostrar[c_vino].str.contains(termino, case=False, na=False) |
            df_mostrar[c_bodega].str.contains(termino, case=False, na=False)
        ]

    if df_mostrar.empty:
        st.warning("No hay vinos para mostrar con ese filtro.")
    else:
        # Mostrar en cuadrícula de 3
        filas = st.columns(3)
        for i, (idx, row) in enumerate(df_mostrar.iterrows()):
            with filas[i % 3]:
                # Imagen con validación
                url = row.get(c_url, "")
                if url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Sin+Imagen", use_container_width=True)
                
                # Datos del vino
                st.subheader(row.get(c_vino, "Vino desconocido"))
                st.write(f"🏷️ **Bodega:** {row.get(c_bodega, 'N/A')}")
                st.write(f"📍 **Origen:** {row.get(c_origen, 'N/A')}")
                
                if c_precio:
                    st.success(f"Precio Horeca: {row[c_precio]}€")
                st.divider()

else:
    st.warning("Esperando a que el archivo CSV esté disponible en el repositorio...")
