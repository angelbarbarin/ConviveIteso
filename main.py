from connect import (
    get_mongo_db,
    get_cassandra_session,
    get_dgraph_client
)

from Queries.cassandra_queries import (
    cassandra_r1_historial_asistencia_usuario,
    cassandra_r2_historial_reservaciones_usuario,
    cassandra_r3_asistencias_por_evento,
    cassandra_r4_historial_uso_espacio,
    cassandra_r5_actividad_usuario_rango_fechas,
    cassandra_r6_ultimos_checkins_espacio,
    cassandra_r7_historial_reservaciones_canceladas,
    cassandra_r8_participacion_usuario_tipo_actividad
)

from Queries.mongo_queries import (
    mongo_r1_evento_especifico,
    mongo_r2_eventos_por_tipo_y_fecha,
    mongo_r3_espacios_disponibles_para_reserva,
    mongo_r4_reservaciones_espacio_fecha,
    mongo_r5_eventos_por_organizador,
    mongo_r6_total_eventos_por_tipo,
    mongo_r7_total_reservaciones_por_tipo_espacio,
    mongo_r8_eventos_mayor_demanda
)

from Queries.dgraph_queries import (
    dgraph_r1_users_coinciden,
    dgraph_r2_eventos_con_distintos_roles,
    dgraph_r3_usuarios_por_area_organizadora,
    dgraph_r4_participacion_usuarios_externos,
    dgraph_r5_espacios_por_usuario_y_tipo_evento,
    dgraph_r6_organizadores_por_tipo_usuario,
    dgraph_r7_usuarios_vinculados_evento_o_espacio,
    dgraph_r8_tipos_eventos_conectan_usuarios
)

def mostrar_menu_principal():
    print("\n===== RESERVA ITESO - MENÚ PRINCIPAL =====")
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
    print("4. Historial de reservaciones canceladas")
    print("5. Participación por tipo de actividad")
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


def ejecutar_submenu(tipo, mongo_db=None, cassandra_session=None, dgraph_client=None):
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
        # =========================
        # CONSULTAS CASSANDRA EN HISTORIAL
        # =========================
        if tipo == "historial":
            if opcion == "1":
                cassandra_r1_historial_asistencia_usuario(cassandra_session)
            elif opcion == "2":
                cassandra_r2_historial_reservaciones_usuario(cassandra_session)
            elif opcion == "3":
                cassandra_r5_actividad_usuario_rango_fechas(cassandra_session)
            elif opcion == "4":
                cassandra_r7_historial_reservaciones_canceladas(cassandra_session)
            elif opcion == "5":
                cassandra_r8_participacion_usuario_tipo_actividad(cassandra_session)
            else:
                ejecutar_opcion(f"{tipo.upper()} - Opción {opcion}")

        elif tipo == "eventos":
            if opcion == "1":
                mongo_r1_evento_especifico(mongo_db)
            if opcion == "2":
                mongo_r2_eventos_por_tipo_y_fecha(mongo_db)
            if opcion == "3":
                mongo_r3_espacios_disponibles_para_reserva(mongo_db)
            if opcion == "4":
                cassandra_r3_asistencias_por_evento(cassandra_session)
            else:
                ejecutar_opcion(f"{tipo.upper()} - Opción {opcion}")

        elif tipo == "espacios":
            if opcion == "1":
                mongo_r3_espacios_disponibles_para_reserva(mongo_db)
            if opcion == "2":
                mongo_r4_reservaciones_espacio_fecha(mongo_db)
            if opcion == "3":
                cassandra_r4_historial_uso_espacio(cassandra_session)
            elif opcion == "4":
                cassandra_r6_ultimos_checkins_espacio(cassandra_session)
            else:
                ejecutar_opcion(f"{tipo.upper()} - Opción {opcion}")
        # =========================
        # CONSULTAS DGRAPH EN GRAFO
        # =========================
        elif tipo == "grafo":
            if opcion == "1":
                dgraph_r1_users_coinciden(dgraph_client)
            elif opcion == "2":
                dgraph_r2_eventos_con_distintos_roles(dgraph_client)
            elif opcion == "3":
                dgraph_r3_usuarios_por_area_organizadora(dgraph_client)
            elif opcion == "4":
                dgraph_r4_participacion_usuarios_externos(dgraph_client)
            elif opcion == "5":
                dgraph_r5_espacios_por_usuario_y_tipo_evento(dgraph_client)
            elif opcion == "6":
                dgraph_r7_usuarios_vinculados_evento_o_espacio(dgraph_client)
            else:
                print("Opción inválida en consultas de grafo.")

        # =========================
        # CONSULTAS DGRAPH EN ANALÍTICAS
        # =========================
        elif tipo == "analiticas":
            if opcion == "1":
                mongo_r6_total_eventos_por_tipo(mongo_db)
            if opcion == "2":
                mongo_r7_total_reservaciones_por_tipo_espacio(mongo_db)
            if opcion == "3":
                mongo_r8_eventos_mayor_demanda(mongo_db)
            if opcion == "4":
                dgraph_r6_organizadores_por_tipo_usuario(dgraph_client)
            elif opcion == "5":
                dgraph_r8_tipos_eventos_conectan_usuarios(dgraph_client)
            else:
                ejecutar_opcion(f"{tipo.upper()} - Opción {opcion}")

        else:
            ejecutar_opcion(f"{tipo.upper()} - Opción {opcion}")

def main():
    mongo_db = get_mongo_db()
    cassandra_session = get_cassandra_session()
    dgraph_client = get_dgraph_client()

    while True:
        mostrar_menu_principal()
        opcion = input("Selecciona una sección: ")

        if opcion == "1":
            ejecutar_submenu("historial", mongo_db, cassandra_session, dgraph_client)
        elif opcion == "2":
            ejecutar_submenu("eventos", mongo_db, cassandra_session, dgraph_client)
        elif opcion == "3":
            ejecutar_submenu("espacios", mongo_db, cassandra_session, dgraph_client)
        elif opcion == "4":
            ejecutar_submenu("analiticas", mongo_db, cassandra_session, dgraph_client)
        elif opcion == "5":
            ejecutar_submenu("grafo", mongo_db, cassandra_session, dgraph_client)
        elif opcion == "0":
            print("Saliendo del sistema Reserva ITESO...")
            break
        else:
            print("Opción inválida. Intenta de nuevo.")



if __name__ == "__main__":
    main()