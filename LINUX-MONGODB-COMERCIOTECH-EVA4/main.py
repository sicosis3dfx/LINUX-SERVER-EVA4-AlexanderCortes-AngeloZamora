# TI3032-U4-INFORME-TECNICO-PYTHON-MONGODB-AlexanderCortés-AngeloZamora
"""
Módulo de Integración y Operación CRUD para ComercioTech
Asignatura: Bases de Datos No Estructuradas (TI3032)

Este script implementa un menú interactivo en consola para administrar el ciclo de vida
completo (CRUD) de la base de datos ComercioTech en pesos chilenos (CLP), utilizando
conexiones seguras basadas en variables de entorno (Hardening) y subdocumentos embebidos.
"""

import os
import sys
import datetime
import subprocess
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# =====================================================================
# CONFIGURACIÓN DE CONEXIÓN SEGURA (HARDENING)
# =====================================================================
# Parámetros discretos cargados de manera proactiva para evitar hardcoding
MONGO_USER = quote_plus(os.getenv("MONGO_USER", "appComercio"))
MONGO_PASSWORD = quote_plus(os.getenv("MONGO_PASSWORD", "ClaveSegura123."))
MONGO_HOST = os.getenv("MONGO_HOST", "ec2-54-144-87-228.compute-1.amazonaws.com")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "comerciotech")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "comerciotech")

# Construcción segura de la URI de conexión
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_AUTH_SOURCE}"

# Inicialización del cliente de base de datos con control de excepciones
try:
    print("Estableciendo conexión segura con el clúster NoSQL... ⌛")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Forzar verificación física mediante un ping al clúster de administración
    client.admin.command("ping")
    print("¡Conexión establecida exitosamente con MongoDB! 😁 👌\n")
except ConnectionFailure as cf:
    print(f" ❌ Error crítico de conexión: No se pudo alcanzar el host. Detalle: {cf}", file=sys.stderr)
    sys.exit(1)
except OperationFailure as of:
    print(f" ❌ Error de autenticación: Credenciales de hardening rechazadas. Detalle: {of}", file=sys.stderr)
    sys.exit(1)

# Selección de la base de datos y colecciones para ComercioTech
db = client[MONGO_DB]
coleccion_clientes = db["clientes"]
coleccion_productos = db["productos"]
coleccion_pedidos = db["pedidos"]


# =====================================================================
# UTILERÍAS DE INTERFAZ
# =====================================================================
def limpiar_pantalla() -> None:
    """Limpia la consola del sistema operativo de manera multiplataforma."""
    subprocess.run(["cls" if os.name == "nt" else "clear"], shell=True)


def formatear_clp(monto: float) -> str:
    """
    Formatea un valor flotante al formato de moneda nacional (Pesos Chilenos).
    
    Args:
        monto (float): El valor numérico a formatear.
        
    Returns:
        str: El string con formato '$X.XXX CLP'.
    """
    return f"${int(monto):,} CLP".replace(",", ".")


# =====================================================================
# FUNCIONES: INSERCIÓN INICIAL (SEED)
# =====================================================================
def inicializar_base_de_datos() -> None:
    """Limpia las colecciones activas e inserta registros de prueba en CLP."""
    # Drop preventivo para asegurar una demostración limpia en el examen
    coleccion_clientes.drop()
    coleccion_productos.drop()
    coleccion_pedidos.drop()

    # Inserción de clientes iniciales
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

    # Inserción de productos tecnológicos en Pesos Chilenos (CLP)
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

    # Inserción de pedidos con arreglos de subdocumentos embebidos (Pilar de la Rúbrica)
    coleccion_pedidos.insert_many([
        {
            "_id": 501,
            "cliente_id": 1,
            "fecha_pedido": "2026-02-10T10:00:00Z",
            "monto_total": 310490, # 1 SSD ($189.990) + 1 RAM ($120.500)
            "productos": [
                {"producto_id": 101, "nombre": "Disco Duro SSD NVMe 2TB", "cantidad": 1, "precio_unitario": 189990},
                {"producto_id": 102, "nombre": "Memoria RAM DDR5 32GB", "cantidad": 1, "precio_unitario": 120500}
            ]
        },
        {
            "_id": 502,
            "cliente_id": 2,
            "fecha_pedido": "2025-10-01T13:30:00Z",
            "monto_total": 241000, # 2 Memorias RAM
            "productos": [
                {"producto_id": 102, "nombre": "Memoria RAM DDR5 32GB", "cantidad": 2, "precio_unitario": 120500}
            ]
        }
    ])
    print("[✓] Base de datos de ComercioTech inicializada y poblada con éxito (CLP).")


# =====================================================================
# OPERACIONES CRUD INTERACTIVAS
# =====================================================================

# 1. READ (Visualización de datos activos en formato nacional)
def visualizar_datos_comerciotech() -> None:
    """Consulta y despliega en formato legible los datos de las tres colecciones."""
    try:
        print("\n--- CLIENTES REGISTRADOS ---")
        for cli in coleccion_clientes.find():
            print(f"ID: {cli['_id']:<3} | Nombre: {cli['nombre']:<18} | Correo: {cli['email']:<28} | Fono: {cli['telefono']}")

        print("\n--- CATÁLOGO DE PRODUCTOS ACTIVO ---")
        for prod in coleccion_productos.find():
            print(f"ID: {prod['_id']:<3} | Ítem: {prod['nombre']:<25} | Precio: {formatear_clp(prod['precio']):<14} | Stock: {prod['stock']}")

        print("\n--- REGISTRO HISTÓRICO DE PEDIDOS ---")
        for ped in coleccion_pedidos.find():
            print(f"Pedido: #{ped['_id']:<3} | Cliente ID: {ped['cliente_id']:<3} | Fecha: {ped['fecha_pedido']} | Total: {formatear_clp(ped['monto_total'])}")
            for p_emb in ped["productos"]:
                print(f"   -> [Subdocumento] ID Prod: {p_emb['producto_id']:<3} | Cant: {p_emb['cantidad']:<2} | P.U.: {formatear_clp(p_emb['precio_unitario'])}")
    except PyMongoError as pe:
        print(f"[X] Error al consultar datos lógicos: {pe}", file=sys.stderr)


# 2. CREATE (Creación interactiva de documentos lógicos)
def crear_pedido_interactivo() -> None:
    """Guía al usuario para crear un pedido interactivo con subdocumentos y cálculo de total."""
    try:
        print("\n--- REGISTRAR NUEVO PEDIDO ---")
        # Visualizar datos para referencia rápida del operador
        visualizar_datos_comerciotech()
        
        # Validaciones de ID del pedido
        id_pedido = int(input("\nIngrese ID para el nuevo Pedido (Ej: 503): "))
        if coleccion_pedidos.find_one({"_id": id_pedido}):
            print("[X] Error: El ID del pedido ya existe.")
            return

        # Validación de Cliente existente
        id_cliente = int(input("Ingrese el ID del Cliente que realiza la compra: "))
        if not coleccion_clientes.find_one({"_id": id_cliente}):
            print("[X] Error: El Cliente especificado no existe en el sistema.")
            return

        productos_compras = []
        monto_total = 0

        # Ciclo interactivo de agregación de ítems (Cumple operaciones complejas de subdocumentos)
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

            # Restar atómicamente el stock en catálogo (UPDATE del catálogo)
            coleccion_productos.update_one({"_id": id_prod}, {"$inc": {"stock": -cantidad}})

            # Estructurar subdocumento del producto adquirido
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
            print("[Info] El pedido no contiene productos. Operación abortada.")
            return

        # Insertar pedido estructurado
        nuevo_pedido = {
            "_id": id_pedido,
            "cliente_id": id_cliente,
            "fecha_pedido": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "monto_total": monto_total,
            "productos": productos_compras
        }
        
        coleccion_pedidos.insert_one(nuevo_pedido)
        print(f"\n[✓] Pedido #{id_pedido} creado de manera conforme. Total transacción: {formatear_clp(monto_total)}")

    except ValueError:
        print("[X] Error de entrada: Ingrese valores numéricos adecuados.")
    except PyMongoError as pe:
        print(f"[X] Excepción crítica de MongoDB durante la persistencia: {pe}", file=sys.stderr)


# 3. UPDATE (Actualización controlada de stock y precios)
def actualizar_precio_producto() -> None:
    """Permite buscar un ítem y actualizar su valor neto en CLP."""
    try:
        print("\n--- ACTUALIZACIÓN DE PRECIOS EN CATÁLOGO ---")
        id_prod = int(input("Ingrese el ID del Producto a modificar: "))
        producto = coleccion_productos.find_one({"_id": id_prod})
        
        if not producto:
            print("[X] El ID especificado no pertenece a ningún producto de catálogo.")
            return

        print(f"Producto encontrado: '{producto['nombre']}' - Precio actual: {formatear_clp(producto['precio'])}")
        nuevo_precio = float(input("Ingrese el nuevo valor en Pesos Chilenos (CLP): "))
        
        if nuevo_precio <= 0:
            print("[X] El valor de mercado debe ser un número positivo.")
            return

        # Ejecutar instrucción atómica de actualización
        coleccion_productos.update_one(
            {"_id": id_prod},
            {"$set": {"precio": nuevo_precio}}
        )
        print(f"[✓] Precio de '{producto['nombre']}' actualizado de manera exitosa a {formatear_clp(nuevo_precio)}.")

    except ValueError:
        print("[X] Entrada de datos incorrecta. Ingrese un valor numérico.")
    except PyMongoError as pe:
        print(f"[X] Fallo operativo del motor: {pe}", file=sys.stderr)


# 4. DELETE (Eliminación preventiva de transacciones o registros de catálogo)
def eliminar_pedido_por_cancelacion() -> None:
    """Busca un pedido por ID, reversa el stock de los productos y lo remueve del sistema."""
    try:
        print("\n--- CANCELAR Y ELIMINAR PEDIDO ---")
        id_pedido = int(input("Ingrese el ID del Pedido que desea anular: "))
        pedido = coleccion_pedidos.find_one({"_id": id_pedido})

        if not pedido:
            print("[X] No se encontró ningún pedido registrado bajo el identificador provisto.")
            return

        # Devolución atómica de stock de los productos embebidos (Hacia el catálogo)
        for prod_emb in pedido["productos"]:
            coleccion_productos.update_one(
                {"_id": prod_emb["producto_id"]},
                {"$inc": {"stock": prod_emb["cantidad"]}}
            )
            print(f"  -> Reversado stock de '{prod_emb['nombre']}': +{prod_emb['cantidad']} unidades.")

        # Eliminación lógica
        coleccion_pedidos.delete_one({"_id": id_pedido})
        print(f"[✓] Pedido #{id_pedido} cancelado y removido de la base de datos de manera conforme.")

    except ValueError:
        print("[X] Ingrese un identificador numérico de pedido válido.")
    except PyMongoError as pe:
        print(f"[X] Error durante la remoción del registro físico: {pe}", file=sys.stderr)


# =====================================================================
# CONSULTAS ANALÍTICAS AVANZADAS (REUTILIZACIÓN DEL MENÚ DE EVALUACIÓN 3)
# =====================================================================
def consultas_analiticas_menu() -> None:
    """Menú secundario con consultas e indexación lógica avanzada en CLP."""
    while True:
        limpiar_pantalla()
        print(
            """
            ==================================================================
            |                   CENTRO DE ANALÍTICA NoSQL                    |
            ==================================================================
            1. Pedidos con monto superior a $300.000 CLP.
            2. Buscar clientes con correos corporativos / institucionales.
            3. Buscar pedidos que contengan un producto crítico específico.
            0. Volver al menú principal.
            ==================================================================
            """
        )
        opcion = input("Seleccione consulta analítica [1-3, 0]: ")

        if opcion == "1":
            limpiar_pantalla()
            print("\n  >> PEDIDOS DE ALTO VALOR (> $300.000 CLP) <<\n")
            query = {"monto_total": {"$gt": 300000}}
            resultado = coleccion_pedidos.find(query).sort("monto_total", -1)
            for doc in resultado:
                print(f"Pedido: #{doc['_id']} | Cliente ID: {doc['cliente_id']} | Total: {formatear_clp(doc['monto_total'])}")
            input("\nPresione ENTER para continuar...")

        elif opcion == "2":
            limpiar_pantalla()
            print("\n  >> CLIENTES CORPORATIVOS O DE SEGURIDAD EXCLUSIVA <<\n")
            # Buscar correos que no sean genéricos (gmail, hotmail o yahoo)
            query = {"email": {"$not": {"$regex": "(gmail\\.com|hotmail\\.com|yahoo\\.com)$", "$options": "i"}}}
            resultado = coleccion_clientes.find(query).sort("nombre", 1)
            for doc in resultado:
                print(f"Nombre: {doc['nombre']:<20} | Correo: {doc['email']}")
            input("\nPresione ENTER para continuar...")

        elif opcion == "3":
            limpiar_pantalla()
            print("\n  >> MONITOREO DE COMPRA DE PRODUCTOS CRÍTICOS <<\n")
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
                            print(f"   -> [Filtro Subdocumento] Catálogo: {p_emb['nombre']} x{p_emb['cantidad']}")
                
                if not encontrados:
                    print("No se encontraron transacciones activas con este ítem.")
            except ValueError:
                print("[X] Ingrese un ID numérico de producto válido.")
            input("\nPresione ENTER para continuar...")

        elif opcion == "0":
            break


# =====================================================================
# MENÚ PRINCIPAL INTERACTIVO
# =====================================================================
def main() -> None:
    """Función de entrada principal que inicializa y gestiona la sesión interactiva."""
    # Sincronización inicial automatizada
    inicializar_base_de_datos()
    input("\nPresione ENTER para ingresar al sistema de ComercioTech...")

    while True:
        limpiar_pantalla()
        print(
            """
            ==================================================================
            |                 SISTEMA TRANSACCIONAL NoSQL                    |
            |                         COMERCIOTECH                           |
            ==================================================================
            1. Visualizar datos del sistema (READ).
            2. Registrar nueva venta interactiva (CREATE con Subdocumentos).
            3. Modificar precio de mercado de catálogo (UPDATE).
            4. Cancelar y revertir venta física (DELETE con control).
            5. Centro de analítica avanzada e indexación lógica.
            6. Re-inicializar base de datos (Reset de fábrica).
            0. Salir y liberar recursos en AWS.
            ==================================================================
            """
        )
        opcion = input("Seleccione operación del ciclo de vida NoSQL [1-6, 0]: ")

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
            actualizar_precio_producto()
            input("\nPresione ENTER para continuar...")

        elif opcion == "4":
            limpiar_pantalla()
            eliminar_pedido_por_cancelacion()
            input("\nPresione ENTER para continuar...")

        elif opcion == "5":
            consultas_analiticas_menu()

        elif opcion == "6":
            limpiar_pantalla()
            inicializar_base_de_datos()
            input("\nPresione ENTER para continuar...")

        elif opcion == "0":
            limpiar_pantalla()
            print("Cerrando sesión de manera segura con el host en AWS...")
            client.close()
            print("¡Recursos liberados correctamente en AWS Academy! Adios. 👋")
            input("\nPresione ENTER para salir...")
            break
        else:
            input("\nOpción incorrecta. Presione ENTER para continuar...")

    sys.exit(0)


if __name__ == "__main__":
    main()