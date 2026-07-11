import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# =====================================================================
# CONFIGURACIÓN INICIAL Y DISEÑO MÓVIL PREMIUM (CSS TOTAL)
# =====================================================================
st.set_page_config(page_title="Nutriveritas", page_icon="🥇", layout="wide")

# Inyección CSS Maestro para limpiar Streamlit y optimizar pantallas móviles
st.markdown("""
    <style>
    /* Ocultar elementos innecesarios de Streamlit en móviles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    /* Optimizar márgenes globales en teléfonos */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    /* CONTENEDOR MAESTRO DE SCROLL (Para la lista de alimentos) */
    .mobile-scroll-box {
        max-height: 340px; 
        overflow-y: auto;
        -webkit-overflow-scrolling: touch; /* Habilita scroll táctil ultra fluido en iOS/Android */
        padding-right: 5px;
        margin-top: 10px;
    }

    /* DISEÑO DE FILA UNIFICADA (Tarjeta + Botón en la misma línea) */
    .food-row-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #1e222b;
        border-left: 4px solid #ffcc00;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    
    .food-info-side {
        flex-grow: 1;
        padding-right: 10px;
    }

    .food-row-title {
        font-size: 14px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .food-row-caption {
        font-size: 11px;
        color: #a3a8b4;
        line-height: 1.3;
    }

    /* Estilo del Mini Botón Químico de Borrado Nativo HTML */
    .btn-delete-native {
        background-color: #ff4b4b22;
        color: #ff4b4b;
        border: 1px solid #ff4b4b44;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 14px;
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

# =====================================================================
# SECCIÓN 1: BASE DE DATOS
# =====================================================================
def iniciar_db():
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, calorias REAL, proteinas REAL, 
                carbohidratos REAL, grasas REAL, sodio REAL, fibra REAL, antioxidantes REAL, azucar_anadida REAL,
                acesulfame_k REAL, alitame REAL, aspartame REAL, ciclamato REAL, esteviol REAL,
                neohesperidina REAL, neotame REAL, sacarina REAL, sucralosa REAL, taumatina REAL, advantame REAL,
                ingredientes TEXT DEFAULT ''
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumo_diario (
                id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, id_producto INTEGER, gramos REAL,
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumo_agua (
                id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, mililitros REAL
            )
        ''')
        conn.commit()

iniciar_db()
fecha_hoy_texto = date.today().isoformat()

# =====================================================================
# SECCIÓN 2: CONTROLADORES DE BORRADO DE ALIMENTOS
# =====================================================================
# Detectar si se presionó un botón de borrado nativo a través de parámetros URL query
query_params = st.query_params
if "delete_id" in query_params:
    id_a_borrar = query_params["delete_id"]
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_del:
        cursor = conn_del.cursor()
        cursor.execute("DELETE FROM consumo_diario WHERE id = ?", (id_a_borrar,))
        conn_del.commit()
    # Limpiar los parámetros de la URL para evitar bucles de borrado
    st.query_params.clear()
    st.rerun()

# =====================================================================
# SECCIÓN 3: CONFIGURACIÓN LATERAL
# =====================================================================
with st.sidebar:
    st.header("⚙️ Configuración")
    meta_cal = st.number_input("Calorías (kcal)", value=1850, step=50)
    meta_prot = st.number_input("Proteína (g)", value=150, step=5)
    meta_carb = st.number_input("Carbohidratos (g)", value=425, step=5)
    meta_gras = st.number_input("Grasas (g)", value=56, step=1)
    meta_agua = st.number_input("Agua (ml)", value=2000, step=100)
    meta_fibra = st.number_input("Fibra (g)", value=30, step=5)
    meta_antiox = st.number_input("Antioxidantes (u)", value=100, step=10)
    limite_azucar = st.number_input("Azúcar Añadida Max (g)", value=25.0, step=5.0)
    limite_edulcorantes = st.number_input("Edulcorantes Max (mg)", value=150.0, step=10.0)

# =====================================================================
# SECCIÓN 4: BÓVEDA
# =====================================================================
with st.expander("🔐 Administrar Bóveda (Agregar o Borrar Alimentos)", expanded=False):
    tab_manual, tab_gestionar = st.tabs(["✍️ Carga Manual", "🗑️ Ver / Borrar Bóveda"])
    
    with tab_manual:
        with st.form("form_nuevo_alimento"):
            nuevo_nombre = st.text_input("Nombre del Alimento")
            col_c, col_p, col_cb, col_g = st.columns(4)
            nuevo_cal = col_c.number_input("Kcal", min_value=0.0)
            nuevo_prot = col_p.number_input("Prot (g)", min_value=0.0)
            nuevo_carb = col_cb.number_input("Carbs (g)", min_value=0.0)
            nuevo_gras = col_g.number_input("Grasas (g)", min_value=0.0)
            
            nuevo_azucar = st.number_input("Azúcar Añadida (g)", min_value=0.0)
            btn_guardar = st.form_submit_button("💾 Guardar Alimento")
            
            if btn_guardar and nuevo_nombre.strip():
                try:
                    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_add:
                        cursor = conn_add.cursor()
                        cursor.execute('''
                            INSERT INTO productos (nombre, calorias, proteinas, carbohidratos, grasas, sodio, fibra, antioxidantes, azucar_anadida,
                            acesulfame_k, alitame, aspartame, ciclamato, esteviol, neohesperidina, neotame, sacarina, sucralosa, taumatina, advantame)
                            VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                        ''', (nuevo_nombre.strip(), nuevo_cal, nuevo_prot, nuevo_carb, nuevo_gras, nuevo_azucar))
                        conn_add.commit()
                    st.success("¡Guardado!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Ya existe.")

    with tab_gestionar:
        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_gest:
            df_boveda = pd.read_sql_query("SELECT * FROM productos", conn_gest)
            if not df_boveda.empty:
                alimento_borrar = st.selectbox("Alimento a eliminar de la faz de la tierra:", df_boveda['nombre'].tolist(), index=None)
                if st.button("🚨 Eliminar Definitivamente") and alimento_borrar:
                    cursor = conn_gest.cursor()
                    cursor.execute("DELETE FROM productos WHERE nombre = ?", (alimento_borrar,))
                    conn_gest.commit()
                    st.rerun()

# =====================================================================
# SECCIÓN 5: AGREGAR REGISTROS (COMIDA Y AGUA)
# =====================================================================
st.title("🥇 Nutriveritas")

with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_main:
    df_productos = pd.read_sql_query("SELECT * FROM productos", conn_main)

# Layout compacto optimizado para móviles (Filas consecutivas limpias)
st.markdown("### 🍽️ Agregar Registro")
if not df_productos.empty:
    producto_seleccionado = st.selectbox("Busca un alimento:", df_productos['nombre'].tolist(), index=None, placeholder="Ej: Huevo Blanco...")
    gramos_consumir = st.number_input("Gramos / ml consumidos:", min_value=0.0, value=100.0, step=10.0)
    
    if producto_seleccionado:
        prod_data = df_productos[df_productos['nombre'] == producto_seleccionado].iloc[0]
        factor = float(gramos_consumir) / 100.0
        
        # Vista rápida matemática en columnas compactas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Kcal", f"{(float(prod_data['calorias'] or 0)*factor):.1f}")
        c2.metric("🥩 Prot", f"{(float(prod_data['proteinas'] or 0)*factor):.1f}g")
        c3.metric("🌾 Carbs", f"{(float(prod_data['carbohidratos'] or 0)*factor):.1f}g")
        c4.metric("🥑 Grasas", f"{(float(prod_data['grasas'] or 0)*factor):.1f}g")
        
        if st.button("➕ Agregar a mi Día", type="primary", use_container_width=True):
            with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_ins:
                cursor = conn_ins.cursor()
                cursor.execute("INSERT INTO consumo_diario (fecha, id_producto, gramos) VALUES (?, ?, ?)",
                               (fecha_hoy_texto, int(prod_data['id']), float(gramos_consumir)))
                conn_ins.commit()
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
        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_w:
            cursor = conn_w.cursor()
            cursor.execute("INSERT INTO consumo_agua (fecha, mililitros) VALUES (?, ?)", (fecha_hoy_texto, agua_input))
            conn_w.commit()
        st.rerun()

# =====================================================================
# SECCIÓN 6: INTERFAZ DE PROGRESO DE HOY
# =====================================================================
st.markdown("---")
st.markdown("### 📊 Tu Progreso de Hoy")

query_hoy = f'''
    SELECT c.id as id_consumo, c.gramos, p.nombre, p.calorias, p.proteinas, p.carbohidratos, p.grasas, p.azucar_anadida,
    p.acesulfame_k, p.alitame, p.aspartame, p.ciclamato, p.esteviol, p.neohesperidina, p.neotame, p.sacarina, p.sucralosa, p.taumatina, p.advantame
    FROM consumo_diario c JOIN productos p ON c.id_producto = p.id WHERE c.fecha = ?
'''

with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_prog:
    df_hoy = pd.read_sql_query(query_hoy, conn_prog, params=(fecha_hoy_texto,))
    cursor = conn_prog.cursor()
    cursor.execute("SELECT SUM(mililitros) FROM consumo_agua WHERE fecha = ?", (fecha_hoy_texto,))
    res_agua = cursor.fetchone()[0]
    tot_agua = res_agua if res_agua else 0.0

tot_cal = tot_prot = tot_carb = tot_gras = tot_azucar = tot_edul = 0.0
if not df_hoy.empty:
    for _, row in df_hoy.iterrows():
        f = row['gramos'] / 100.0
        tot_cal += row['calorias'] * f
        tot_prot += row['proteinas'] * f
        tot_carb += row['carbohidratos'] * f
        tot_gras += row['grasas'] * f
        tot_azucar += row['azucar_anadida'] * f
        tot_edul += sum([row[ed] for ed in EDULCORANTES_COLS]) * f

# Barras de Progreso estéticas en el teléfono
st.markdown(f"**🔥 Calorías:** {tot_cal:.1f} / {meta_cal} kcal")
st.progress(min(tot_cal / meta_cal, 1.0) if meta_cal > 0 else 0.0)

st.markdown(f"**🥩 Proteína:** {tot_prot:.1f}g / {meta_prot}g")
st.progress(min(tot_prot / meta_prot, 1.0) if meta_prot > 0 else 0.0)

st.markdown(f"**🌾 Carbs:** {tot_carb:.1f}g / {meta_carb}g")
st.progress(min(tot_carb / meta_carb, 1.0) if meta_carb > 0 else 0.0)

st.markdown(f"**💧 Agua:** {tot_agua:.0f}ml / {meta_agua}ml")
st.progress(min(tot_agua / meta_agua, 1.0) if meta_agua > 0 else 0.0)

st.markdown(f"**🍬 Azúcar Añadida (Límite):** {tot_azucar:.1f}g / {limite_azucar}g")
st.progress(min(tot_azucar / limite_azucar, 1.0) if limite_azucar > 0 else 0.0)

st.markdown(f"**🧪 TOTAL Edulcorantes:** {tot_edul:.1f}mg / {limite_edulcorantes}mg")
st.progress(min(tot_edul / limite_edulcorantes, 1.0) if limite_edulcorantes > 0 else 0.0)

# =====================================================================
# 🚨 SECCIÓN MÁXIMA POTENCIA: LA LISTA CON SCROLL TÁCTIL SIN ERRORES
# =====================================================================
st.markdown("---")
st.markdown("### 🍽️ Alimentos consumidos hoy")

if not df_hoy.empty:
    # Abrimos la caja con scroll táctil nativo permitido por el celular
    html_acumulado = '<div class="mobile-scroll-box">'
    
    for index, row in df_hoy.iterrows():
        f = row['gramos'] / 100.0
        c_cal = row['calorias'] * f
        c_prot = row['proteinas'] * f
        c_carb = row['carbohidratos'] * f
        c_gras = row['grasas'] * f
        c_edul = sum([row[ed] for ed in EDULCORANTES_COLS]) * f
        
        # Enlace HTML nativo que inyecta la instrucción de borrado en la URL
        link_borrar = f"?delete_id={row['id_consumo']}"
        
        # Construimos la fila unificada (Información + Botón de la basura en la misma línea real)
        html_acumulado += f"""
        <div class="food-row-container">
            <div class="food-info-side">
                <div class="food-row-title">🔹 {row['nombre']} <span style="color:#ffcc00;">({row['gramos']:.0f}g)</span></div>
                <div class="food-row-caption">🔥 <b>{c_cal:.1f}</b> | 🥩 <b>{c_prot:.1f}g</b> | 🌾 <b>{c_carb:.1f}g</b> | 🥑 <b>{c_gras:.1f}g</b> | 🧪 <b>{c_edul:.1f}mg</b></div>
            </div>
            <div>
                <a class="btn-delete-native" href="{link_borrar}" target="_self">🗑️</a>
            </div>
        </div>
        """
        
    html_acumulado += '</div>'
    
    # Renderizamos la lista completa de golpe
    st.markdown(html_acumulado, unsafe_allow_html=True)
else:
    st.info("Aún no has registrado ningún alimento hoy.")
