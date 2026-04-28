from connect import connect_mongo, connect_cassandra, connect_dgraph


def mostrar_menu_principal():
    print("\n===== CONVIVE ITESO - MENÚ PRINCIPAL =====")
    print("1. Historial y actividad de usuarios")
    print("2. Consulta de eventos")
    print("3. Consulta de espacios y reservaciones")
    print("4. Analíticas y métricas")
    print("5. Consultas de relaciones en grafo")
    print("0. Salir")
    

def menu_historial():
    print("\n--- Historial y actividad de usuarios ---")
    print("1. Historial reciente de asistencia de un usuario")
    print("2. Historial reciente de reservaciones de un usuario")
    print("3. Actividad de usuario por rango de fechas")
    print("4. Participación por tipo de actividad")
    print("0. Volver")


def menu_eventos():
    print("\n--- Consulta de eventos ---")
    print("1. Consultar evento específico")
    print("2. Eventos por tipo y fecha")
    print("3. Eventos por organizador")
    print("4. Historial de asistencias por evento")
    print("0. Volver")


def menu_espacios():
    print("\n--- Consulta de espacios y reservaciones ---")
    print("1. Espacios disponibles para reserva")
    print("2. Reservaciones de un espacio en una fecha")
    print("3. Historial de uso de un espacio")
    print("4. Últimos 10 check-ins en un espacio")
    print("5. Reservaciones canceladas por usuario")
    print("6. Reservaciones canceladas por espacio")
    print("0. Volver")


def menu_analiticas():
    print("\n--- Analíticas y métricas ---")
    print("1. Total de eventos por tipo")
    print("2. Total de reservaciones por tipo de espacio")
    print("3. Eventos con mayor demanda")
    print("4. Organizadores relacionados con tipos de usuarios")
    print("5. Tipos de eventos que conectan más usuarios")
    print("0. Volver")


def menu_grafo():
    print("\n--- Consultas de relaciones en grafo ---")
    print("1. Usuarios que coinciden en eventos con un usuario")
    print("2. Eventos con usuarios de distintos roles")
    print("3. Usuarios vinculados a eventos por área")
    print("4. Participación de usuarios externos")
    print("5. Espacios usados por usuarios según tipo de evento")
    print("6. Usuarios vinculados por evento o espacio")
    print("0. Volver")


def ejecutar_opcion(nombre_consulta):
    print(f"\nConsulta seleccionada: {nombre_consulta}")
    print("Esta opción queda preparada para integrar la lógica de consulta correspondiente.\n")


def ejecutar_submenu(tipo):
    while True:
        if tipo == "historial":
            menu_historial()
        elif tipo == "eventos":
            menu_eventos()
        elif tipo == "espacios":
            menu_espacios()
        elif tipo == "analiticas":
            menu_analiticas()
        elif tipo == "grafo":
            menu_grafo()

        opcion = input("Selecciona una opción: ")

        if opcion == "0":
            break

        ejecutar_opcion(f"{tipo.upper()} - Opción {opcion}")


def main():
    mongo_db = connect_mongo()
    cassandra_session = connect_cassandra()
    dgraph_client = connect_dgraph()

    while True:
        mostrar_menu_principal()
        opcion = input("Selecciona una sección: ")

        if opcion == "1":
            ejecutar_submenu("historial")
        elif opcion == "2":
            ejecutar_submenu("eventos")
        elif opcion == "3":
            ejecutar_submenu("espacios")
        elif opcion == "4":
            ejecutar_submenu("analiticas")
        elif opcion == "5":
            ejecutar_submenu("grafo")
        elif opcion == "0":
            print("Saliendo del sistema Convive ITESO...")
            break
        else:
            print("Opción inválida. Intenta de nuevo.")



if __name__ == "__main__":
    main()