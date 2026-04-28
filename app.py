import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catálogo Vinos 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # 1. Probamos con la codificación típica de Excel en español para evitar caracteres raros
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            skiprows=1, 
            encoding='latin1', 
            sep=',',
            on_bad_lines='skip',
            engine='python'
        )

        # 2. LIMPIEZA RADICAL DE COLUMNAS VACÍAS
        # Esto elimina esa primera columna de comas que desplaza todo
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(how='all', axis=1) # Elimina columnas que sean todo nulos
        df = df.dropna(how='all', axis=0) # Elimina filas vacías

        # 3. NORMALIZAR NOMBRES DE COLUMNAS
        # Quitamos espacios, puntos y pasamos a mayúsculas
        df.columns = [str(c).strip().upper().replace('.', '').replace(' ', '') for c in df.columns]

        # 4. LIMPIAR DATOS DE LAS CELDAS
        # Convertimos todo a texto limpio para que no falle la búsqueda
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Mostramos un buscador que mire en "VINO" y "BODEGA"
    # Intentamos detectar las columnas incluso si han cambiado de nombre
    c_vino = next((c for c in df.columns if 'VINO' in c), df.columns[1])
    c_bodega = next((c for c in df.columns if 'BODEGA' in c), df.columns[0])
    c_url = next((c for c in df.columns if 'URL' in c), df.columns[-1])
    c_origen = next((c for c in df.columns if 'ORIGEN' in c), None)
    c_precio = next((c for c in df.columns if 'HORECA' in c), None)

    busqueda = st.sidebar.text_input("Buscar vino o bodega...")

    df_final = df.copy()
    if busqueda:
        # Buscamos ignorando tildes y mayúsculas
        df_final = df_final[
            df_final[c_vino].str.contains(busqueda, case=False, na=False) |
            df_final[c_bodega].str.contains(busqueda, case=False, na=False)
        ]

    if df_final.empty:
        st.warning("No se encontraron vinos.")
    else:
        # Cuadrícula
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_final.iterrows()):
            with cols[i % 3]:
                # Imagen
                url = row[c_url]
                if url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Vino", use_container_width=True)
                
                # Texto (usamos .get por si acaso)
                st.subheader(row[c_vino])
                st.write(f"🏠 **Bodega:** {row[c_bodega]}")
                
                if c_origen:
                    st.write(f"📍 **Origen:** {row[c_origen]}")
                
                if c_precio:
                    # Intentamos que el precio se vea bien
                    st.success(f"Precio Horeca: {row[c_precio]}€")
                
                st.divider()

    # Pestaña de ayuda técnica por si algo falla
    with st.expander("Ayuda: Si no ves los datos correctamente"):
        st.write("Columnas detectadas actualmente:", list(df.columns))
        st.write("Vista previa de los datos:")
        st.dataframe(df.head())
else:
    st.error("El archivo CSV no se ha cargado. Verifica que el nombre en GitHub sea exacto.")
