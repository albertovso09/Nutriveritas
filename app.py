import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# =====================================================================
# CONFIGURACIÓN INICIAL Y FUENTE MONTSERRAT
# =====================================================================
st.set_page_config(page_title="Nutriveritas", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

    /* Aplicamos Montserrat SOLO a los textos legibles, evitando romper iconos de Streamlit */
    html, body, p, h1, h2, h3, h4, h5, h6, label, input, button, div.stMarkdown {
        font-family: 'Montserrat', sans-serif !important;
    }

    [data-testid="stExpander"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
        margin-bottom: 0 !important;
        padding-left: 4px;
        line-height: 1.4 !important;
    }

    /* Ocultar elementos innecesarios nativos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Espaciados limpios en teléfonos */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    /* Contenedores móviles */
    .mobile-scroll-box {
        max-height: 340px; 
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        padding-right: 5px;
        margin-top: 12px;
    }

    .food-row-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #1e293b; 
        border-left: 3px solid #ffcc00; 
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .food-info-side {
        flex-grow: 1;
        padding-right: 10px;
    }

    .food-row-title {
        font-size: 13px;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .food-row-caption {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 400;
        letter-spacing: 0.02em;
    }

    .btn-delete-native {
        background-color: rgba(239, 68, 68, 0.08);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "Base_Datos_Gold.db"
EDULCORANTES_COLS = [
    "acesulfame_k", "alitame", "aspartame", "ciclamato", "esteviol",
    "neohesperidina", "neotame", "sacarina", "sucralosa", "taumatina", "advantame"
]
fecha_hoy_texto = date.today().isoformat()

# =====================================================================
# SECCIÓN 1: BASE DE DATOS Y BORRADO SEGURO
# =====================================================================
def ejecutar_query(query, params=(), is_select=False):
    """Función unificada para evitar choques de memoria y bloquear la DB correctamente"""
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if is_select:
            return cursor.fetchall()
        conn.commit()

def iniciar_db():
    ejecutar_query('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, calorias REAL, proteinas REAL, 
            carbohidratos REAL, grasas REAL, sodio REAL, fibra REAL, antioxidantes REAL, azucar_anadida REAL,
            acesulfame_k REAL, alitame REAL, aspartame REAL, ciclamato REAL, esteviol REAL,
            neohesperidina REAL, neotame REAL, sacarina REAL, sucralosa REAL, taumatina REAL, advantame REAL,
            ingredientes TEXT DEFAULT ''
        )
    ''')
    ejecutar_query('''
        CREATE TABLE IF NOT EXISTS consumo_diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, id_producto INTEGER, gramos REAL,
            FOREIGN KEY(id_producto) REFERENCES productos(id)
        )
    ''')
    ejecutar_query('''
        CREATE TABLE IF NOT EXISTS consumo_agua (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, mililitros REAL
        )
    ''')

iniciar_db()

# Procesar borrado ANTES de renderizar nada para evitar Segmentation Fault
if "delete_id" in st.query_params:
    id_a_borrar = st.query_params["delete_id"]
    ejecutar_query("DELETE FROM consumo_diario WHERE id = ?", (id_a_borrar,))
    st.query_params.clear()
    st.rerun()

# =====================================================================
# SECCIÓN 2: METAS DIARIAS
# =====================================================================
with st.expander("⚙️ Ajustar Metas Diarias", expanded=False):
    meta_cal = st.number_input("Calorías (kcal)", value=1850, step=50, min_value=0)
    meta_prot = st.number_input("Proteína (g)", value=150, step=5, min_value=0)
    meta_carb = st.number_input("Carbohidratos (g)", value=425, step=5, min_value=0)
    meta_gras = st.number_input("Grasas (g)", value=56, step=1, min_value=0)
    meta_agua = st.number_input("Agua (ml)", value=2000, step=100, min_value=0)
    meta_fibra = st.number_input("Fibra (g)", value=30, step=5, min_value=0)
    meta_antiox = st.number_input("Antioxidantes (u)", value=100, step=10, min_value=0)
    
    limite_azucar = st.slider("Azúcar Añadida Max (g)", min_value=0.0, max_value=150.0, value=25.0, step=2.5)
    limite_edulcorantes = st.slider("Límite por Edulcorante (mg)", min_value=0.0, max_value=1000.0, value=150.0, step=10.0)

# =====================================================================
# SECCIÓN 3: BÓVEDA
# =====================================================================
with st.expander("🔐 Administrar Bóveda", expanded=False):
    tab_manual, tab_gestionar = st.tabs(["✍️ Carga Manual", "🗑️ Ver / Borrar"])
    
    with tab_manual:
        with st.form("form_nuevo_alimento", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre del Alimento")
            col_c, col_p, col_cb, col_g = st.columns(4)
            nuevo_cal = col_c.number_input("Kcal", min_value=0.0, value=0.0)
            nuevo_prot = col_p.number_input("Prot (g)", min_value=0.0, value=0.0)
            nuevo_carb = col_cb.number_input("Carbs (g)", min_value=0.0, value=0.0)
            nuevo_gras = col_g.number_input("Grasas (g)", min_value=0.0, value=0.0)
            nuevo_azucar = st.number_input("Azúcar Añadida (g)", min_value=0.0, value=0.0)
            btn_guardar = st.form_submit_button("💾 Guardar Alimento")
            
            if btn_guardar and nuevo_nombre.strip():
                try:
                    ejecutar_query('''
                        INSERT INTO productos (nombre, calorias, proteinas, carbohidratos, grasas, sodio, fibra, antioxidantes, azucar_anadida,
                        acesulfame_k, alitame, aspartame, ciclamato, esteviol, neohesperidina, neotame, sacarina, sucralosa, taumatina, advantame)
                        VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                    ''', (nuevo_nombre.strip(), float(nuevo_cal), float(nuevo_prot), float(nuevo_carb), float(nuevo_gras), float(nuevo_azucar)))
                    st.success("¡Guardado!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Ese alimento ya existe.")

    with tab_gestionar:
        with sqlite3.connect(DB_FILE) as conn_gest:
            df_boveda = pd.read_sql_query("SELECT id, nombre FROM productos", conn_gest)
        if not df_boveda.empty:
            alimento_borrar = st.selectbox("Alimento a eliminar:", df_boveda['nombre'].tolist(), index=None)
            if st.button("🚨 Eliminar Definitivamente") and alimento_borrar:
                ejecutar_query("DELETE FROM productos WHERE nombre = ?", (alimento_borrar,))
                st.rerun()

# =====================================================================
# SECCIÓN 4: AGREGAR REGISTROS (COMIDA Y AGUA)
# =====================================================================
st.title("Nutriveritas")

with sqlite3.connect(DB_FILE) as conn_main:
    df_productos = pd.read_sql_query("SELECT * FROM productos", conn_main)

st.markdown("### 🍽️ Agregar Registro")
if not df_productos.empty:
    producto_seleccionado = st.selectbox("Busca un alimento:", df_productos['nombre'].tolist(), index=None, placeholder="Ej: Huevo Blanco...")
    gramos_consumir = st.number_input("Gramos / ml consumidos:", min_value=0.1, value=100.0, step=10.0)
    
    if producto_seleccionado:
        prod_data = df_productos[df_productos['nombre'] == producto_seleccionado].iloc[0]
        factor = float(gramos_consumir) / 100.0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Kcal", f"{(float(prod_data['calorias'] or 0)*factor):.1f}")
        c2.metric("🥩 Prot", f"{(float(prod_data['proteinas'] or 0)*factor):.1f}g")
        c3.metric("🌾 Carbs", f"{(float(prod_data['carbohidratos'] or 0)*factor):.1f}g")
        c4.metric("🥑 Grasas", f"{(float(prod_data['grasas'] or 0)*factor):.1f}")
        
        if st.button("➕ Agregar a mi Día", type="primary", use_container_width=True):
            ejecutar_query("INSERT INTO consumo_diario (fecha, id_producto, gramos) VALUES (?, ?, ?)",
                           (fecha_hoy_texto, int(prod_data['id']), float(gramos_consumir)))
            st.rerun()
else:
    st.info("La bóveda está vacía.")

st.markdown("---")
st.markdown("### 💧 Registrar Agua")
col_w1, col_w2 = st.columns([2, 1])
with col_w1:
    agua_input = st.number_input("Mililitros:", min_value=0, value=250, step=250, label_visibility="collapsed")
with col_w2:
    if st.button("➕ Tomar", type="secondary", use_container_width=True):
        ejecutar_query("INSERT INTO consumo_agua (fecha, mililitros) VALUES (?, ?)", (fecha_hoy_texto, float(agua_input)))
        st.rerun()

# =====================================================================
# SECCIÓN 5: PROGRESO DE HOY Y EDULCORANTES RESTAURADOS
# =====================================================================
st.markdown("---")
st.markdown("### 📊 Tu Progreso de Hoy")

query_hoy = f'''
    SELECT c.id as id_consumo, c.gramos, p.nombre, p.calorias, p.proteinas, p.carbohidratos, p.grasas, p.azucar_anadida,
    p.acesulfame_k, p.alitame, p.aspartame, p.ciclamato, p.esteviol, p.neohesperidina, p.neotame, p.sacarina, p.sucralosa, p.taumatina, p.advantame
    FROM consumo_diario c JOIN productos p ON c.id_producto = p.id WHERE c.fecha = ?
'''

with sqlite3.connect(DB_FILE) as conn_prog:
    df_hoy = pd.read_sql_query(query_hoy, conn_prog, params=(fecha_hoy_texto,))

res_agua = ejecutar_query("SELECT SUM(mililitros) FROM consumo_agua WHERE fecha = ?", (fecha_hoy_texto,), is_select=True)
tot_agua = float(res_agua[0][0]) if res_agua and res_agua[0][0] else 0.0

tot_cal = tot_prot = tot_carb = tot_gras = tot_azucar = 0.0
# Diccionario para almacenar el total individual de cada edulcorante
totales_edulcorantes = {ed: 0.0 for ed in EDULCORANTES_COLS}

if not df_hoy.empty:
    for _, row in df_hoy.iterrows():
        f = float(row['gramos']) / 100.0
        tot_cal += float(row['calorias'] or 0) * f
        tot_prot += float(row['proteinas'] or 0) * f
        tot_carb += float(row['carbohidratos'] or 0) * f
        tot_gras += float(row['grasas'] or 0) * f
        tot_azucar += float(row['azucar_anadida'] or 0) * f
        
        # Sumar a cada edulcorante específico
        for ed in EDULCORANTES_COLS:
            totales_edulcorantes[ed] += float(row[ed] or 0) * f

st.markdown(f"**🔥 Calorías:** {tot_cal:.1f} / {meta_cal} kcal")
st.progress(min(tot_cal / max(meta_cal, 1), 1.0))

st.markdown(f"**🥩 Proteína:** {tot_prot:.1f}g / {meta_prot}g")
st.progress(min(tot_prot / max(meta_prot, 1), 1.0))

st.markdown(f"**🌾 Carbs:** {tot_carb:.1f}g / {meta_carb}g")
st.progress(min(tot_carb / max(meta_carb, 1), 1.0))

st.markdown(f"**💧 Agua:** {tot_agua:.0f}ml / {meta_agua}ml")
st.progress(min(tot_agua / max(meta_agua, 1), 1.0))

st.markdown(f"**🍬 Azúcar Añadida:** {tot_azucar:.1f}g / {limite_azucar}g")
st.progress(min(tot_azucar / max(limite_azucar, 1.0), 1.0))

# Restauramos el bloque visual detallado de los edulcorantes
st.markdown("---")
st.markdown("### 🧪 Detalle de Edulcorantes")
edulcorantes_consumidos = False

for ed, total_mg in totales_edulcorantes.items():
    if total_mg > 0:
        edulcorantes_consumidos = True
        nombre_legible = ed.replace("_", " ").title()
        st.markdown(f"**{nombre_legible}:** {total_mg:.1f}mg / {limite_edulcorantes}mg")
        st.progress(min(total_mg / max(limite_edulcorantes, 1.0), 1.0))

if not edulcorantes_consumidos:
    st.info("No has consumido edulcorantes hoy. ¡Excelente! 🙌")

# =====================================================================
# SECCIÓN 6: LISTA CON SCROLL TÁCTIL
# =====================================================================
st.markdown("---")
st.markdown("### 🍽️ Consumidos hoy")

if not df_hoy.empty:
    html_acumulado = '<div class="mobile-scroll-box">'
    
    for index, row in df_hoy.iterrows():
        f = float(row['gramos']) / 100.0
        c_cal = float(row['calorias'] or 0) * f
        c_prot = float(row['proteinas'] or 0) * f
        c_carb = float(row['carbohidratos'] or 0) * f
        c_gras = float(row['grasas'] or 0) * f
        c_edul = sum([float(row[ed] or 0) for ed in EDULCORANTES_COLS]) * f
        
        link_borrar = f"?delete_id={row['id_consumo']}"
        
        html_acumulado += f"""
        <div class="food-row-container">
            <div class="food-info-side">
                <div class="food-row-title">🔹 {row['nombre']} <span style="color:#ffcc00; font-weight:normal;">({row['gramos']:.0f}g)</span></div>
                <div class="food-row-caption">🔥 <b>{c_cal:.1f}</b> | 🥩 <b>{c_prot:.1f}g</b> | 🌾 <b>{c_carb:.1f}g</b> | 🥑 <b>{c_gras:.1f}g</b> | 🧪 <b>{c_edul:.1f}mg</b></div>
            </div>
            <div>
                <a class="btn-delete-native" href="{link_borrar}" target="_self">🗑️</a>
            </div>
        </div>
        """
        
    html_acumulado += '</div>'
    st.markdown(html_acumulado, unsafe_allow_html=True)
else:
    st.info("Aún no has registrado ningún alimento hoy.")
