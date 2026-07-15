# TI3032-U4-INFORME-TECNICO-PYTHON-MONGODB-AlexanderCortés-AngeloZamora
"""
Módulo de Persistencia y Operaciones CRUD - ComercioTech
Asignatura: Bases de Datos No Estructuradas (TI3032)

Este script implementa un menú en consola para administrar los clientes, productos 
y pedidos de la tienda ComercioTech. Utiliza variables de entorno para una conexión 
segura a MongoDB y maneja operaciones con subdocumentos en pesos chilenos (CLP).
"""

import os
import sys
import datetime
import subprocess
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# =====================================================================
# CONFIGURACIÓN DE CONEXIÓN SECURA
# =====================================================================
# Cargar credenciales desde el archivo .env para proteger los accesos
MONGO_USER = quote_plus(os.getenv("MONGO_USER", "appComercio"))
MONGO_PASSWORD = quote_plus(os.getenv("MONGO_PASSWORD", "ClaveSegura123."))
MONGO_HOST = os.getenv("MONGO_HOST", "ec2-18-215-168-127.compute-1.amazonaws.com")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "comerciotech")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "comerciotech")

# Construcción de la URI de conexión
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_AUTH_SOURCE}"

# Intentar conectar con la base de datos
try:
    print("Conectando a la base de datos MongoDB... ⌛")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Comprobar la conexión activa con un ping
    client.admin.command("ping")
    print("¡Conexión establecida exitosamente! 😁 👌\n")
except ConnectionFailure as cf:
    print(f" ❌ Error de conexión: No se pudo conectar al servidor. Detalle: {cf}", file=sys.stderr)
    sys.exit(1)
except OperationFailure as of:
    print(f" ❌ Error de autenticación: Usuario o contraseña incorrectos. Detalle: {of}", file=sys.stderr)
    sys.exit(1)

# Base de datos y colecciones
db = client[MONGO_DB]
coleccion_clientes = db["clientes"]
coleccion_productos = db["productos"]
coleccion_pedidos = db["pedidos"]


# =====================================================================
# UTILIDADES DE PANTALLA
# =====================================================================
def limpiar_pantalla() -> None:
    """Limpia la consola según el sistema operativo actual."""
    subprocess.run(["cls" if os.name == "nt" else "clear"], shell=True)


def formatear_clp(monto: float) -> str:
    """Formatea un valor numérico a pesos chilenos ($X.XXX CLP)."""
    return f"${int(monto):,} CLP".replace(",", ".")


# =====================================================================
# CARGA DE DATOS DE PRUEBA (SEED)
# =====================================================================
def inicializar_base_de_datos() -> None:
    """Borra las colecciones actuales y recarga datos limpios en pesos chilenos (CLP)."""
    # Borrado previo para asegurar un inicio limpio en cada prueba
    coleccion_clientes.drop()
    coleccion_productos.drop()
    coleccion_pedidos.drop()

    # Insertar clientes de prueba
    coleccion_clientes.insert_many([
        {
            "_id": 1,
            "nombre": "Laura Martínez",
            "email": "laura.martinez@gmail.com",
            "fecha_registro": "2026-01-15T10:30:00Z",
            "direccion": "Av. Providencia 1234, Santiago",
            "telefono": "+56 9 8123 4567"
        },
        {
            "_id": 2,
            "nombre": "Carlos Rojas",
            "email": "carlos.rojas@hotmail.com",
            "fecha_registro": "2025-09-22T14:10:00Z",
            "direccion": "Calle Los Aromos 456, Valparaíso",
            "telefono": "+56 9 7234 5678"
        },
        {
            "_id": 3,
            "nombre": "Angelo Zamora",
            "email": "angelo.zamora@comerciotech.cl",
            "fecha_registro": "2026-07-14T12:00:00Z",
            "direccion": "Av. Costanera 4321, Santiago",
            "telefono": "+56 9 1111 2222"
        },
        {
            "_id": 4,
            "nombre": "Alexander Cortés",
            "email": "alexander.cortes@comerciotech.cl",
            "fecha_registro": "2026-07-14T12:00:00Z",
            "direccion": "Av. Batuco 4111, Santiago",
            "telefono": "+56 9 5481 9624"
        }
    ])

    # Insertar productos de prueba (Catálogo)
    coleccion_productos.insert_many([
        {
            "_id": 101,
            "nombre": "Disco Duro SSD NVMe 2TB",
            "precio": 189990,
            "stock": 150,
            "categorias": ["Almacenamiento", "Hardware"]
        },
        {
            "_id": 102,
            "nombre": "Memoria RAM DDR5 32GB",
            "precio": 120500,
            "stock": 80,
            "categorias": ["Memorias", "Hardware"]
        },
        {
            "_id": 103,
            "nombre": "Procesador AMD Ryzen 7",
            "precio": 349990,
            "stock": 45,
            "categorias": ["Procesadores", "Hardware"]
        },
        {
            "_id": 104,
            "nombre": "Monitor Gamer 27'' IPS",
            "precio": 279990,
            "stock": 30,
            "categorias": ["Monitores", "Hardware"]
        }
    ])

    # Insertar pedidos con subdocumentos embebidos (Productos comprados)
    coleccion_pedidos.insert_many([
        {
            "_id": 501,
            "cliente_id": 1,
            "fecha_pedido": "2026-02-10T10:00:00Z",
            "monto_total": 310490,
            "productos": [
                {"producto_id": 101, "nombre": "Disco Duro SSD NVMe 2TB", "cantidad": 1, "precio_unitario": 189990},
                {"producto_id": 102, "nombre": "Memoria RAM DDR5 32GB", "cantidad": 1, "precio_unitario": 120500}
            ]
        },
        {
            "_id": 502,
            "cliente_id": 2,
            "fecha_pedido": "2025-10-01T13:30:00Z",
            "monto_total": 241000,
            "productos": [
                {"producto_id": 102, "nombre": "Memoria RAM DDR5 32GB", "cantidad": 2, "precio_unitario": 120500}
            ]
        }
    ])
    print("[✓] Base de datos inicializada con datos de prueba (CLP).")


# =====================================================================
# OPERACIONES CRUD
# =====================================================================

# 1. READ
def visualizar_datos_comerciotech() -> None:
    """Muestra de forma ordenada los datos de las colecciones."""
    try:
        print("\n--- LISTA DE CLIENTES ---")
        for cli in coleccion_clientes.find():
            print(f"ID: {cli['_id']:<3} | Nombre: {cli['nombre']:<18} | Correo: {cli['email']:<28} | Fono: {cli['telefono']}")

        print("\n--- LISTA DE PRODUCTOS ---")
        for prod in coleccion_productos.find():
            print(f"ID: {prod['_id']:<3} | Ítem: {prod['nombre']:<25} | Precio: {formatear_clp(prod['precio']):<14} | Stock: {prod['stock']}")

        print("\n--- HISTORIAL DE PEDIDOS ---")
        for ped in coleccion_pedidos.find():
            print(f"Pedido: #{ped['_id']:<3} | Cliente ID: {ped['cliente_id']:<3} | Fecha: {ped['fecha_pedido']} | Total: {formatear_clp(ped['monto_total'])}")
            for p_emb in ped["productos"]:
                # CORRECCIÓN: Ahora imprime el nombre desnormalizado del producto guardado en el subdocumento
                print(f"   -> [Subdocumento] ID Prod: {p_emb['producto_id']:<3} | Producto: {p_emb['nombre']:<25} | Cant: {p_emb['cantidad']:<2} | P.U.: {formatear_clp(p_emb['precio_unitario'])}")
    except PyMongoError as pe:
        print(f"[X] Error al consultar datos: {pe}", file=sys.stderr)


# 2. CREATE Pedido (con subdocumentos)
def crear_pedido_interactivo() -> None:
    """Permite crear un pedido agregando múltiples productos y restando su stock."""
    try:
        print("\n--- CREAR NUEVO PEDIDO ---")
        visualizar_datos_comerciotech()
        
        # Validar si el ID de pedido ya existe
        id_pedido = int(input("\nIngrese ID para el nuevo Pedido (Ej: 503): "))
        if coleccion_pedidos.find_one({"_id": id_pedido}):
            print("[X] Error: El ID del pedido ya existe.")
            return

        # Validar que el cliente exista
        id_cliente = int(input("Ingrese el ID del Cliente que realiza la compra: "))
        if not coleccion_clientes.find_one({"_id": id_cliente}):
            print("[X] Error: El cliente no existe.")
            return

        productos_compras = []
        monto_total = 0

        # Agregar productos al pedido
        while True:
            id_prod = int(input("\nIngrese ID del Producto a comprar (0 para finalizar): "))
            if id_prod == 0:
                break
                
            producto = coleccion_productos.find_one({"_id": id_prod})
            if not producto:
                print("[X] Producto no encontrado. Intente nuevamente.")
                continue

            cantidad = int(input(f"Cantidad de '{producto['nombre']}' (Stock disponible: {producto['stock']}): "))
            if cantidad > producto["stock"] or cantidad <= 0:
                print("[X] Cantidad inválida o supera el stock actual.")
                continue

            # Restar stock del catálogo de productos
            coleccion_productos.update_one({"_id": id_prod}, {"$inc": {"stock": -cantidad}})

            # Crear el subdocumento del producto
            sub_doc = {
                "producto_id": id_prod,
                "nombre": producto["nombre"],
                "cantidad": cantidad,
                "precio_unitario": producto["precio"]
            }
            productos_compras.append(sub_doc)
            monto_total += producto["precio"] * cantidad
            print(f"  [+] Añadido al carro: {producto['nombre']} x{cantidad}")

        if not productos_compras:
            print("[Info] El pedido no contiene productos. Operación cancelada.")
            return

        # Guardar el pedido en la base de datos
        nuevo_pedido = {
            "_id": id_pedido,
            "cliente_id": id_cliente,
            "fecha_pedido": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "monto_total": monto_total,
            "productos": productos_compras
        }
        
        coleccion_pedidos.insert_one(nuevo_pedido)
        print(f"\n[✓] Pedido #{id_pedido} registrado con éxito. Total a pagar: {formatear_clp(monto_total)}")

    except ValueError:
        print("[X] Error: Ingrese valores numéricos adecuados.")
    except PyMongoError as pe:
        print(f"[X] Error al guardar el pedido en MongoDB: {pe}", file=sys.stderr)


# 3. CREATE Cliente
def crear_cliente_interactivo() -> None:
    """Permite registrar un nuevo cliente de forma manual en el sistema."""
    try:
        print("\n--- REGISTRAR NUEVO CLIENTE ---")
        id_cliente = int(input("Ingrese ID para el nuevo Cliente (Ej: 5): "))
        if coleccion_clientes.find_one({"_id": id_cliente}):
            print("[X] Error: Ya existe un cliente con ese ID.")
            return

        nombre = input("Ingrese nombre del cliente: ").strip()
        if not nombre:
            print("[X] Error: El nombre no puede estar vacío.")
            return

        email = input("Ingrese correo electrónico: ").strip()
        direccion = input("Ingrese dirección de despacho: ").strip()
        telefono = input("Ingrese teléfono de contacto: ").strip()

        nuevo_cliente = {
            "_id": id_cliente,
            "nombre": nombre,
            "email": email,
            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "direccion": direccion,
            "telefono": telefono
        }

        coleccion_clientes.insert_one(nuevo_cliente)
        print(f"\n[✓] Cliente '{nombre}' con ID {id_cliente} registrado de forma exitosa.")

    except ValueError:
        print("[X] Error: El ID debe ser un valor numérico entero.")
    except PyMongoError as pe:
        print(f"[X] Error al guardar el cliente en MongoDB: {pe}", file=sys.stderr)


# 4. CREATE Producto (Nueva Función)
def crear_producto_interactivo() -> None:
    """Permite registrar un nuevo producto en el catálogo de inventario."""
    try:
        print("\n--- REGISTRAR NUEVO PRODUCTO ---")
        id_prod = int(input("Ingrese ID (SKU) para el nuevo Producto (Ej: 105): "))
        if coleccion_productos.find_one({"_id": id_prod}):
            print("[X] Error: Ya existe un producto registrado con ese ID.")
            return

        nombre = input("Ingrese nombre del producto (Ej: Teclado Mecánico): ").strip()
        if not nombre:
            print("[X] Error: El nombre del producto no puede estar vacío.")
            return

        precio = float(input("Ingrese precio en pesos chilenos (CLP): "))
        if precio <= 0:
            print("[X] Error: El precio debe ser un número positivo.")
            return

        stock = int(input("Ingrese stock disponible inicial: "))
        if stock < 0:
            print("[X] Error: El stock no puede ser negativo.")
            return

        # Entrada de categorías simples separadas por coma
        cat_input = input("Categorías (separadas por coma, Ej: Teclados, Hardware): ").strip()
        categorias = [cat.strip() for cat in cat_input.split(",") if cat.strip()]

        nuevo_producto = {
            "_id": id_prod,
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "categorias": categorias
        }

        coleccion_productos.insert_one(nuevo_producto)
        print(f"\n[✓] Producto '{nombre}' con ID {id_prod} agregado exitosamente al catálogo.")

    except ValueError:
        print("[X] Error: Entrada inválida. Verifique que el ID, precio y stock sean números.")
    except PyMongoError as pe:
        print(f"[X] Error al guardar el producto en MongoDB: {pe}", file=sys.stderr)


# 5. UPDATE Producto
def actualizar_precio_producto() -> None:
    """Busca un producto por ID y actualiza su precio."""
    try:
        print("\n--- ACTUALIZAR PRECIO DE UN PRODUCTO ---")
        id_prod = int(input("Ingrese el ID del Producto a modificar: "))
        producto = coleccion_productos.find_one({"_id": id_prod})
        
        if not producto:
            print("[X] Error: No se encontró ningún producto con ese ID.")
            return

        print(f"Producto encontrado: '{producto['nombre']}' - Precio actual: {formatear_clp(producto['precio'])}")
        nuevo_precio = float(input("Ingrese el nuevo precio en Pesos Chilenos (CLP): "))
        
        if nuevo_precio <= 0:
            print("[X] Error: El precio debe ser un número positivo.")
            return

        # Modificar el precio con $set
        coleccion_productos.update_one(
            {"_id": id_prod},
            {"$set": {"precio": nuevo_precio}}
        )
        print(f"[✓] Precio de '{producto['nombre']}' actualizado a {formatear_clp(nuevo_precio)}.")

    except ValueError:
        print("[X] Entrada de datos incorrecta. Ingrese un valor numérico.")
    except PyMongoError as pe:
        print(f"[X] Error en el servidor al actualizar: {pe}", file=sys.stderr)


# 6. DELETE Pedido
def eliminar_pedido_por_cancelacion() -> None:
    """Busca un pedido, devuelve la cantidad de productos al stock y lo elimina."""
    try:
        print("\n--- ELIMINAR / CANCELAR PEDIDO ---")
        id_pedido = int(input("Ingrese el ID del Pedido que desea anular: "))
        pedido = coleccion_pedidos.find_one({"_id": id_pedido})

        if not pedido:
            print("[X] Error: No se encontró ningún pedido con ese ID.")
            return

        # Devolver el stock al catálogo antes de eliminar el pedido
        for prod_emb in pedido["productos"]:
            coleccion_productos.update_one(
                {"_id": prod_emb["producto_id"]},
                {"$inc": {"stock": prod_emb["cantidad"]}}
            )
            print(f"  -> Devolviendo stock de '{prod_emb['nombre']}': +{prod_emb['cantidad']} unidades.")

        # Eliminar el pedido de la colección
        coleccion_pedidos.delete_one({"_id": id_pedido})
        print(f"[✓] Pedido #{id_pedido} eliminado con éxito.")

    except ValueError:
        print("[X] Ingrese un ID de pedido numérico válido.")
    except PyMongoError as pe:
        print(f"[X] Error al eliminar el registro: {pe}", file=sys.stderr)


# 7. DELETE Cliente
def eliminar_cliente_interactivo() -> None:
    """Elimina un cliente por ID si no tiene pedidos activos para mantener la integridad de los datos."""
    try:
        print("\n--- ELIMINAR CLIENTE ---")
        id_cliente = int(input("Ingrese el ID del Cliente a eliminar: "))
        cliente = coleccion_clientes.find_one({"_id": id_cliente})

        if not cliente:
            print("[X] Error: No se encontró ningún cliente con ese ID.")
            return

        # Validación técnica de integridad: Buscar si el cliente tiene pedidos activos
        pedidos_asociados = coleccion_pedidos.find_one({"cliente_id": id_cliente})
        if pedidos_asociados:
            print(f"[X] ERROR DE SEGURIDAD NoSQL: No se puede eliminar a '{cliente['nombre']}' porque tiene pedidos activos en el sistema.")
            print("    Debe anular o eliminar primero todos sus pedidos antes de dar de baja al cliente.")
            return

        # Si no tiene pedidos asociados, se elimina de manera limpia
        coleccion_clientes.delete_one({"_id": id_cliente})
        print(f"[✓] Cliente '{cliente['nombre']}' eliminado exitosamente.")

    except ValueError:
        print("[X] Ingrese un ID de cliente numérico válido.")
    except PyMongoError as pe:
        print(f"[X] Error en MongoDB al eliminar el cliente: {pe}", file=sys.stderr)


# =====================================================================
# CONSULTAS AVANZADAS
# =====================================================================
def consultas_analiticas_menu() -> None:
    """Submenú interactivo para realizar búsquedas personalizadas en CLP."""
    while True:
        limpiar_pantalla()
        print(
            """
            ==================================================================
            |                      CONSULTAS NoSQL                           |
            ==================================================================
            1. Buscar pedidos mayores a $300.000 CLP.
            2. Buscar clientes con correos corporativos.
            3. Buscar pedidos por ID de producto.
            0. Volver al menú principal.
            ==================================================================
            """
        )
        opcion = input("Seleccione consulta analítica [1-3, 0]: ")

        if opcion == "1":
            limpiar_pantalla()
            print("\n  >> PEDIDOS MAYORES A $300.000 CLP <<\n")
            query = {"monto_total": {"$gt": 300000}}
            resultado = coleccion_pedidos.find(query).sort("monto_total", -1)
            for doc in resultado:
                print(f"Pedido: #{doc['_id']} | Cliente ID: {doc['cliente_id']} | Total: {formatear_clp(doc['monto_total'])}")
            input("\nPresione ENTER para continuar...")

        elif opcion == "2":
            limpiar_pantalla()
            print("\n  >> CLIENTES CON CORREOS CORPORATIVOS <<\n")
            # Excluye dominios genéricos (gmail, hotmail o yahoo)
            query = {"email": {"$not": {"$regex": "(gmail\\.com|hotmail\\.com|yahoo\\.com)$", "$options": "i"}}}
            resultado = coleccion_clientes.find(query).sort("nombre", 1)
            for doc in resultado:
                print(f"Nombre: {doc['nombre']:<20} | Correo: {doc['email']}")
            input("\nPresione ENTER para continuar...")

        elif opcion == "3":
            limpiar_pantalla()
            print("\n  >> BUSCAR PEDIDOS POR PRODUCTO <<\n")
            try:
                id_prod = int(input("Ingrese ID de producto a monitorear (Ej: 102): "))
                query = {"productos.producto_id": id_prod}
                resultado = coleccion_pedidos.find(query)
                
                encontrados = False
                for doc in resultado:
                    encontrados = True
                    print(f"Pedido: #{doc['_id']} | Cliente ID: {doc['cliente_id']} | Total Pedido: {formatear_clp(doc['monto_total'])}")
                    for p_emb in doc["productos"]:
                        if p_emb["producto_id"] == id_prod:
                            print(f"   -> Producto comprado: {p_emb['nombre']} x{p_emb['cantidad']}")
                
                if not encontrados:
                    print("No se encontraron transacciones con este producto.")
            except ValueError:
                print("[X] Ingrese un ID numérico de producto válido.")
            input("\nPresione ENTER para continuar...")

        elif opcion == "0":
            break


# =====================================================================
# MENÚ PRINCIPAL
# =====================================================================
def main() -> None:
    """Flujo de entrada principal del menú."""
    # COMENTADO: Ya no borra la base de datos de forma automática al iniciar el programa
    # inicializar_base_de_datos() 
    
    # Mensaje de bienvenida directo al menú
    input("\nPresione ENTER para ingresar al sistema de ComercioTech...")

    while True:
        limpiar_pantalla()
        print(
            """
            ==================================================================
            |                     SISTEMA COMERCIOTECH                       |
            |                           MENÚ CRUD                            |
            ==================================================================
            1. Mostrar datos de la base de datos (READ).
            2. Crear un nuevo pedido (CREATE Pedido).
            3. Registrar un nuevo cliente (CREATE Cliente).
            4. Registrar un nuevo producto (CREATE Producto).
            5. Actualizar precio de un producto (UPDATE Producto).
            6. Eliminar / Cancelar un pedido (DELETE Pedido).
            7. Eliminar un cliente de la base de datos (DELETE Cliente).
            8. Consultas y analítica NoSQL.
            9. Reestablecer datos de prueba (Reset a estado inicial).
            0. Salir.
            ==================================================================
            """
        )
        opcion = input("Seleccione una opción [1-9, 0]: ")

        if opcion == "1":
            limpiar_pantalla()
            print("\n=======================================================")
            print("         REPORTE DE PERSISTENCIA ACTIVO (CLP)          ")
            print("=======================================================")
            visualizar_datos_comerciotech()
            input("\nPresione ENTER para continuar...")

        elif opcion == "2":
            limpiar_pantalla()
            crear_pedido_interactivo()
            input("\nPresione ENTER para continuar...")

        elif opcion == "3":
            limpiar_pantalla()
            crear_cliente_interactivo()
            input("\nPresione ENTER para continuar...")

        elif opcion == "4":
            limpiar_pantalla()
            crear_producto_interactivo()
            input("\nPresione ENTER para continuar...")

        elif opcion == "5":
            limpiar_pantalla()
            actualizar_precio_producto()
            input("\nPresione ENTER para continuar...")

        elif opcion == "6":
            limpiar_pantalla()
            eliminar_pedido_por_cancelacion()
            input("\nPresione ENTER para continuar...")

        elif opcion == "7":
            limpiar_pantalla()
            eliminar_cliente_interactivo()
            input("\nPresione ENTER para continuar...")

        elif opcion == "8":
            consultas_analiticas_menu()

        elif opcion == "9":
            limpiar_pantalla()
            inicializar_base_de_datos()
            input("\nPresione ENTER para continuar...")

        elif opcion == "0":
            limpiar_pantalla()
            print("Cerrando conexión con la base de datos...")
            client.close()
            print("¡Conexión cerrada! Adiós. 👋")
            input("\nPresione ENTER para salir...")
            break
        else:
            input("\nOpción incorrecta. Presione ENTER para continuar...")

    sys.exit(0)


if __name__ == "__main__":
    main()