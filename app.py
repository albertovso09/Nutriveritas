import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# =====================================================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# =====================================================================
st.set_page_config(page_title="Nutriveritas", page_icon="🥇", layout="wide")
DB_FILE = "Base_Datos_Gold.db"

# Lista maestra de edulcorantes para iteraciones
EDULCORANTES_COLS = [
    "acesulfame_k", "alitame", "aspartame", "ciclamato", "esteviol",
    "neohesperidina", "neotame", "sacarina", "sucralosa", "taumatina", "advantame"
]

# =====================================================================
# SECCIÓN 1: INICIALIZACIÓN Y ACTUALIZACIÓN DE BASE DE DATOS
# =====================================================================
def iniciar_db():
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        cursor = conn.cursor()
        
        # Tabla de Inventario (Bóveda) - Estructura Premium 11 Edulcorantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                calorias REAL,
                proteinas REAL,
                carbohidratos REAL,
                grasas REAL,
                sodio REAL,
                fibra REAL,
                antioxidantes REAL,
                azucar_anadida REAL,
                acesulfame_k REAL,
                alitame REAL,
                aspartame REAL,
                ciclamato REAL,
                esteviol REAL,
                neohesperidina REAL,
                neotame REAL,
                sacarina REAL,
                sucralosa REAL,
                taumatina REAL,
                advantame REAL,
                ingredientes TEXT DEFAULT ''
            )
        ''')
        
        # Tabla de Historial Diario de Comida
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumo_diario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                id_producto INTEGER,
                gramos REAL,
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            )
        ''')
        
        # Tabla: Historial Diario de Agua
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consumo_agua (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                mililitros REAL
            )
        ''')
        
        conn.commit()

iniciar_db()

# =====================================================================
# SECCIÓN 2: BARRA LATERAL (CONFIGURACIÓN DE METAS)
# =====================================================================
with st.sidebar:
    st.header("⚙️ Configuración")
    st.subheader("🎯 Metas para Hoy")
    st.markdown("Modifica libremente según el día:")
    
    meta_cal = st.number_input("Calorías (kcal)", value=1850, step=50)
    meta_prot = st.number_input("Proteína (g)", value=150, step=5)
    meta_carb = st.number_input("Carbohidratos (g)", value=425, step=5)
    meta_gras = st.number_input("Grasas (g)", value=56, step=1)
    st.divider()
    meta_agua = st.number_input("Agua (ml)", value=2000, step=100)
    meta_fibra = st.number_input("Fibra (g)", value=30, step=5)
    meta_antiox = st.number_input("Antioxidantes (u)", value=100, step=10)
    st.divider()
    st.markdown("🚨 **Límites de Salud (Máximos)**")
    limite_azucar = st.number_input("Azúcar Añadida Max (g)", value=25.0, step=5.0)
    limite_edulcorantes = st.number_input("Edulcorantes Max (Suma Total mg)", value=150.0, step=10.0)

# =====================================================================
# SECCIÓN 3: GESTIÓN DE LA BÓVEDA (AGREGAR Y BORRAR ALIMENTOS)
# =====================================================================
with st.expander("🔐 Administrar Bóveda (Agregar o Borrar Alimentos)", expanded=False):
    st.markdown("⚠️ **Regla de Oro:** Registra los valores nutricionales por cada **100 gramos** (o 100 ml) del producto.")
    
    tab_manual, tab_excel, tab_gestionar = st.tabs(["✍️ Carga Manual", "📊 Carga Masiva (Excel)", "🗑️ Ver / Borrar Bóveda"])
    
    # --- TAB 1: CARGA MANUAL ---
    with tab_manual:
        with st.form("form_nuevo_alimento"):
            col_n, col_c = st.columns([2, 1])
            nuevo_nombre = col_n.text_input("Nombre del Alimento")
            nuevo_cal = col_c.number_input("Calorías (kcal)", min_value=0.0, step=1.0)
            
            st.markdown("**Macronutrientes (g)**")
            col_p, col_cb, col_g = st.columns(3)
            nuevo_prot = col_p.number_input("Proteínas", min_value=0.0, step=0.1)
            nuevo_carb = col_cb.number_input("Carbohidratos", min_value=0.0, step=0.1)
            nuevo_gras = col_g.number_input("Grasas", min_value=0.0, step=0.1)
            
            st.markdown("**Micronutrientes y Salud**")
            col_s, col_f, col_a = st.columns(3)
            nuevo_sod = col_s.number_input("Sodio (mg)", min_value=0.0, step=1.0)
            nuevo_fib = col_f.number_input("Fibra (g)", min_value=0.0, step=0.1)
            nuevo_ant = col_a.number_input("Antioxidantes (u)", min_value=0.0, step=1.0)

            st.markdown("🚨 **Azúcar Añadida**")
            nuevo_azucar = st.number_input("Azúcar Añadida (g)", min_value=0.0, step=0.1)
            
            st.markdown("🧪 **Desglose de Edulcorantes (mg)**")
            col_e1, col_e2, col_e3, col_e4 = st.columns(4)
            val_edul = {}
            for i, ed in enumerate(EDULCORANTES_COLS):
                if i % 4 == 0: target_col = col_e1
                elif i % 4 == 1: target_col = col_e2
                elif i % 4 == 2: target_col = col_e3
                else: target_col = col_e4
                val_edul[ed] = target_col.number_input(ed.capitalize().replace("_", " "), min_value=0.0, step=1.0)

            nuevo_ingredientes = st.text_area("Ingredientes (Opcional)")
            
            btn_guardar = st.form_submit_button("💾 Guardar en la Bóveda", type="primary", width="stretch")
            
            if btn_guardar:
                if nuevo_nombre.strip() == "":
                    st.error("¡El alimento necesita un nombre!")
                else:
                    try:
                        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_add:
                            cursor_add = conn_add.cursor()
                            cursor_add.execute('''
                                INSERT INTO productos (
                                    nombre, calorias, proteinas, carbohidratos, grasas, sodio, fibra, antioxidantes, azucar_anadida, 
                                    acesulfame_k, alitame, aspartame, ciclamato, esteviol, neohesperidina, neotame, sacarina, sucralosa, taumatina, advantame, ingredientes
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                nuevo_nombre.strip(), nuevo_cal, nuevo_prot, nuevo_carb, nuevo_gras, nuevo_sod, nuevo_fib, nuevo_ant, nuevo_azucar,
                                val_edul['acesulfame_k'], val_edul['alitame'], val_edul['aspartame'], val_edul['ciclamato'], val_edul['esteviol'],
                                val_edul['neohesperidina'], val_edul['neotame'], val_edul['sacarina'], val_edul['sucralosa'], val_edul['taumatina'],
                                val_edul['advantame'], nuevo_ingredientes
                            ))
                            conn_add.commit()
                        st.success(f"¡Éxito! '{nuevo_nombre}' guardado.")
                    except sqlite3.IntegrityError:
                        st.error("Ese alimento ya existe. Usa un nombre distinto o bórralo primero.")
                        
    # --- TAB 2: CARGA MASIVA ---
    with tab_excel:
        st.info("Sube tu archivo .xlsx o .csv maestro.")
        archivo_subido = st.file_uploader("📂 Arrastra tu archivo aquí", type=["xlsx", "csv"])
        
        if archivo_subido is not None:
            try:
                if archivo_subido.name.endswith('.csv'):
                    df_carga = pd.read_csv(archivo_subido)
                else:
                    df_carga = pd.read_excel(archivo_subido)
                
                df_carga = df_carga.fillna(0.0)
                
                st.write("Vista previa de los primeros 5 alimentos:")
                st.dataframe(df_carga.head(), width="stretch")

                if st.button("🚀 Cargar todo a la Bóveda", type="primary"):
                    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_masiva:
                        cursor_masiva = conn_masiva.cursor()
                        agregados = 0
                        
                        for index, row in df_carga.iterrows():
                            try:
                                n_nom = str(row.get('nombre', '')).strip()
                                if n_nom:
                                    cursor_masiva.execute('''
                                        INSERT INTO productos (
                                            nombre, calorias, proteinas, carbohidratos, grasas, sodio, fibra, antioxidantes, azucar_anadida,
                                            acesulfame_k, alitame, aspartame, ciclamato, esteviol, neohesperidina, neotame, sacarina, sucralosa, taumatina, advantame, ingredientes
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        n_nom, float(row.get('calorias', 0)), float(row.get('proteinas', 0)), float(row.get('carbohidratos', 0)),
                                        float(row.get('grasas', 0)), float(row.get('sodio', 0)), float(row.get('fibra', 0)), float(row.get('antioxidantes', 0)),
                                        float(row.get('azucar_anadida', 0)), float(row.get('acesulfame_k', 0)), float(row.get('alitame', 0)),
                                        float(row.get('aspartame', 0)), float(row.get('ciclamato', 0)), float(row.get('esteviol', 0)),
                                        float(row.get('neohesperidina', 0)), float(row.get('neotame', 0)), float(row.get('sacarina', 0)),
                                        float(row.get('sucralosa', 0)), float(row.get('taumatina', 0)), float(row.get('advantame', 0)),
                                        str(row.get('ingredientes', ''))
                                    ))
                                    agregados += 1
                            except sqlite3.IntegrityError:
                                pass
                            except Exception:
                                pass
                                
                        conn_masiva.commit()
                    st.success(f"¡Carga completa! Se agregaron {agregados} alimentos nuevos a tu bóveda.")
                    
            except Exception as e:
                st.error(f"Hubo un error al leer el archivo: {e}")

    # --- TAB 3: VER / BORRAR BÓVEDA ---
    with tab_gestionar:
        with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_gest:
            df_boveda = pd.read_sql_query("SELECT * FROM productos", conn_gest)
            
            if not df_boveda.empty:
                st.markdown("### 📋 Alimentos registrados")
                st.dataframe(df_boveda, hide_index=True, width="stretch")
                
                st.markdown("---")
                st.markdown("### 🗑️ Eliminar un alimento")
                st.warning("Selecciona el alimento que deseas borrar por completo de tu sistema.")
                
                alimento_borrar = st.selectbox("Buscar alimento a eliminar:", df_boveda['nombre'].tolist(), index=None, placeholder="Selecciona un alimento...")
                
                if st.button("🚨 Eliminar Definitivamente", type="primary") and alimento_borrar:
                    cursor_gest = conn_gest.cursor()
                    cursor_gest.execute("DELETE FROM productos WHERE nombre = ?", (alimento_borrar,))
                    conn_gest.commit()
                    st.success(f"El alimento '{alimento_borrar}' ha sido borrado.")
                    st.rerun()
            else:
                st.info("Tu bóveda está completamente vacía.")

# =====================================================================
# SECCIÓN 4: INTERFAZ PRINCIPAL (REGISTRO Y VISTA PREVIA)
# =====================================================================
st.title("🥇 Nutriveritas - Consumo Diario")

with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_main:
    df_productos = pd.read_sql_query("SELECT * FROM productos", conn_main)

col_izq, col_der = st.columns([2, 1])

fecha_hoy = date.today().isoformat()

with col_izq:
    st.markdown("### 🍽️ Agregar Comida")
    if not df_productos.empty:
        col_busca, col_cant = st.columns([3, 1])
        with col_busca:
            producto_seleccionado = st.selectbox(
                "Busca un alimento:",
                df_productos['nombre'].tolist(),
                index=None,
                placeholder="Ej: Yogur Griego Deslactosado..."
            )
        with col_cant:
            gramos_consumir = st.number_input("Gramos/ml:", min_value=0.0, value=100.0, step=10.0)

        if producto_seleccionado:
            prod_data = df_productos[df_productos['nombre'] == producto_seleccionado].iloc[0]
            factor = gramos_consumir / 100.0
            
            suma_edul_preview = sum([prod_data[ed] for ed in EDULCORANTES_COLS]) * factor
            
            st.markdown(f"**🔍 Aporte por {gramos_consumir} g/ml:**")
            
            with st.container(border=True):
                mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                mc1.metric("🔥 Calorías", f"{(prod_data['calorias'] * factor):.1f}")
                mc2.metric("🥩 Proteína", f"{(prod_data['proteinas'] * factor):.1f} g")
                mc3.metric("🌾 Carbs", f"{(prod_data['carbohidratos'] * factor):.1f} g")
                mc4.metric("🥑 Grasas", f"{(prod_data['grasas'] * factor):.1f} g")
                mc5.metric("⚖️ Factor", f"x{factor:.1f}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                mc6, mc7, mc8, mc9, mc10 = st.columns(5)
                mc6.metric("🥦 Fibra", f"{(prod_data['fibra'] * factor):.1f} g")
                mc7.metric("🍇 Antiox.", f"{(prod_data['antioxidantes'] * factor):.1f} u")
                mc8.metric("🧂 Sodio", f"{(prod_data['sodio'] * factor):.1f} mg")
                mc9.metric("🍬 Azúcar Añd.", f"{(prod_data['azucar_anadida'] * factor):.1f} g")
                mc10.metric("🧪 Edulcor. (Total)", f"{suma_edul_preview:.1f} mg")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Agregar a mi día", type="primary", width="stretch"):
                id_prod = int(prod_data['id'])
                gramos_float = float(gramos_consumir)
                with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_insert_food:
                    cursor = conn_insert_food.cursor()
                    cursor.execute("INSERT INTO consumo_diario (fecha, id_producto, gramos) VALUES (?, ?, ?)",
                                   (fecha_hoy, id_prod, gramos_float))
                    conn_insert_food.commit()
                st.success(f"¡Añadido: {gramos_float}g de {producto_seleccionado}!")
                st.rerun()
    else:
        st.info("Tu bóveda está vacía. Ve a 'Administrar Bóveda' para empezar.")

with col_der:
    st.markdown("### 💧 Agregar Agua")
    col_w1, col_w2 = st.columns([2, 1])
    with col_w1:
        agua_input = st.number_input("Mililitros:", min_value=0, value=250, step=250)
    with col_w2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Tomar", type="primary"):
            with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_insert_water:
                cursor = conn_insert_water.cursor()
                cursor.execute("INSERT INTO consumo_agua (fecha, mililitros) VALUES (?, ?)", (fecha_hoy, agua_input))
                conn_insert_water.commit()
            st.success(f"¡{agua_input}ml de agua registrados!")
            st.rerun()

# =====================================================================
# SECCIÓN 5: PROGRESO DEL DÍA
# =====================================================================
st.markdown("---")
st.markdown("### 📊 Tu Progreso de Hoy")

columnas_select = "c.id as id_consumo, c.gramos, p.nombre, p.calorias, p.proteinas, p.carbohidratos, p.grasas, p.fibra, p.antioxidantes, p.azucar_anadida, " + ", ".join([f"p.{ed}" for ed in EDULCORANTES_COLS])
query_hoy = f'''
    SELECT {columnas_select}
    FROM consumo_diario c
    JOIN productos p ON c.id_producto = p.id
    WHERE c.fecha = ?
'''

with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_progress:
    df_hoy = pd.read_sql_query(query_hoy, conn_progress, params=(fecha_hoy,))
    
    cursor = conn_progress.cursor()
    cursor.execute("SELECT SUM(mililitros) FROM consumo_agua WHERE fecha = ?", (fecha_hoy,))
    res_agua = cursor.fetchone()[0]
    tot_agua = res_agua if res_agua else 0.0

# Variables para macros y micronutrientes
tot_cal = tot_prot = tot_carb = tot_gras = tot_fib = tot_ant = tot_azucar = tot_edul = 0.0

# Diccionario para sumar los mg de cada edulcorante individualmente
totales_edulcorantes = {ed: 0.0 for ed in EDULCORANTES_COLS}

if not df_hoy.empty:
    for _, row in df_hoy.iterrows():
        factor = row['gramos'] / 100.0
        tot_cal += row['calorias'] * factor
        tot_prot += row['proteinas'] * factor
        tot_carb += row['carbohidratos'] * factor
        tot_gras += row['grasas'] * factor
        tot_fib += row['fibra'] * factor
        tot_ant += row['antioxidantes'] * factor
        tot_azucar += row['azucar_anadida'] * factor
        
        for ed in EDULCORANTES_COLS:
            totales_edulcorantes[ed] += row[ed] * factor
            tot_edul += row[ed] * factor

col_pg1, col_pg2, col_pg3, col_pg4 = st.columns(4)
with col_pg1:
    st.markdown(f"**🔥 Calorías**\n\n{tot_cal:.1f} / {meta_cal} kcal")
    st.progress(min(tot_cal / meta_cal, 1.0) if meta_cal > 0 else 0.0)
with col_pg2:
    st.markdown(f"**🥩 Proteína**\n\n{tot_prot:.1f}g / {meta_prot}g")
    st.progress(min(tot_prot / meta_prot, 1.0) if meta_prot > 0 else 0.0)
with col_pg3:
    st.markdown(f"**🌾 Carbs**\n\n{tot_carb:.1f}g / {meta_carb}g")
    st.progress(min(tot_carb / meta_carb, 1.0) if meta_carb > 0 else 0.0)
with col_pg4:
    st.markdown(f"**🥑 Grasas**\n\n{tot_gras:.1f}g / {meta_gras}g")
    st.progress(min(tot_gras / meta_gras, 1.0) if meta_gras > 0 else 0.0)

st.markdown("<br>", unsafe_allow_html=True)
col_pg5, col_pg6, col_pg7 = st.columns(3)
with col_pg5:
    st.markdown(f"**💧 Agua**\n\n{tot_agua:.0f}ml / {meta_agua}ml")
    st.progress(min(tot_agua / meta_agua, 1.0) if meta_agua > 0 else 0.0)
with col_pg6:
    st.markdown(f"**🥦 Fibra**\n\n{tot_fib:.1f}g / {meta_fibra}g")
    st.progress(min(tot_fib / meta_fibra, 1.0) if meta_fibra > 0 else 0.0)
with col_pg7:
    st.markdown(f"**🍇 Antioxidantes**\n\n{tot_ant:.1f} u / {meta_antiox} u")
    st.progress(min(tot_ant / meta_antiox, 1.0) if meta_antiox > 0 else 0.0)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 🚨 Alertas (Límite Máximo)")

alertas_cols = st.columns(4)

with alertas_cols[0]:
    st.markdown(f"**🍬 Azúcar Añadida**\n\n{tot_azucar:.1f}g / {limite_azucar}g")
    st.progress(min(tot_azucar / limite_azucar, 1.0) if limite_azucar > 0 else 0.0)

with alertas_cols[1]:
    st.markdown(f"**🧪 TOTAL Edulcorantes**\n\n{tot_edul:.1f}mg / {limite_edulcorantes}mg")
    st.progress(min(tot_edul / limite_edulcorantes, 1.0) if limite_edulcorantes > 0 else 0.0)

current_col = 2
for i, edulcorante in enumerate(EDULCORANTES_COLS):
    if current_col >= 4:
        st.markdown("<br>", unsafe_allow_html=True)
        alertas_cols = st.columns(4)
        current_col = 0
        
    with alertas_cols[current_col]:
        nombre_formateado = edulcorante.capitalize().replace("_", " ")
        valor_consumido = totales_edulcorantes[edulcorante]
        st.markdown(f"**{nombre_formateado}**\n\n{valor_consumido:.1f} mg / {limite_edulcorantes} mg")
        st.progress(min(valor_consumido / limite_edulcorantes, 1.0) if limite_edulcorantes > 0 else 0.0)
    
    current_col += 1

# =====================================================================
# SECCIÓN 6: LISTA MÓVIL DE ALIMENTOS CONSUMIDOS HOY
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🍽️ Alimentos consumidos hoy")

if not df_hoy.empty:
    for index, row in df_hoy.iterrows():
        with st.container(border=True):
            factor = row['gramos'] / 100.0
            c_cal = row['calorias'] * factor
            c_prot = row['proteinas'] * factor
            c_carb = row['carbohidratos'] * factor
            c_gras = row['grasas'] * factor
            c_edul = sum([row[ed] for ed in EDULCORANTES_COLS]) * factor
            
            col_info, col_btn = st.columns([4, 1])
            
            with col_info:
                st.markdown(f"**{row['nombre']}** - {row['gramos']}g/ml")
                st.caption(f"🔥 {c_cal:.1f} kcal | 🥩 {c_prot:.1f}g | 🌾 {c_carb:.1f}g | 🥑 {c_gras:.1f}g | 🧪 Edul: {c_edul:.1f}mg")
                
            with col_btn:
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{row['id_consumo']}", help="Eliminar registro", width="text" if hasattr(st, 'button') and False else "stretch"):
                    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn_delete_entry:
                        cursor_del = conn_delete_entry.cursor()
                        cursor_del.execute("DELETE FROM consumo_diario WHERE id = ?", (row['id_consumo'],))
                        conn_delete_entry.commit()
                    st.toast("Alimento eliminado del registro.")
                    st.rerun()
else:
    st.info("Aún no has registrado ningún alimento hoy.")
