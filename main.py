from connect import connect_mongo, connect_cassandra, connect_dgraph


def mostrar_menu():
    print("\n=== CONVIVE ITESO ===")
    print("\n--- Cassandra ---")
    print("1. Historial reciente de asistencia de un usuario")
    print("2. Historial reciente de reservaciones de un usuario")
    print("3. Historial de asistencias por evento y fecha")
    print("4. Historial de uso de un espacio por fecha")
    print("5. Actividad de un usuario por rango de fechas")
    print("6. Últimos 10 check-ins en un espacio")
    print("7. Historial de reservaciones canceladas")
    print("8. Participación histórica por tipo de actividad")

    print("\n--- MongoDB ---")
    print("9. Consultar evento por ID")
    print("10. Eventos por tipo y fecha")
    print("11. Espacios disponibles para reserva")
    print("12. Reservaciones de un espacio en una fecha")
    print("13. Eventos por organizador")
    print("14. Total de eventos por tipo")
    print("15. Total de reservaciones por tipo de espacio")
    print("16. Eventos con mayor demanda")

    print("\n--- Dgraph ---")
    print("17. Usuarios que coinciden en eventos con un usuario")
    print("18. Eventos en los que coinciden usuarios de distintos roles")
    print("19. Usuarios vinculados a eventos organizados por cierta área")
    print("20. Participación de usuarios externos en eventos")
    print("21. Espacios usados por usuarios según tipo de evento")
    print("22. Organizadores relacionados con tipos de usuarios")
    print("23. Usuarios vinculados por un mismo evento o espacio")
    print("24. Tipos de eventos que conectan más usuarios")

    print("\n0. Salir")


def main():
    mongo_db = connect_mongo()
    cassandra_session = connect_cassandra()
    dgraph_client = connect_dgraph()

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "0":
            print("Saliendo del sistema...")
            break
        elif opcion in [str(i) for i in range(1, 25)]:
            print("Consulta planeada correctamente. Lógica pendiente de implementar.")
        else:
            print("Opción no válida")


if __name__ == "__main__":
    main()