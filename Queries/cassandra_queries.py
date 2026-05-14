from datetime import datetime
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