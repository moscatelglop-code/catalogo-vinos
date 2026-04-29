import streamlit as st

import pandas as pd

from fpdf import FPDF

import io

import requests

from tempfile import NamedTemporaryFile



st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")



# --- ESTILOS CSS ---

st.markdown("""

    <style>

    [data-testid="stImage"] img {

        height: 250px;

        object-fit: contain;

        background-color: #ffffff;

        border-radius: 10px;

    }

    .stButton>button { width: 100%; border-radius: 10px; }

    .selected-card {

        border: 2px solid #722f37;

        padding: 10px;

        border-radius: 10px;

        background-color: #fff4f5;

    }

    </style>

    """, unsafe_allow_html=True)



@st.cache_data

def load_data():

    try:

        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')

        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)

        df.columns = [str(c).strip().upper() for c in df.columns]

        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")

        return df

    except Exception as e:

        st.error(f"Error al abrir el archivo Excel: {e}")

        return pd.DataFrame()



# --- FUNCIÓN GENERAR PDF ---

def generar_pdf(vinos_seleccionados):

    pdf = FPDF()

    pdf.add_page()

    

    # Título

    pdf.set_font("helvetica", "B", 16)

    pdf.set_text_color(114, 47, 55) 

    pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=1, align='C')

    pdf.ln(10)

    

    # Cabecera para peticiones (evita bloqueos)

    headers = {'User-Agent': 'Mozilla/5.0'}



    for _, row in vinos_seleccionados.iterrows():

        y_inicial = pdf.get_y()

        url_img = str(row.get('URL', ""))

        

        img_mostrada = False

        img_h_final = 0 # Guardaremos el alto calculado

        

        # --- INTENTO DE DESCARGA DE IMAGEN ---

        if url_img.startswith("http"):

            try:

                # Descargamos la imagen

                res = requests.get(url_img, headers=headers, timeout=10)

                if res.status_code == 200:

                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:

                        tmp.write(res.content)

                        tmp_path = tmp.name

                    

                    # --- ESCALADO PROPORCIONAL ---

                    # TRUCO: Definimos un alto fijo (20mm) y ancho=0.

                    # FPDF calculará el alto proporcional automáticamente.

                    info = pdf.image(tmp_path, x=10, y=y_inicial, w=0, h=20)

                    

                    # Obtenemos el alto que FPDF calculó para usarlo en el espaciado

                    img_h_final = info.h

                    img_mostrada = True

            except Exception as e:

                print(f"Error con imagen de {url_img}: {e}")



        # --- CONTENIDO DE TEXTO ---

        # El texto siempre alineado en x=35 para que se vea ordenado

        pdf.set_xy(35, y_inicial)

        

        # Nombre del Vino

        pdf.set_font("helvetica", "B", 12)

        pdf.set_text_color(114, 47, 55)

        nombre = str(row.get('VINO', 'Vino')).encode('latin-1', 'ignore').decode('latin-1')

        pdf.cell(0, 7, nombre, ln=1)

        

        # Detalles (Añada, Bodega)

        pdf.set_x(35)

        pdf.set_font("helvetica", "", 10)

        pdf.set_text_color(0, 0, 0)

        

        bodega = str(row.get('BODEGA', 'N/A')).encode('latin-1', 'ignore').decode('latin-1')

        anada = str(row.get('AÑADA', row.get('AÑO', 'N/A'))).encode('latin-1', 'ignore').decode('latin-1')

        origen = str(row.get('ORIGEN', 'N/A')).encode('latin-1', 'ignore').decode('latin-1')

        

        pdf.cell(0, 6, f"Bodega: {bodega} | Añada: {anada}", ln=1)

        pdf.set_x(35)

        pdf.cell(0, 6, f"Origen: {origen}", ln=1)

        

        # Precio

        pdf.set_x(35)

        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)

        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"

        pdf.set_font("helvetica", "B", 10)

        pdf.cell(0, 6, f"Precio Horeca: {precio}", ln=1)



        # --- ESPACIADO DINÁMICO ---

        # Calculamos dónde termina el vino actual basándonos en:

        # El final del texto (pdf.get_y()) O el final de la imagen (y_inicial + alto_imagen).

        

        # Le damos un mínimo de 25mm de alto por vino para que no queden muy pegados.

        fin_de_texto = pdf.get_y()

        fin_de_imagen = y_inicial + img_h_final

        

        proximo_y = max(fin_de_texto, fin_de_imagen, y_inicial + 25)

        

        pdf.set_y(proximo_y + 3) # Margen de 3mm antes de la línea

        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Línea divisoria

        pdf.ln(5) # Margen de 5mm después de la línea



        # Salto de página automático si estamos muy abajo

        if pdf.get_y() > 260:

            pdf.add_page()



    return bytes(pdf.output())

df = load_data()



# --- ESTADO DE SELECCIÓN ---

if 'seleccionados' not in st.session_state:

    st.session_state.seleccionados = []



# --- SIDEBAR ---

with st.sidebar:

    try:

        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)

    except:

        st.title("🍷 GLOP DYD")

    

    st.divider()

    busqueda = st.text_input("🔍 Buscar vino o bodega...")

    

    # Botón de exportar

    st.subheader("📄 Exportación")

    if st.session_state.seleccionados:

        df_export = df[df.index.isin(st.session_state.seleccionados)]

        pdf_data = generar_pdf(df_export)

        st.download_button(

            label="📥 Descargar PDF Seleccionados",

            data=pdf_data,

            file_name="catalogo_seleccionado_glop.pdf",

            mime="application/pdf",

            type="primary"

        )

        if st.button("Limpiar selección"):

            st.session_state.seleccionados = []

            st.rerun()

    else:

        st.info("Selecciona vinos en el catálogo para exportar.")



# --- CUADRÍCULA ---

if not df.empty:

    df_f = df.copy()

    if busqueda:

        df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) | 

                    df_f['BODEGA'].str.contains(busqueda, case=False)]



    st.title("🍷 Catálogo Digital")

    

    cols = st.columns(4)

    for i, (idx, row) in enumerate(df_f.iterrows()):

        with cols[i % 4]:

            # Checkbox de selección

            seleccionado = st.checkbox("Seleccionar", key=f"sel_{idx}", 

                                     value=idx in st.session_state.seleccionados)

            

            if seleccionado and idx not in st.session_state.seleccionados:

                st.session_state.seleccionados.append(idx)

            elif not seleccionado and idx in st.session_state.seleccionados:

                st.session_state.seleccionados.remove(idx)



            url = row.get('URL', "")

            img_url = url if str(url).startswith("http") else "https://via.placeholder.com/200x300?text=Vino"

            st.image(img_url, use_container_width=True)

            

            st.markdown(f"**{row['VINO']}**")

            st.caption(f"{row['BODEGA']}")

            

            # Mostrar precio rápido si existe

            c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)

            if c_horeca:

                st.write(f"**{row[c_horeca]}€**")
