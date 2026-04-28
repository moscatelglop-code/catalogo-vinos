import streamlit as st
import pandas as pd

st.set_page_config(page_title="Catàleg Vins GLOP 2026", layout="wide")

@st.cache_data
def load_data():
    try:
        # Carreguem el fitxer amb la codificació correcta per a les tildes
        df = pd.read_csv(
            'CATALOGO 2026 GLOP.xlsx', 
            encoding='latin1', 
            sep=',',
            on_bad_lines='skip',
            engine='python'
        )
        
        # Eliminem files que estiguin totalment buides
        df = df.dropna(how='all', axis=0)
        
        # Netegem els noms de les columnes (tot a majúscules i sense espais)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Netegem els espais en blanc de les dades
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        
        return df
    except Exception as e:
        st.error(f"Error carregant les dades: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🍷 Catàleg de Vins GLOP 2026")

    # Buscador lateral
    st.sidebar.header("Cercador")
    terme = st.sidebar.text_input("Cerca per vi o celler...")

    # Filtre de seguretat: comprovem si les columnes existeixen
    col_vino = 'VINO' if 'VINO' in df.columns else df.columns[1]
    col_bodega = 'BODEGA' if 'BODEGA' in df.columns else df.columns[0]
    col_url = 'URL' if 'URL' in df.columns else df.columns[-1]

    # Lògica de filtrat
    df_f = df.copy()
    if terme:
        df_f = df_f[
            df_f[col_vino].str.contains(terme, case=False, na=False) |
            df_f[col_bodega].str.contains(terme, case=False, na=False)
        ]

    # Mostrar quadrícula
    if df_f.empty:
        st.warning("No s'han trobat vins.")
    else:
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 3]:
                # Gestió de la imatge
                url = row.get(col_url, "")
                if str(url).startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x400?text=Sense+Foto", use_container_width=True)
                
                # Dades del vi
                st.subheader(row.get(col_vino, "Vi"))
                st.write(f"🏠 **Celler:** {row.get(col_bodega, 'N/A')}")
                st.write(f"🌍 **Origen:** {row.get('ORIGEN', 'N/A')}")
                st.write(f"🍇 **Raïm:** {row.get('UVAS', 'N/A')}")
                
                # Preu Horeca
                preu = row.get('PRECIO HORECA', '')
                if preu:
                    st.info(f"💰 Preu Horeca: {preu}€")
                st.divider()

else:
    st.info("Esperant que el fitxer CSV estigui disponible a GitHub...")
