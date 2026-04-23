

def mostrar_menu():
    print("\n=== Convive ITESO ===")
    print("1. Consultar evento por ID (MongoDB)")
    print("2. Consultar eventos por tipo y fecha (MongoDB)")
    print("3. Consultar espacios disponibles (MongoDB)")
    print("4. Historial reciente de asistencia de un usuario (Cassandra)")
    print("5. Historial reciente de reservaciones de un usuario (Cassandra)")
    print("6. Usuarios que coinciden en eventos con otro usuario (Dgraph)")
    print("7. Eventos donde coinciden distintos roles (Dgraph)")
    print("0. Salir")
    

def main():


    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ")

        if opcion == "0":
            print("Saliendo del sistema...")
            break
        elif opcion == "1":
            print("Consulta MongoDB pendiente")
        elif opcion == "2":
            print("Consulta MongoDB pendiente")
        elif opcion == "3":
            print("Consulta MongoDB pendiente")
        elif opcion == "4":
            print("Consulta Cassandra pendiente")
        elif opcion == "5":
            print("Consulta Cassandra pendiente")
        elif opcion == "6":
            print("Consulta Dgraph pendiente")
        elif opcion == "7":
            print("Consulta Dgraph pendiente")
        else:
            print("Opción no válida")


if __name__ == "__main__":
    main()