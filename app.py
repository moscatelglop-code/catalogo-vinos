import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Catálogo Vinos 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # 1. Leer el archivo como texto plano primero para limpiar las comas iniciales
        with open('CATALOGO 2026 GLOP.xlsx', 'r', encoding='latin1') as f:
            lineas = f.readlines()
        
        # 2. Limpieza manual: Quitamos la primera coma de cada línea y filtramos líneas vacías
        lineas_limpias = []
        for l in lineas:
            l = l.strip()
            if l.startswith(','):
                l = l[1:] # Quita la primera coma que desplaza todo
            if len(l) > 10: # Solo líneas con contenido real
                lineas_limpias.append(l)
        
        # 3. Convertir de nuevo a DataFrame
        csv_limpio = io.StringIO('\n'.join(lineas_limpias))
        df = pd.read_csv(csv_limpio, sep=',', on_bad_lines='skip')

        # 4. Limpieza de nombres de columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # 5. Limpieza de datos (quitar espacios y caracteres raros de control)
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
            
        return df
    except Exception as e:
        st.error(f"Error crítico al procesar el archivo: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catálogo de Vinos GLOP 2026")

    # Buscador lateral
    busqueda = st.sidebar.text_input("Buscar por nombre de vino o bodega")

    # Filtrar (Usamos posiciones para que sea infalible)
    # Columna 0: BODEGA, Columna 1: VINO, Columna 7: PRECIO HORECA, Columna 9: URL
    df_f = df.copy()
    if busqueda:
        mask = df_f.iloc[:, 1].str.contains(busqueda, case=False, na=False) | \
               df_f.iloc[:, 0].str.contains(busqueda, case=False, na=False)
        df_f = df_f[mask]

    # Mostrar resultados
    if df_f.empty:
        st.warning("No se encontraron resultados.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                # Imagen (Columna 9 es la URL)
                url = row.iloc[9] if len(row) > 9 else ""
                if str(url).startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Sin+Foto", use_container_width=True)
                
                # Datos por posición
                st.subheader(row.iloc[1]) # VINO
                st.write(f"🏠 **Bodega:** {row.iloc[0]}")
                st.write(f"🌍 **Origen:** {row.iloc[5]}") # ORIGEN
                
                precio = row.iloc[7] # PRECIO HORECA
                st.info(f"💰 PVP Horeca: {precio}€")
                st.divider()
else:
    st.warning("No se pudo cargar la base de datos. Comprueba el nombre del archivo en GitHub.")
