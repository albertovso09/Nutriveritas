import streamlit as st
import sqlite3
import streamlit.components.v1 as components
from datetime import date

# =====================================================================
# CONFIGURACIÓN INICIAL Y FUENTE MONTSERRAT
# =====================================================================
st.set_page_config(page_title="Nutriveritas", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

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

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    
    [data-testid="stCaptionContainer"] {
        margin-top: -10px;
        color: #94a3b8;
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
# SECCIÓN 1: MOTOR DE BASE DE DATOS BLINDADO
# =====================================================================
def ejecutar_accion(query, params=()):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    finally:
        conn.close()

def obtener_datos(query, params=()):
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def iniciar_db():
    ejecutar_accion('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, calorias REAL, proteinas REAL, 
            carbohidratos REAL, grasas REAL, sodio REAL, fibra REAL, antioxidantes REAL, azucar_anadida REAL,
            acesulfame_k REAL, alitame REAL, aspartame REAL, ciclamato REAL, esteviol REAL,
            neohesperidina REAL, neotame REAL, sacarina REAL, sucralosa REAL, taumatina REAL, advantame REAL,
            ingredientes TEXT DEFAULT ''
        )
    ''')
    ejecutar_accion('''
        CREATE TABLE IF NOT EXISTS consumo_diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, id_producto INTEGER, gramos REAL,
            FOREIGN KEY(id_producto) REFERENCES productos(id)
        )
    ''')
    ejecutar_accion('''
        CREATE TABLE IF NOT EXISTS consumo_agua (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, mililitros REAL
        )
    ''')

iniciar_db()

# Procesar borrado cuando el iframe mande la señal a la página padre
if "delete_id" in st.query_params:
    id_a_borrar = st.query_params["delete_id"]
    # Aseguramos que sea un número entero para la base de datos
    ejecutar_accion("DELETE FROM consumo_diario WHERE id = ?", (int(id_a_borrar),))
    del st.query_params["delete_id"]
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
# SECCIÓN 3: BÓVEDA CON EDULCORANTES HABILITADOS
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
            
            st.markdown("**(Opcional) Edulcorantes en miligramos (mg):**")
            cols_ed = st.columns(3)
            ed_valores = {}
            for i, ed in enumerate(EDULCORANTES_COLS):
                ed_valores[ed] = cols_ed[i % 3].number_input(ed.replace("_", " ").title(), min_value=0.0, value=0.0, step=10.0)

            btn_guardar = st.form_submit_button("💾 Guardar Alimento")
            
            if btn_guardar and nuevo_nombre.strip():
                try:
                    ejecutar_accion(f'''
                        INSERT INTO productos (nombre, calorias, proteinas, carbohidratos, grasas, sodio, fibra, antioxidantes, azucar_anadida,
                        {", ".join(EDULCORANTES_COLS)})
                        VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, {", ".join(["?"] * len(EDULCORANTES_COLS))})
                    ''', (
                        nuevo_nombre.strip(), float(nuevo_cal), float(nuevo_prot), float(nuevo_carb), float(nuevo_gras), float(nuevo_azucar),
                        *[float(ed_valores[ed]) for ed in EDULCORANTES_COLS]
                    ))
                    st.success("¡Guardado!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Ese alimento ya existe.")

    with tab_gestionar:
        boveda_items = obtener_datos("SELECT id, nombre FROM productos")
        if boveda_items:
            nombres_boveda = [item["nombre"] for item in boveda_items]
            alimento_borrar = st.selectbox("Alimento a eliminar:", nombres_boveda, index=None)
            if st.button("🚨 Eliminar Definitivamente") and alimento_borrar:
                ejecutar_accion("DELETE FROM productos WHERE nombre = ?", (alimento_borrar,))
                st.rerun()

# =====================================================================
# SECCIÓN 4: AGREGAR REGISTROS
# =====================================================================
st.title("Nutriveritas")

productos = obtener_datos("SELECT * FROM productos")

st.markdown("### 🍽️ Agregar Registro")
if productos:
    nombres_prod = [p["nombre"] for p in productos]
    producto_seleccionado = st.selectbox("Busca un alimento:", nombres_prod, index=None, placeholder="Ej: Huevo Blanco...")
    gramos_consumir = st.number_input("Gramos / ml consumidos:", min_value=0.1, value=100.0, step=10.0)
    
    if producto_seleccionado:
        prod_data = next(p for p in productos if p["nombre"] == producto_seleccionado)
        factor = float(gramos_consumir) / 100.0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Kcal", f"{(float(prod_data['calorias'] or 0)*factor):.1f}")
        c2.metric("🥩 Prot", f"{(float(prod_data['proteinas'] or 0)*factor):.1f}g")
        c3.metric("🌾 Carbs", f"{(float(prod_data['carbohidratos'] or 0)*factor):.1f}g")
        c4.metric("🥑 Grasas", f"{(float(prod_data['grasas'] or 0)*factor):.1f}")
        
        if st.button("➕ Agregar a mi Día", type="primary", use_container_width=True):
            ejecutar_accion("INSERT INTO consumo_diario (fecha, id_producto, gramos) VALUES (?, ?, ?)",
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
        ejecutar_accion("INSERT INTO consumo_agua (fecha, mililitros) VALUES (?, ?)", (fecha_hoy_texto, float(agua_input)))
        st.rerun()

# =====================================================================
# SECCIÓN 5: PROGRESO Y BARRAS DE EDULCORANTES INTELIGENTES
# =====================================================================
st.markdown("---")
st.markdown("### 📊 Tu Progreso de Hoy")

query_hoy = '''
    SELECT c.id as id_consumo, c.gramos, p.nombre, p.calorias, p.proteinas, p.carbohidratos, p.grasas, p.azucar_anadida,
    p.acesulfame_k, p.alitame, p.aspartame, p.ciclamato, p.esteviol, p.neohesperidina, p.neotame, p.sacarina, p.sucralosa, p.taumatina, p.advantame
    FROM consumo_diario c JOIN productos p ON c.id_producto = p.id WHERE c.fecha = ?
'''
registros_hoy = obtener_datos(query_hoy, (fecha_hoy_texto,))

res_agua = obtener_datos("SELECT SUM(mililitros) as total FROM consumo_agua WHERE fecha = ?", (fecha_hoy_texto,))
tot_agua = float(res_agua[0]['total']) if res_agua and res_agua[0]['total'] else 0.0

tot_cal = tot_prot = tot_carb = tot_gras = tot_azucar = 0.0
totales_edulcorantes = {ed: 0.0 for ed in EDULCORANTES_COLS}

for row in registros_hoy:
    f = float(row['gramos']) / 100.0
    tot_cal += float(row['calorias'] or 0) * f
    tot_prot += float(row['proteinas'] or 0) * f
    tot_carb += float(row['carbohidratos'] or 0) * f
    tot_gras += float(row['grasas'] or 0) * f
    tot_azucar += float(row['azucar_anadida'] or 0) * f
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

st.markdown("---")
with st.expander("🧪 Lista de Edulcorantes Consumidos", expanded=True):
    edulcorantes_consumidos = False
    for ed in EDULCORANTES_COLS:
        val_edulcorante = totales_edulcorantes[ed]
        if val_edulcorante > 0:
            edulcorantes_consumidos = True
            nombre_legible = ed.replace("_", " ").title()
            st.markdown(f"**{nombre_legible}:** {val_edulcorante:.1f}mg / {limite_edulcorantes}mg")
            st.progress(min(val_edulcorante / max(limite_edulcorantes, 1.0), 1.0))
    
    if not edulcorantes_consumidos:
        st.info("No has registrado consumo de edulcorantes hoy. ¡Excelente! 🙌")

# =====================================================================
# SECCIÓN 6: EL EXPERIMENTO FRANKENSTEIN (SWIPE-TO-DELETE CON JAVASCRIPT)
# =====================================================================
st.markdown("---")
st.markdown("### 🍽️ Consumidos hoy")

if registros_hoy:
    # Creamos un bloque de HTML, CSS y Javascript puro
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');
      body {
        font-family: 'Montserrat', sans-serif;
        margin: 0; padding: 0; background-color: transparent; color: #f8fafc;
      }
      .list-container {
        overflow-x: hidden; /* Oculta lo que sale por los lados */
        overflow-y: auto;
        padding-bottom: 20px;
      }
      .swipe-item {
        position: relative;
        height: 80px;
        margin-bottom: 10px;
        background-color: #1e293b;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        overflow: hidden;
      }
      .delete-btn {
        position: absolute;
        right: 0; top: 0; bottom: 0;
        width: 80px;
        background-color: #ef4444; /* Rojo papelera */
        color: white;
        display: flex; align-items: center; justify-content: center;
        text-decoration: none; font-size: 24px;
        border-radius: 0 8px 8px 0;
      }
      .content {
        position: absolute;
        left: 0; top: 0; bottom: 0; width: 100%;
        background-color: #1e293b;
        z-index: 1;
        transition: transform 0.2s ease-out; /* Animación de rebote suave */
        display: flex; flex-direction: column; justify-content: center;
        padding: 0 15px; box-sizing: border-box;
        border-left: 3px solid #ffcc00;
        border-radius: 8px;
      }
      .title { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
      .macros { font-size: 11px; color: #94a3b8; }
    </style>
    </head>
    <body>
    <div class="list-container">
    """
    
    # Generamos los items en HTML leyendo los datos de Python
    for row in registros_hoy:
        f = float(row['gramos']) / 100.0
        c_cal = float(row['calorias'] or 0) * f
        c_prot = float(row['proteinas'] or 0) * f
        c_carb = float(row['carbohidratos'] or 0) * f
        c_gras = float(row['grasas'] or 0) * f
        c_edul = sum([float(row[ed] or 0) for ed in EDULCORANTES_COLS]) * f
        
        html_code += f"""
        <div class="swipe-item">
            <!-- Quitamos la etiqueta <a> y usamos un div con data-id para control total -->
            <div class="delete-btn" data-id="{row['id_consumo']}">🗑️</div>
            
            <!-- Tarjeta que se desliza por encima -->
            <div class="content" id="item-{row['id_consumo']}">
                <div class="title">🔹 {row['nombre']} ({row['gramos']:.0f}g)</div>
                <div class="macros">🔥 {c_cal:.1f} | 🥩 {c_prot:.1f}g | 🌾 {c_carb:.1f}g | 🥑 {c_gras:.1f}g | 🧪 {c_edul:.1f}mg</div>
            </div>
        </div>
        """
        
    html_code += """
    </div>
    
    <!-- El cerebro en JavaScript -->
    <script>
      const swipeItems = document.querySelectorAll('.swipe-item');
      
      swipeItems.forEach(container => {
          const item = container.querySelector('.content');
          const deleteBtn = container.querySelector('.delete-btn');
          
          let startX = 0;
          let currentX = 0;

          // 🔥 FUNCION MAESTRA DE BORRADO 🔥
          const ejecutarBorrado = () => {
              const idConsumo = deleteBtn.getAttribute('data-id');
              
              // 1. Animación visual de colapso
              item.style.transform = `translateX(-100vw)`; 
              container.style.transition = 'all 0.3s ease-out';
              container.style.transform = 'translateX(-100vw)'; 
              container.style.height = '0px'; 
              container.style.marginBottom = '0px'; 
              container.style.opacity = '0'; 
              
              // 2. Hack para escapar del iframe y obtener la URL real de tu app
              let base = document.referrer; 
              if (!base) {
                  // Fallback directo a tu app si el referrer está bloqueado
                  base = "https://nutriveritas.streamlit.app/";
              }
              base = base.split('?')[0]; // Limpiamos basurita de la URL
              
              // 3. ¡Forzamos a la ventana PREDOMINANTE a recargar con el parámetro!
              const targetUrl = base + "?delete_id=" + idConsumo;
              window.top.location.href = targetUrl;
          };
          
          // Si el usuario decide deslizar a medias y luego hacer "clic" en el basurero
          deleteBtn.addEventListener('click', ejecutarBorrado);
          
          // Detectar cuando tocas la pantalla
          item.addEventListener('touchstart', (e) => {
              startX = e.touches[0].clientX;
              currentX = startX; 
              item.style.transition = 'none'; 
          }, {passive: true});
          
          // Detectar el arrastre
          item.addEventListener('touchmove', (e) => {
              currentX = e.touches[0].clientX;
              let diff = startX - currentX;
              
              if (diff > 0) {
                  item.style.transform = `translateX(-${diff}px)`;
              }
          }, {passive: true});
          
          // Detectar cuando sueltas el dedo
          item.addEventListener('touchend', (e) => {
              item.style.transition = 'transform 0.2s ease-out'; 
              let diff = startX - currentX;
              
              // 1. Si deslizaste MÁS de 120px (swipe completo)
              if (diff > 120) {
                  ejecutarBorrado();
              } 
              // 2. Si deslizaste lo suficiente solo para revelar el botón
              else if (diff > 45) {
                  item.style.transform = `translateX(-80px)`; 
              } 
              // 3. Si fue un toque o deslizamiento muy corto, regresa a su lugar
              else {
                  item.style.transform = `translateX(0px)`;
              }
          });
      });
    </script>
    </body>
    </html>
    """
    
    # Inyectamos el monstruo en Streamlit
    components.html(html_code, height=350, scrolling=True)
else:
    st.info("Aún no has registrado ningún alimento hoy.")
