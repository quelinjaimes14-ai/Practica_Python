import random
from datetime import datetime, timedelta

# --- CONFIGURACIÓN (La misma lógica de negocio) ---
nombre_tabla = "comportamientos"  # El nombre de tu tabla en phpMyAdmin
ips_base = [f"192.168.1.{i}" for i in range(1, 51)] 
origenes = ['Google Ads', 'Facebook', 'Instagram Bio', 'Directo', 'Newsletter']
productos = ['Camisa_Lino_Blanca', 'Jean_Slim_Negro', 'Zapatillas_Urban', 'Vestido_Verano_Floral', 'Chaqueta_Cuero']
acciones_interfaz = ['btn_agregar_carrito', 'btn_ver_tallas', 'img_zoom', 'link_menu_hombres']

# Tipos de movimiento
TIPO_INGRESO, TIPO_CLICK, TIPO_VISTA, TIPO_COMPRA, TIPO_CANCELACION = 1, 2, 3, 4, 5

def generar_sesion_usuario(fecha_inicio):
    sesion_sql = []
    
    ip = random.choice(ips_base)
    origen = random.choice(origenes)
    tiempo = fecha_inicio
    
    # Función auxiliar para formatear valores SQL
    def format_sql(ip, tipo, origen, elem, fecha, com):
        # NULL para el ID (autoincremental), y comillas simples para textos
        return f"(NULL, '{ip}', {tipo}, '{origen}', '{elem}', '{fecha}', '{com}')"

    # 1. Ingreso
    sesion_sql.append(format_sql(ip, TIPO_INGRESO, origen, 'Home_Page', tiempo.strftime("%Y-%m-%d %H:%M:%S"), 'Inicio de sesion'))
    
    # Lógica de comportamiento
    dado = random.random()
    if dado < 0.15:   # Compra
        acciones, compra, cancela = 5, True, False
    elif dado < 0.40: # Cancela
        acciones, compra, cancela = 4, False, True
    else:             # Solo mira
        acciones, compra, cancela = random.randint(1, 3), False, False

    # Navegación intermedia
    for _ in range(acciones):
        tiempo += timedelta(seconds=random.randint(5, 45))
        prod = random.choice(productos)
        
        # Vista
        sesion_sql.append(format_sql(ip, TIPO_VISTA, origen, f"vista_{prod}", tiempo.strftime("%Y-%m-%d %H:%M:%S"), 'Navegando catalogo'))
        
        # Posible Click
        if random.random() > 0.5:
            tiempo += timedelta(seconds=2)
            sesion_sql.append(format_sql(ip, TIPO_CLICK, origen, random.choice(acciones_interfaz), tiempo.strftime("%Y-%m-%d %H:%M:%S"), 'Interaccion interfaz'))

    # Desenlace
    tiempo += timedelta(seconds=random.randint(10, 60))
    if compra:
        sesion_sql.append(format_sql(ip, TIPO_COMPRA, origen, 'btn_finalizar_pago_exitoso', tiempo.strftime("%Y-%m-%d %H:%M:%S"), 'Venta Exitosa'))
    elif cancela:
        sesion_sql.append(format_sql(ip, TIPO_CANCELACION, origen, 'btn_cancelar_checkout', tiempo.strftime("%Y-%m-%d %H:%M:%S"), 'Abandono en pago'))
        
    return sesion_sql

# --- GENERACIÓN DEL ARCHIVO SQL ---
registros_totales = []
fecha_base = datetime(2025, 11, 1, 9, 0, 0)

print("Generando sentencias SQL...")

# Encabezado del archivo SQL (Crear tabla si no existe)
sql_header = f"""
INSERT INTO `{nombre_tabla}` (`id`, `ip_usuario`, `tipo_movimiento`, `origen`, `elementos_involucrados`, `fecha_hora`, `comenario`) VALUES
"""

# Generamos los datos
lineas_insert = []
for _ in range(350): # Generamos 350 sesiones (aprox 2500 registros)
    fecha_base += timedelta(minutes=random.randint(10, 180))
    nuevos_registros = generar_sesion_usuario(fecha_base)
    lineas_insert.extend(nuevos_registros)

# Escribimos el archivo
with open('comportamientos.sql', mode='w', encoding='utf-8') as file:
    file.write(sql_header)
    # Unimos todos los valores con coma y salto de línea
    file.write(",\n".join(lineas_insert))
    file.write(";") # Cerramos la sentencia SQL

print(f"¡Listo! Se ha creado 'comportamientos.sql' con {len(lineas_insert)} registros.")
print("Ahora puedes importarlo en phpMyAdmin en la pestaña 'Importar'.")