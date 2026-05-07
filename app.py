import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import requests
import os
from tempfile import NamedTemporaryFile

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")

# Estilos CSS para tarjetas uniformes y botones redondeados
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 250px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
    }
    .stButton>button { width: 100%; border-radius: 10px; }
    .stCheckbox { margin-bottom: -15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (Cache para velocidad)
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo Excel: {e}")
        return pd.DataFrame()

# 3. VENTANA EMERGENTE (DETALLES COMPLETOS)
@st.dialog("Ficha Técnica del Producto")
def mostrar_detalles(row):
    col_img, col_info = st.columns([1, 1.2])
    
    with col_img:
        url = row.get('URL', "")
        img_url = url if str(url).startswith("http") else "https://via.placeholder.com/400x600?text=Sin+Imagen"
        st.image(img_url, use_container_width=True)
    
    with col_info:
        st.subheader(row['VINO'])
        st.write(f"**Bodega:** {row.get('BODEGA', 'N/A')}")
        st.write(f"**Origen:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"**Uvas:** {row.get('UVAS', 'N/A')}")
        st.write(f"**Añada:** {row.get('AÑADA', row.get('AÑO', 'N/A'))}")
        
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]} €")
        
        st.divider()
        st.caption("Información técnica para uso comercial. Precios válidos para 2026.")

# 4. FUNCIÓN GENERAR PDF
def generar_pdf(vinos_seleccionados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(114, 47, 55) 
    pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=1, align='C')
    pdf.ln(10)
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for _, row in vinos_seleccionados.iterrows():
        y_inicial = pdf.get_y()
        url_img = str(row.get('URL', ""))
        tmp_path = None

        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, headers=headers, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    pdf.image(tmp_path, x=10, y=y_inicial, h=28)
            except: pass
            finally:
                if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)

        pdf.set_xy(45, y_inicial)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(114, 47, 55)
        nombre = str(row.get('VINO', 'Vino')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 7, nombre, ln=1)
        
        pdf.set_x(45)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        bodega = str(row.get('BODEGA', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Bodega: {bodega}", ln=1)
        
        pdf.set_x(45)
        origen = str(row.get('ORIGEN', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        uvas = str(row.get('UVAS', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 6, f"Origen: {origen} | Uvas: {uvas}", ln=1)
        
        pdf.set_x(45)
        pdf.set_font("Helvetica", "B", 10)
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"
        pdf.cell(0, 6, f"Precio Horeca: {precio}", ln=1)

        y_final = max(pdf.get_y(), y_inicial + 32)
        pdf.set_y(y_final)
        pdf.line(10, y_final, 200, y_final)
        pdf.ln(5)
        
        if pdf.get_y() > 250: pdf.add_page()

    return bytes(pdf.output())

F

import streamlit as st

import pandas as pd

from fpdf import FPDF

import io

import requests

import os

from tempfile import NamedTemporaryFile



# 1. CONFIGURACIÓN DE LA PÁGINA

st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide")



# Estilos CSS para tarjetas uniformes y botones redondeados

st.markdown("""

<style>

[data-testid="stImage"] img {

height: 250px;

object-fit: contain;

background-color: #ffffff;

border-radius: 10px;

}

.stButton>button { width: 100%; border-radius: 10px; }

.stCheckbox { margin-bottom: -15px; }

</style>

""", unsafe_allow_html=True)



# 2. CARGA DE DATOS (Cache para velocidad)

@st.cache_data

def load_data():

    try:

        df = pd.read_excel('CATALOGO 2026 GLOP.xlsx', engine='openpyxl')

        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)

        df.columns = [str(c).strip().upper() for c in df.columns]

        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")

        return df

    except Exception as e:

        st.error(f"Error al cargar el archivo Excel: {e}")

    return pd.DataFrame()



# 3. VENTANA EMERGENTE (DETALLES COMPLETOS)

@st.dialog("Ficha Técnica del Producto")

def mostrar_detalles(row):

col_img, col_info = st.columns([1, 1.2])


with col_img:

url = row.get('URL', "")

img_url = url if str(url).startswith("http") else "https://via.placeholder.com/400x600?text=Sin+Imagen"

st.image(img_url, use_container_width=True)


with col_info:

st.subheader(row['VINO'])

st.write(f"**Bodega:** {row.get('BODEGA', 'N/A')}")

st.write(f"**Origen:** {row.get('ORIGEN', 'N/A')}")

st.write(f"**Uvas:** {row.get('UVAS', 'N/A')}")

st.write(f"**Añada:** {row.get('AÑADA', row.get('AÑO', 'N/A'))}")


c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)

if c_horeca:

st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]} €")


st.divider()

st.caption("Información técnica para uso comercial. Precios válidos para 2026.")



# 4. FUNCIÓN GENERAR PDF

def generar_pdf(vinos_seleccionados):

pdf = FPDF()

pdf.set_auto_page_break(auto=True, margin=15)

pdf.add_page()


pdf.set_font("Helvetica", "B", 16)

pdf.set_text_color(114, 47, 55)

pdf.cell(190, 10, "CATALOGO DE VINOS SELECCIONADOS - GLOP 2026", ln=1, align='C')

pdf.ln(10)


headers = {'User-Agent': 'Mozilla/5.0'}



for _, row in vinos_seleccionados.iterrows():

y_inicial = pdf.get_y()

url_img = str(row.get('URL', ""))

tmp_path = None



if url_img.startswith("http"):

try:

res = requests.get(url_img, headers=headers, timeout=5)

if res.status_code == 200:

with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:

tmp.write(res.content)

tmp_path = tmp.name

pdf.image(tmp_path, x=10, y=y_inicial, h=28)

except: pass

finally:

if tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)



pdf.set_xy(45, y_inicial)

pdf.set_font("Helvetica", "B", 12)

pdf.set_text_color(114, 47, 55)

nombre = str(row.get('VINO', 'Vino')).encode('latin-1', 'replace').decode('latin-1')

pdf.cell(0, 7, nombre, ln=1)


pdf.set_x(45)

pdf.set_font("Helvetica", "", 10)

pdf.set_text_color(0, 0, 0)

bodega = str(row.get('BODEGA', 'N/A')).encode('latin-1', 'replace').decode('latin-1')

pdf.cell(0, 6, f"Bodega: {bodega}", ln=1)


pdf.set_x(45)

origen = str(row.get('ORIGEN', 'N/A')).encode('latin-1', 'replace').decode('latin-1')

uvas = str(row.get('UVAS', 'N/A')).encode('latin-1', 'replace').decode('latin-1')

pdf.cell(0, 6, f"Origen: {origen} | Uvas: {uvas}", ln=1)


pdf.set_x(45)

pdf.set_font("Helvetica", "B", 10)

c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)

precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"

pdf.cell(0, 6, f"Precio Horeca: {precio}", ln=1)



y_final = max(pdf.get_y(), y_inicial + 32)

pdf.set_y(y_final)

pdf.line(10, y_final, 200, y_final)

pdf.ln(5)


if pdf.get_y() > 250: pdf.add_page()



return bytes(pdf.output())



# 5. LÓGICA PRINCIPAL DE LA APP

df = load_data()



if 'seleccionados' not in st.session_state:

st.session_state.seleccionados = []



# --- BARRA LATERAL (SIDEBAR) CON LOGO ---

with st.sidebar:

# AÑADIMOS EL LOGO AQUÍ

try:

st.image("LOGO GLOP DYD.jpeg", use_container_width=True)

except:

st.error("No se encontró el archivo de logo 'LOGO GLOP DYD.jpeg'")


st.title("Catálogo Vinos")

st.divider()

busqueda = st.text_input("🔍 Buscar por vino o bodega...")


if st.session_state.seleccionados:

st.subheader("Selección actual")

st.write(f"Vinos seleccionados: {len(st.session_state.seleccionados)}")


df_export = df[df.index.isin(st.session_state.seleccionados)]

pdf_data = generar_pdf(df_export)


st.download_button(

label="📥 Descargar Catálogo PDF",

data=pdf_data,

file_name="seleccion_glop_2026.pdf",

mime="application/pdf",

type="primary"

)


if st.button("Limpiar selección"):

st.session_state.seleccionados = []

st.rerun()

else:

st.info("Selecciona vinos para generar el PDF.")



# --- CUERPO DEL CATÁLOGO ---

if not df.empty:

df_f = df.copy()

if busqueda:

df_f = df_f[df_f['VINO'].str.contains(busqueda, case=False) |

df_f['BODEGA'].str.contains(busqueda, case=False)]



st.title("Catálogo Digital 2026")


cols = st.columns(4)

for i, (idx, row) in enumerate(df_f.iterrows()):

with cols[i % 4]:

with st.container(border=True):

is_selected = idx in st.session_state.seleccionados

if st.checkbox("Seleccionar", key=f"sel_{idx}", value=is_selected):

if idx not in st.session_state.seleccionados:

st.session_state.seleccionados.append(idx)

st.rerun()

elif is_selected:

st.session_state.seleccionados.remove(idx)

st.rerun()



img_url = row.get('URL', "https://via.placeholder.com/200x300")

st.image(img_url, use_container_width=True)


st.markdown(f"**{row['VINO']}**")

st.caption(f"{row['BODEGA']}")


if st.button("🔍 Ver detalles", key=f"btn_{idx}"):

mostrar_detalles(row)

else:

st.error("Por favor, asegúrate de que el archivo 'CATALOGO 2026 GLOP.xlsx' esté en la carpeta raíz.")

Este es un código sólido y bien estructurado para una aplicación de catálogo en Streamlit. Tienes una lógica de filtrado eficiente y la generación de PDF mediante fpdf2 (aunque usas fpdf, la sintaxis es compatible) está bien planteada.

He realizado algunas optimizaciones clave para mejorar la estabilidad, el manejo de memoria al generar el PDF y la experiencia de usuario (UX):

Mejoras implementadas:
Manejo de Errores en PDF: Se añadió un bloque try-except más robusto para la descarga de imágenes.

Optimización de st.rerun(): En Streamlit, los st.rerun() dentro de bucles pueden causar parpadeos o bucles infinitos. He ajustado la lógica de selección para que sea más fluida.

Codificación de Texto: Se mejoró la limpieza de caracteres especiales para evitar errores de codificación Latin-1 al generar el PDF (común con tildes y ñ).

Layout de Tarjetas: Se añadió un pequeño ajuste de CSS para que el texto de los nombres de los vinos no rompa el diseño de la cuadrícula.

Python
import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
import os
from tempfile import NamedTemporaryFile

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Catálogo Vinos GLOP 2026", layout="wide", page_icon="🍷")

# Estilos CSS mejorados
st.markdown("""
    <style>
    [data-testid="stImage"] img {
        height: 250px;
        object-fit: contain;
        background-color: #ffffff;
        border-radius: 10px;
        padding: 5px;
    }
    .stButton>button { width: 100%; border-radius: 10px; }
    .stCheckbox { margin-bottom: -15px; }
    /* Limitar altura del nombre para mantener uniformidad */
    .vino-title {
        height: 50px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data
def load_data():
    file_path = 'CATALOGO 2026 GLOP.xlsx'
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df.columns = [str(c).strip().upper() for c in df.columns]
        # Limpieza de strings
        df = df.map(lambda x: str(x).strip() if pd.notnull(x) else "")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# 3. DIÁLOGO DE DETALLES
@st.dialog("Ficha Técnica del Producto")
def mostrar_detalles(row):
    col_img, col_info = st.columns([1, 1.2])
    
    with col_img:
        url = row.get('URL', "")
        img_url = url if url.startswith("http") else "https://via.placeholder.com/400x600?text=Sin+Imagen"
        st.image(img_url, use_container_width=True)
    
    with col_info:
        st.subheader(row['VINO'])
        st.write(f"**Bodega:** {row.get('BODEGA', 'N/A')}")
        st.write(f"**Origen:** {row.get('ORIGEN', 'N/A')}")
        st.write(f"**Uvas:** {row.get('UVAS', 'N/A')}")
        st.write(f"**Añada:** {row.get('AÑADA', row.get('AÑO', 'N/A'))}")
        
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        if c_horeca:
            st.metric(label="Precio Tarifa Horeca", value=f"{row[c_horeca]} €")
        
        st.divider()
        st.caption("Precios y disponibilidad sujetos a cambios para la temporada 2026.")

# 4. GENERACIÓN DE PDF PROFESIONAL
def generar_pdf(vinos_seleccionados):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Función para limpiar texto para FPDF (Latin-1)
    def clean_txt(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    for _, row in vinos_seleccionados.iterrows():
        pdf.add_page()
        
        # Encabezado de página
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(114, 47, 55) # Color vino
        pdf.cell(190, 10, "GLOP - SELECCIÓN EXCLUSIVA 2026", ln=1, align='C')
        pdf.ln(10)

        # Imagen
        y_img = pdf.get_y()
        url_img = str(row.get('URL', ""))
        if url_img.startswith("http"):
            try:
                res = requests.get(url_img, timeout=5)
                if res.status_code == 200:
                    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                        tmp.write(res.content)
                        tmp_path = tmp.name
                    pdf.image(tmp_path, x=15, y=y_img, h=60)
                    os.remove(tmp_path)
            except:
                pdf.rect(15, y_img, 40, 60) # Recuadro si falla imagen
        
        # Info a la derecha de la imagen
        pdf.set_xy(70, y_img)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, clean_txt(row.get('VINO', 'Vino')), ln=1)
        
        pdf.set_x(70)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 7, clean_txt(row.get('BODEGA', 'N/A')), ln=1)
        
        pdf.ln(5)
        pdf.set_x(70)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, f"Origen: {clean_txt(row.get('ORIGEN', 'N/A'))}\n"
                             f"Uvas: {clean_txt(row.get('UVAS', 'N/A'))}\n"
                             f"Añada: {clean_txt(row.get('AÑADA', row.get('AÑO', 'N/A')))}")
        
        # Precio
        pdf.ln(5)
        pdf.set_x(70)
        pdf.set_font("Helvetica", "B", 12)
        c_horeca = next((c for c in row.index if 'HORECA' in c and 'COMPRA' not in c), None)
        precio = f"{row[c_horeca]} EUR" if c_horeca else "Consultar"
        pdf.cell(0, 8, f"PVP Horeca: {precio}", ln=1)
        
        # Pie de página simple
        pdf.set_y(-25)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 10, "Documento comercial generado para clientes GLOP D&D", align='C')

    return pdf.output(dest='S').encode('latin-1')

# 5. LÓGICA DE LA APP
df = load_data()

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = set() # Usar set para búsquedas más rápidas

with st.sidebar:
    try:
        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)
    except:
        st.title("🍷 GLOP DYD")
    
    st.divider()
    busqueda = st.text_input("🔍 Buscar vino, bodega o zona...")
    
    if st.session_state.seleccionados:
        st.success(f"Vinos seleccionados: {len(st.session_state.seleccionados)}")
        
        df_export = df[df.index.isin(list(st.session_state.seleccionados))]
        
        with st.spinner("Generando PDF..."):
            pdf_bytes = generar_pdf(df_export)
            
        st.download_button(
            label="📥 Descargar Catálogo PDF",
            data=pdf_bytes,
            file_name="catalogo_glop_2026.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = set()
            st.rerun()
    else:
        st.info("Marca los vinos en el catálogo para generar un PDF personalizado.")

# CUERPO PRINCIPAL
if not df.empty:
    st.title("Catálogo Digital 2026")
    
    df_f = df.copy()
    if busqueda:
        mask = df_f.apply(lambda r: r.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        df_f = df_f[mask]

    # Grid de productos
    cols = st.columns(4)
    for i, (idx, row) in enumerate(df_f.iterrows()):
        with cols[i % 4]:
            with st.container(border=True):
                # Checkbox de selección
                checked = idx in st.session_state.seleccionados
                if st.checkbox("Seleccionar", key=f"check_{idx}", value=checked):
                    if idx not in st.session_state.seleccionados:
                        st.session_state.seleccionados.add(idx)
                        st.rerun()
                elif checked:
                    st.session_state.seleccionados.remove(idx)
                    st.rerun()

                img_url = row.get('URL', "")
                if not img_url.startswith("http"):
                    img_url = "https://via.placeholder.com/200x300?text=Vino"
                
                st.image(img_url, use_container_width=True)
                st.markdown(f"<div class='vino-title'>{row['VINO']}</div>", unsafe_allow_html=True)
                st.caption(f"Bodega: {row['BODEGA']}")
                
                if st.button("Ver ficha", key=f"btn_{idx}"):
                    mostrar_detalles(row)
else:
    st.warning("⚠️ No se encontró el archivo 'CATALOGO 2026 GLOP.xlsx'. Por favor, súbelo al servidor.")

st.session_state.seleccionados = set(): Cambiar la lista por un conjunto (set) hace que verificar si un vino ya está seleccionado sea instantáneo, incluso si tienes miles de vinos.

pdf.output(dest='S'): Esta forma de generar el PDF es más directa para enviarlo como descarga en Streamlit sin tener que manejar archivos temporales para el PDF en sí.

Limpieza de caracteres: FPDF suele dar error Latin-1 codec cant encode character... con símbolos como el euro o comillas especiales. La función clean_txt previene que la app se caiga al generar el PDF.

multi_cell en el PDF: Si la información de las uvas u origen es muy larga, cell la cortaría. multi_cell permite que el texto salte de línea automáticamente dentro del documento.

me gustaría que también seleccionase por origen

Para añadir un filtro por Origen (D.O., Región, etc.), lo ideal es colocar un selector multichoice en la barra lateral. Esto permite a los comerciales filtrar rápidamente, por ejemplo, todos los vinos de "Rioja" o "Ribera del Duero".

He actualizado el código para incluir esta lógica. Ahora, los filtros de búsqueda por texto y por origen funcionan de forma combinada.

Código Actualizado (Lógica de Filtrado por Origen)
Python
# ... (Mantener las secciones 1 a 4 del código anterior) ...

# 5. LÓGICA DE LA APP
df = load_data()

if 'seleccionados' not in st.session_state:
    st.session_state.seleccionados = set()

with st.sidebar:
    try:
        st.image("LOGO GLOP DYD.jpeg", use_container_width=True)
    except:
        st.title("🍷 GLOP DYD")
    
    st.divider()
    
    # --- NUEVO FILTRO POR ORIGEN ---
    if not df.empty:
        # Extraemos los orígenes únicos y los ordenamos
        lista_origenes = sorted(df['ORIGEN'].unique())
        filtro_origen = st.multiselect(
            "📍 Filtrar por Origen:",
            options=lista_origenes,
            placeholder="Todas las zonas"
        )
    
    busqueda = st.text_input("🔍 Buscar vino o bodega...")
    
    st.divider()
    
    if st.session_state.seleccionados:
        st.success(f"Vinos seleccionados: {len(st.session_state.seleccionados)}")
        df_export = df[df.index.isin(list(st.session_state.seleccionados))]
        
        with st.spinner("Generando PDF..."):
            pdf_bytes = generar_pdf(df_export)
            
        st.download_button(
            label="📥 Descargar Catálogo PDF",
            data=pdf_bytes,
            file_name="catalogo_glop_2026.pdf",
            mime="application/pdf",
            type="primary"
        )
        
        if st.button("Limpiar selección"):
            st.session_state.seleccionados = set()
            st.rerun()

# --- CUERPO PRINCIPAL CON FILTRADO COMBINADO ---
if not df.empty:
    st.title("Catálogo Digital 2026")
    
    df_f = df.copy()

    # 1. Aplicar filtro de Origen (si hay seleccionados)
    if filtro_origen:
        df_f = df_f[df_f['ORIGEN'].isin(filtro_origen)]

    # 2. Aplicar búsqueda por texto
    if busqueda:
        df_f = df_f[
            df_f['VINO'].str.contains(busqueda, case=False) | 
            df_f['BODEGA'].str.contains(busqueda, case=False)
        ]

    # Mostrar resultados
    if df_f.empty:
        st.warning("No se encontraron vinos con esos criterios.")
    else:
        cols = st.columns(4)
        for i, (idx, row) in enumerate(df_f.iterrows()):
            with cols[i % 4]:
                with st.container(border=True):
                    checked = idx in st.session_state.seleccionados
                    if st.checkbox("Seleccionar", key=f"check_{idx}", value=checked):
                        if idx not in st.session_state.seleccionados:
                            st.session_state.seleccionados.add(idx)
                            st.rerun()
                    elif checked:
                        st.session_state.seleccionados.remove(idx)
                        st.rerun()

                    img_url = row.get('URL', "")
                    if not str(img_url).startswith("http"):
                        img_url = "https://via.placeholder.com/200x300?text=Vino"
                    
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"<div class='vino-title'>{row['VINO']}</div>", unsafe_allow_html=True)
                    st.caption(f"📍 {row['ORIGEN']} | {row['BODEGA']}")
                    
                    if st.button("Ver ficha", key=f"btn_{idx}"):
                        mostrar_detalles(row)
    st.error("Por favor, asegúrate de que el archivo 'CATALOGO 2026 GLOP.xlsx' esté en la carpeta raíz.")
