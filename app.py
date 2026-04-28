import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Catálogo de Vinos GLOP 2026", layout="wide")

# Cargar los datos del CSV que subiste
# El parámetro encoding='latin1' permite leer la Ñ y las tildes sin errores
try:
    df = pd.read_csv('CATALOGO 2026 GLOP.xlsx - Hoja1.csv', skiprows=1, encoding='latin1')
    # Limpiamos columnas vacías que suelen aparecer en exportaciones de Excel
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
except Exception as e:
    st.error(f"Error de lectura: {e}")

st.title("🍷 Catálogo de Vinos GLOP 2026")
st.sidebar.header("Filtros de Búsqueda")

# Buscador y Filtros
busqueda = st.sidebar.text_input("Buscar vino o bodega")
filtro_origen = st.sidebar.multiselect("Origen/D.O.", options=df['ORIGEN'].unique())

# Lógica de filtrado
df_final = df.copy()
if busqueda:
    df_final = df_final[df_final['VINO'].str.contains(busqueda, case=False) | df_final['BODEGA'].str.contains(busqueda, case=False)]
if filtro_origen:
    df_final = df_final[df_final['ORIGEN'].isin(filtro_origen)]

# Mostrar el catálogo en cuadrícula
cols = st.columns(3)
for i, (index, row) in enumerate(df_final.iterrows()):
    with cols[i % 3]:
        st.image(row['URL'], use_container_width=True)
        st.subheader(f"{row['VINO']} ({row['AÑADA']})")
        st.write(f"**Bodega:** {row['BODEGA']}")
        st.write(f"**Uva:** {row['UVAS']}")
        st.write(f"**Precio Horeca:** {row['PRECIO HORECA']}€")
        st.button(f"Ver detalles {row['VINO']}", key=index)
        st.divider()
