from datetime import datetime, timedelta
def _ensure_cassandra_keyspace(session):
    """
    Asegura que la sesión esté trabajando sobre el keyspace correcto.
    """
    session.set_keyspace("conviveiteso")


def _normalize_user_id(user_input):
    """
    Permite que el usuario escriba USER001 o solo 1.
    Si escribe 1, se convierte a USER001.
    """
    user_input = user_input.strip().upper()

    if user_input.startswith("USER"):
        return user_input

    if user_input.isdigit():
        return f"USER{int(user_input):03d}"

    return user_input


def cassandra_r1_historial_asistencia_usuario(session):
    """
    Requerimiento 1:
    Consultar el historial reciente de asistencia de un usuario específico,
    ordenado de la asistencia más reciente a la más antigua, limitado a 20 registros.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R1: Historial reciente de asistencia de un usuario =====")
    user_input = input("Ingresa el user_id del usuario, por ejemplo USER001 o 1: ")

    user_id = _normalize_user_id(user_input)

    query = """
        SELECT user_id,
               attendance_timestamp,
               event_id,
               event_name,
               event_type,
               attendance_status
        FROM attendance_by_user
        WHERE user_id = %s
        ORDER BY attendance_timestamp DESC
        LIMIT 20;
    """

    rows = session.execute(query, (user_id,))

    rows = list(rows)

    if not rows:
        print(f"\nNo se encontraron registros de asistencia para el usuario {user_id}.\n")
        return

    print(f"\nHistorial reciente de asistencia para el usuario {user_id}:")
    print("-" * 80)

    for row in rows:
        print(f"Evento: {row.event_name}")
        print(f"ID del evento: {row.event_id}")
        print(f"Tipo de evento: {row.event_type}")
        print(f"Fecha de asistencia: {row.attendance_timestamp}")
        print(f"Estado de asistencia: {row.attendance_status}")
        print("-" * 80)

def cassandra_r2_historial_reservaciones_usuario(session):
    """
    Requerimiento 2:
    Consultar el historial reciente de reservaciones realizadas por un usuario específico,
    ordenado de la reservación más reciente a la más antigua, limitado a 20 registros.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R2: Historial reciente de reservaciones de un usuario =====")
    user_input = input("Ingresa el user_id del usuario, por ejemplo USER001 o 1: ")

    user_id = _normalize_user_id(user_input)

    query = """
        SELECT user_id,
               reservation_timestamp,
               reservation_id,
               space_id,
               space_name,
               space_type,
               reservation_status,
               usage_date
        FROM reservations_by_user
        WHERE user_id = %s
        ORDER BY reservation_timestamp DESC
        LIMIT 20;
    """

    rows = session.execute(query, (user_id,))
    rows = list(rows)

    if not rows:
        print(f"\nNo se encontraron reservaciones para el usuario {user_id}.\n")
        return

    print(f"\nHistorial reciente de reservaciones para el usuario {user_id}:")
    print("-" * 80)

    for row in rows:
        print(f"ID de reservación: {row.reservation_id}")
        print(f"Espacio: {row.space_name}")
        print(f"ID del espacio: {row.space_id}")
        print(f"Tipo de espacio: {row.space_type}")
        print(f"Fecha de reservación: {row.reservation_timestamp}")
        print(f"Fecha de uso: {row.usage_date}")
        print(f"Estado de reservación: {row.reservation_status}")
        print("-" * 80)
def _normalize_event_id(event_input):
    """
    Normaliza el event_id.
    Si el usuario escribe EVENT001 o EVT001, se deja igual.
    Si escribe solo un número, se convierte a EVENT001.
    """
    event_input = event_input.strip().upper()

    if event_input.startswith("EVENT") or event_input.startswith("EVT"):
        return event_input

    if event_input.isdigit():
        return f"EVENT{int(event_input):03d}"

    return event_input


def _parse_date_input(date_input):
    """
    Convierte una fecha escrita como texto en formato YYYY-MM-DD
    a un objeto date compatible con Cassandra.
    """
    try:
        return datetime.strptime(date_input.strip(), "%Y-%m-%d").date()
    except ValueError:
        print("\nFormato de fecha inválido. Usa el formato YYYY-MM-DD, por ejemplo 2026-05-14.\n")
        return None


def cassandra_r3_asistencias_por_evento(session):
    """
    Requerimiento 3:
    Consultar los registros de asistencia de un evento específico
    en una fecha determinada, ordenados cronológicamente por hora de registro.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R3: Historial de asistencias por evento =====")
    event_input = input("Ingresa el event_id del evento, por ejemplo EVENT001: ")
    event_date_input = input("Ingresa la fecha del evento en formato YYYY-MM-DD: ")

    event_id = _normalize_event_id(event_input)
    event_date = _parse_date_input(event_date_input)

    if event_date is None:
        return

    query = """
        SELECT event_id,
               event_name,
               event_date,
               attendance_timestamp,
               user_id,
               attendance_status
        FROM attendance_by_event_date
        WHERE event_id = %s
          AND event_date = %s
        ORDER BY attendance_timestamp ASC;
    """

    rows = session.execute(query, (event_id, event_date))
    rows = list(rows)

    if not rows:
        print(f"\nNo se encontraron asistencias para el evento {event_id} en la fecha {event_date}.\n")
        return

    print(f"\nHistorial de asistencias para el evento {event_id} en la fecha {event_date}:")
    print("-" * 80)

    for row in rows:
        print(f"Evento: {row.event_name}")
        print(f"ID del evento: {row.event_id}")
        print(f"Fecha del evento: {row.event_date}")
        print(f"Usuario: {row.user_id}")
        print(f"Hora de asistencia: {row.attendance_timestamp}")
        print(f"Estado de asistencia: {row.attendance_status}")
        print("-" * 80)
def _normalize_space_id(space_input):
    """
    Normaliza el space_id.
    Si el usuario escribe SPC001, se deja igual.
    Si escribe solo un número, se convierte a SPC001.
    """
    space_input = space_input.strip().upper()

    if space_input.startswith("SPC"):
        return space_input

    if space_input.isdigit():
        return f"SPC{int(space_input):03d}"

    return space_input


def cassandra_r4_historial_uso_espacio(session):
    """
    Requerimiento 4:
    Consultar el historial de uso de un espacio específico en una fecha determinada,
    mostrando reservaciones y usos registrados en orden cronológico.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R4: Historial de uso de un espacio universitario =====")
    space_input = input("Ingresa el space_id del espacio, por ejemplo SPC001 o 1: ")
    usage_date_input = input("Ingresa la fecha de uso en formato YYYY-MM-DD: ")

    space_id = _normalize_space_id(space_input)
    usage_date = _parse_date_input(usage_date_input)

    if usage_date is None:
        return

    query = """
        SELECT space_id,
               space_name,
               usage_date,
               usage_timestamp,
               user_id,
               activity_type,
               related_event_id,
               status
        FROM space_usage_by_space_date
        WHERE space_id = %s
          AND usage_date = %s
        ORDER BY usage_timestamp ASC;
    """

    rows = session.execute(query, (space_id, usage_date))
    rows = list(rows)

    if not rows:
        print(f"\nNo se encontraron registros de uso para el espacio {space_id} en la fecha {usage_date}.\n")
        return

    print(f"\nHistorial de uso del espacio {space_id} en la fecha {usage_date}:")
    print("-" * 80)

    for row in rows:
        print(f"Espacio: {row.space_name}")
        print(f"ID del espacio: {row.space_id}")
        print(f"Fecha de uso: {row.usage_date}")
        print(f"Hora de uso: {row.usage_timestamp}")
        print(f"Usuario relacionado: {row.user_id}")
        print(f"Tipo de actividad: {row.activity_type}")

        if row.related_event_id:
            print(f"Evento relacionado: {row.related_event_id}")
        else:
            print("Evento relacionado: No aplica")

        print(f"Estado: {row.status}")
        print("-" * 80)
def _generate_date_range(start_date, end_date):
    """
    Genera todas las fechas entre start_date y end_date, incluyendo ambas.
    """
    current_date = start_date

    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)


def cassandra_r5_actividad_usuario_rango_fechas(session):
    """
    Requerimiento 5:
    Consultar la actividad de un usuario dentro de un rango de fechas,
    incluyendo asistencias, reservaciones y cancelaciones,
    ordenada de la más reciente a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R5: Actividad de usuario por rango de fechas =====")

    user_input = input("Ingresa el user_id del usuario, por ejemplo USER001 o 1: ")
    start_date_input = input("Ingresa la fecha inicial en formato YYYY-MM-DD: ")
    end_date_input = input("Ingresa la fecha final en formato YYYY-MM-DD: ")

    user_id = _normalize_user_id(user_input)
    start_date = _parse_date_input(start_date_input)
    end_date = _parse_date_input(end_date_input)

    if start_date is None or end_date is None:
        return

    if start_date > end_date:
        print("\nLa fecha inicial no puede ser mayor que la fecha final.\n")
        return

    query = """
        SELECT user_id,
               activity_date,
               activity_timestamp,
               activity_type,
               related_id,
               details
        FROM user_activity_by_date
        WHERE user_id = %s
          AND activity_date = %s
        ORDER BY activity_timestamp DESC;
    """

    all_rows = []

    for activity_date in _generate_date_range(start_date, end_date):
        rows = session.execute(query, (user_id, activity_date))
        all_rows.extend(list(rows))

    if not all_rows:
        print(f"\nNo se encontró actividad para el usuario {user_id} entre {start_date} y {end_date}.\n")
        return

    all_rows.sort(key=lambda row: row.activity_timestamp, reverse=True)

    print(f"\nActividad del usuario {user_id} entre {start_date} y {end_date}:")
    print("-" * 80)

    for row in all_rows:
        print(f"Fecha de actividad: {row.activity_date}")
        print(f"Hora de actividad: {row.activity_timestamp}")
        print(f"Tipo de actividad: {row.activity_type}")
        print(f"ID relacionado: {row.related_id}")
        print(f"Detalles: {row.details}")
        print("-" * 80)
def cassandra_r6_ultimos_checkins_espacio(session):
    """
    Requerimiento 6:
    Consultar los últimos 10 check-ins registrados en un espacio universitario específico,
    ordenados de la fecha más reciente a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R6: Últimos 10 check-ins en un espacio =====")
    space_input = input("Ingresa el space_id del espacio, por ejemplo SPC001 o 1: ")

    space_id = _normalize_space_id(space_input)

    query = """
        SELECT space_id,
               space_name,
               checkin_timestamp,
               user_id,
               activity_context,
               status
        FROM checkins_by_space
        WHERE space_id = %s
        ORDER BY checkin_timestamp DESC
        LIMIT 10;
    """

    rows = session.execute(query, (space_id,))
    rows = list(rows)

    if not rows:
        print(f"\nNo se encontraron check-ins para el espacio {space_id}.\n")
        return

    print(f"\nÚltimos 10 check-ins registrados en el espacio {space_id}:")
    print("-" * 80)

    for row in rows:
        print(f"Espacio: {row.space_name}")
        print(f"ID del espacio: {row.space_id}")
        print(f"Fecha de check-in: {row.checkin_timestamp}")
        print(f"Usuario: {row.user_id}")
        print(f"Contexto de actividad: {row.activity_context}")
        print(f"Estado: {row.status}")
        print("-" * 80)
def cassandra_r7_historial_reservaciones_canceladas(session):
    """
    Requerimiento 7:
    Consultar el historial de reservaciones canceladas de un usuario
    o de un espacio específico, ordenado de la cancelación más reciente
    a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    print("\n===== Cassandra R7: Historial de reservaciones canceladas =====")
    print("1. Consultar cancelaciones por usuario")
    print("2. Consultar cancelaciones por espacio")

    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        user_input = input("Ingresa el user_id del usuario, por ejemplo USER001 o 1: ")
        user_id = _normalize_user_id(user_input)

        query = """
            SELECT reservation_id,
                   user_id,
                   space_id,
                   space_name,
                   cancellation_timestamp,
                   reservation_status,
                   cancellation_reason
            FROM cancelled_reservations_by_user
            WHERE user_id = %s
            ORDER BY cancellation_timestamp DESC;
        """

        rows = session.execute(query, (user_id,))
        rows = list(rows)

        titulo = f"Reservaciones canceladas del usuario {user_id}"

    elif opcion == "2":
        space_input = input("Ingresa el space_id del espacio, por ejemplo SPC001 o 1: ")
        space_id = _normalize_space_id(space_input)

        query = """
            SELECT reservation_id,
                   user_id,
                   space_id,
                   space_name,
                   cancellation_timestamp,
                   reservation_status,
                   cancellation_reason
            FROM cancelled_reservations_by_space
            WHERE space_id = %s
            ORDER BY cancellation_timestamp DESC;
        """

        rows = session.execute(query, (space_id,))
        rows = list(rows)

        titulo = f"Reservaciones canceladas del espacio {space_id}"

    else:
        print("\nOpción inválida. Intenta de nuevo.\n")
        return

    rows = [
        row for row in rows
        if str(row.reservation_status).lower() == "cancelled"
    ]

    if not rows:
        print("\nNo se encontraron reservaciones canceladas para la búsqueda seleccionada.\n")
        return

    print(f"\n{titulo}:")
    print("-" * 80)

    for row in rows:
        print(f"ID de reservación: {row.reservation_id}")
        print(f"Usuario: {row.user_id}")
        print(f"Espacio: {row.space_name}")
        print(f"ID del espacio: {row.space_id}")
        print(f"Fecha de cancelación: {row.cancellation_timestamp}")
        print(f"Estado de reservación: {row.reservation_status}")
        print(f"Motivo de cancelación: {row.cancellation_reason}")
        print("-" * 80)