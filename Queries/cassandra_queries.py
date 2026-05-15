# =========================================================
# CONVIVE ITESO - CASSANDRA QUERIES
# =========================================================

from datetime import datetime, timedelta


# =========================================================
# UTILIDADES GENERALES CASSANDRA
# =========================================================

def _ensure_cassandra_keyspace(session):
    """
    Asegura que la sesión esté trabajando sobre el keyspace correcto.
    """
    session.set_keyspace("conviveiteso")


def _normalize_user_id(user_input):
    """
    Permite ingresar:
    - USER001
    - 1
    """
    user_input = user_input.strip().upper()

    if user_input.startswith("USER"):
        return user_input

    if user_input.isdigit():
        return f"USER{int(user_input):03d}"

    return user_input


def _normalize_space_id(space_input):
    """
    Permite ingresar:
    - SPC001
    - 1
    """
    space_input = space_input.strip().upper()

    if space_input.startswith("SPC"):
        return space_input

    if space_input.isdigit():
        return f"SPC{int(space_input):03d}"

    return space_input


def _event_id_candidates(event_input):
    """
    Genera posibles formatos de event_id para evitar errores entre EVT001 y EVENT001.
    """
    event_input = event_input.strip().upper()
    candidates = []

    if not event_input:
        return candidates

    if event_input.startswith("EVT"):
        candidates.append(event_input)
        suffix = event_input.replace("EVT", "")
        if suffix.isdigit():
            candidates.append(f"EVENT{int(suffix):03d}")

    elif event_input.startswith("EVENT"):
        candidates.append(event_input)
        suffix = event_input.replace("EVENT", "")
        if suffix.isdigit():
            candidates.append(f"EVT{int(suffix):03d}")

    elif event_input.isdigit():
        candidates.append(f"EVT{int(event_input):03d}")
        candidates.append(f"EVENT{int(event_input):03d}")
        candidates.append(event_input)

    else:
        candidates.append(event_input)

    unique_candidates = []

    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)

    return unique_candidates


def _activity_type_candidates(activity_type_input):
    """
    Genera variantes del tipo de actividad para evitar fallos por mayúsculas/minúsculas.
    """
    activity_type_input = activity_type_input.strip()

    candidates = [
        activity_type_input,
        activity_type_input.lower(),
        activity_type_input.title(),
        activity_type_input.upper()
    ]

    unique_candidates = []

    for candidate in candidates:
        if candidate and candidate not in unique_candidates:
            unique_candidates.append(candidate)

    return unique_candidates


def _parse_date_input(date_input):
    """
    Convierte una fecha en formato YYYY-MM-DD a tipo date.
    """
    try:
        return datetime.strptime(date_input.strip(), "%Y-%m-%d").date()
    except ValueError:
        print("\nFecha inválida. Usa el formato YYYY-MM-DD.")
        print("Ejemplo válido: 2026-05-14\n")
        return None


def _generate_date_range(start_date, end_date):
    """
    Genera todas las fechas entre start_date y end_date, incluyendo ambas.
    """
    current_date = start_date

    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)


def _print_query_header(code, title, description, examples=None):
    """
    Imprime un encabezado user friendly para cada consulta.
    """
    print(f"\n===== {code} =====")
    print(title)

    if description:
        print(f"\n{description}")

    if examples:
        print(examples)

    print()


def _print_separator():
    print("--------------------------------------------------")


def _print_end():
    print("Consulta finalizada.")


# =========================================================
# CASSANDRA R1
# Historial reciente de asistencia de un usuario
# =========================================================

def cassandra_r1_historial_asistencia_usuario(session):
    """
    Requerimiento 1:
    Consultar el historial reciente de asistencia de un usuario específico,
    ordenado de la asistencia más reciente a la más antigua, limitado a 20 registros.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R1",
        "Historial reciente de asistencia de un usuario",
        "Esta consulta muestra los últimos eventos a los que asistió un usuario.",
        "Puedes buscar por código completo o solo por número.\nEjemplos válidos: USER001, 1"
    )

    user_input = input("Ingresa el usuario: ").strip()
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

    rows = list(session.execute(query, (user_id,)))

    if not rows:
        print(f"No se encontraron registros de asistencia para el usuario {user_id}.")
        return

    print("\n===== HISTORIAL RECIENTE DE ASISTENCIA =====\n")
    print(f"Usuario consultado: {user_id}")
    print(f"Registros encontrados: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        _print_separator()
        print(f"{index}. Evento: {row.event_name}")
        print(f"ID del evento: {row.event_id}")
        print(f"Tipo de evento: {row.event_type}")
        print(f"Fecha de asistencia: {row.attendance_timestamp}")
        print(f"Estado: {row.attendance_status}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R2
# Historial reciente de reservaciones de un usuario
# =========================================================

def cassandra_r2_historial_reservaciones_usuario(session):
    """
    Requerimiento 2:
    Consultar el historial reciente de reservaciones realizadas por un usuario específico,
    ordenado de la reservación más reciente a la más antigua, limitado a 20 registros.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R2",
        "Historial reciente de reservaciones de un usuario",
        "Esta consulta muestra las últimas reservaciones realizadas por un usuario.",
        "Sirve para revisar qué espacios ha reservado y el estado de cada reservación.\nEjemplos válidos: USER001, 1"
    )

    user_input = input("Ingresa el usuario: ").strip()
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

    rows = list(session.execute(query, (user_id,)))

    if not rows:
        print(f"No se encontraron reservaciones para el usuario {user_id}.")
        return

    print("\n===== HISTORIAL RECIENTE DE RESERVACIONES =====\n")
    print(f"Usuario consultado: {user_id}")
    print(f"Reservaciones encontradas: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        _print_separator()
        print(f"{index}. Reservación: {row.reservation_id}")
        print(f"Espacio: {row.space_name} ({row.space_id})")
        print(f"Tipo de espacio: {row.space_type}")
        print(f"Fecha de reservación: {row.reservation_timestamp}")
        print(f"Fecha de uso: {row.usage_date}")
        print(f"Estado: {row.reservation_status}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R3
# Historial de asistencias por evento
# =========================================================

def cassandra_r3_asistencias_por_evento(session):
    """
    Requerimiento 3:
    Consultar los registros de asistencia de un evento específico
    en una fecha determinada, ordenados cronológicamente por hora de registro.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R3",
        "Historial de asistencias por evento",
        "Esta consulta muestra los usuarios que registraron asistencia a un evento en una fecha específica.",
        "Ejemplos de evento: EVT001, EVENT001, 1\nEjemplo de fecha: 2026-05-14"
    )

    event_input = input("Ingresa el evento: ").strip()
    event_date_input = input("Ingresa la fecha del evento: ").strip()

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

    rows = []
    selected_event_id = None

    for event_id in _event_id_candidates(event_input):
        rows = list(session.execute(query, (event_id, event_date)))

        if rows:
            selected_event_id = event_id
            break

    if not rows:
        print(f"No se encontraron asistencias para el evento ingresado en la fecha {event_date}.")
        print("Revisa que el event_id y la fecha existan en tus CSV.")
        return

    print("\n===== ASISTENCIAS REGISTRADAS POR EVENTO =====\n")
    print(f"Evento consultado: {selected_event_id}")
    print(f"Fecha consultada: {event_date}")
    print(f"Asistencias encontradas: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        _print_separator()
        print(f"{index}. Usuario: {row.user_id}")
        print(f"Evento: {row.event_name}")
        print(f"ID del evento: {row.event_id}")
        print(f"Fecha del evento: {row.event_date}")
        print(f"Hora de asistencia: {row.attendance_timestamp}")
        print(f"Estado: {row.attendance_status}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R4
# Historial de uso de un espacio universitario
# =========================================================

def cassandra_r4_historial_uso_espacio(session):
    """
    Requerimiento 4:
    Consultar el historial de uso de un espacio específico en una fecha determinada,
    mostrando reservaciones y usos registrados en orden cronológico.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R4",
        "Historial de uso de un espacio universitario",
        "Esta consulta muestra cómo se utilizó un espacio en una fecha específica.",
        "Incluye reservaciones, usuarios relacionados, tipo de actividad y estado.\nEjemplos de espacio: SPC001, 1\nEjemplo de fecha: 2026-05-14"
    )

    space_input = input("Ingresa el espacio: ").strip()
    usage_date_input = input("Ingresa la fecha de uso: ").strip()

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

    rows = list(session.execute(query, (space_id, usage_date)))

    if not rows:
        print(f"No se encontraron registros de uso para el espacio {space_id} en la fecha {usage_date}.")
        return

    print("\n===== HISTORIAL DE USO DEL ESPACIO =====\n")
    print(f"Espacio consultado: {space_id}")
    print(f"Fecha consultada: {usage_date}")
    print(f"Registros encontrados: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        related_event = row.related_event_id if row.related_event_id else "No aplica"

        _print_separator()
        print(f"{index}. Espacio: {row.space_name} ({row.space_id})")
        print(f"Fecha de uso: {row.usage_date}")
        print(f"Hora de uso: {row.usage_timestamp}")
        print(f"Usuario relacionado: {row.user_id}")
        print(f"Tipo de actividad: {row.activity_type}")
        print(f"Evento relacionado: {related_event}")
        print(f"Estado: {row.status}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R5
# Actividad de usuario por rango de fechas
# =========================================================

def cassandra_r5_actividad_usuario_rango_fechas(session):
    """
    Requerimiento 5:
    Consultar la actividad de un usuario dentro de un rango de fechas,
    incluyendo asistencias, reservaciones y cancelaciones,
    ordenada de la más reciente a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R5",
        "Actividad de usuario por rango de fechas",
        "Esta consulta muestra la actividad general de un usuario dentro de un periodo.",
        "Incluye asistencias, reservaciones y cancelaciones.\nEjemplos de usuario: USER001, 1\nEjemplo de fechas: 2026-05-01 a 2026-05-15"
    )

    user_input = input("Ingresa el usuario: ").strip()
    start_date_input = input("Ingresa la fecha inicial: ").strip()
    end_date_input = input("Ingresa la fecha final: ").strip()

    user_id = _normalize_user_id(user_input)
    start_date = _parse_date_input(start_date_input)
    end_date = _parse_date_input(end_date_input)

    if start_date is None or end_date is None:
        return

    if start_date > end_date:
        print("La fecha inicial no puede ser mayor que la fecha final.")
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
        print(f"No se encontró actividad para el usuario {user_id} entre {start_date} y {end_date}.")
        return

    all_rows.sort(key=lambda row: row.activity_timestamp, reverse=True)

    print("\n===== ACTIVIDAD DEL USUARIO POR RANGO DE FECHAS =====\n")
    print(f"Usuario consultado: {user_id}")
    print(f"Periodo consultado: {start_date} a {end_date}")
    print(f"Actividades encontradas: {len(all_rows)}\n")

    for index, row in enumerate(all_rows, start=1):
        _print_separator()
        print(f"{index}. Tipo de actividad: {row.activity_type}")
        print(f"Fecha: {row.activity_date}")
        print(f"Hora: {row.activity_timestamp}")
        print(f"ID relacionado: {row.related_id}")
        print(f"Detalles: {row.details}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R6
# Últimos 10 check-ins en un espacio
# =========================================================

def cassandra_r6_ultimos_checkins_espacio(session):
    """
    Requerimiento 6:
    Consultar los últimos 10 check-ins registrados en un espacio universitario específico,
    ordenados de la fecha más reciente a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R6",
        "Últimos 10 check-ins en un espacio",
        "Esta consulta muestra los registros más recientes de check-in en un espacio universitario.",
        "Sirve para revisar actividad reciente en salas, auditorios o espacios.\nEjemplos válidos: SPC001, 1"
    )

    space_input = input("Ingresa el espacio: ").strip()
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

    rows = list(session.execute(query, (space_id,)))

    if not rows:
        print(f"No se encontraron check-ins para el espacio {space_id}.")
        return

    print("\n===== ÚLTIMOS CHECK-INS DEL ESPACIO =====\n")
    print(f"Espacio consultado: {space_id}")
    print(f"Check-ins encontrados: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        _print_separator()
        print(f"{index}. Espacio: {row.space_name} ({row.space_id})")
        print(f"Usuario: {row.user_id}")
        print(f"Fecha de check-in: {row.checkin_timestamp}")
        print(f"Contexto: {row.activity_context}")
        print(f"Estado: {row.status}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R7
# Historial de reservaciones canceladas
# =========================================================

def cassandra_r7_historial_reservaciones_canceladas(session):
    """
    Requerimiento 7:
    Consultar el historial de reservaciones canceladas de un usuario
    o de un espacio específico, ordenado de la cancelación más reciente
    a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R7",
        "Historial de reservaciones canceladas",
        "Esta consulta permite revisar cancelaciones por usuario o por espacio.",
        "Elige la forma de búsqueda que necesitas."
    )

    print("1. Buscar cancelaciones por usuario")
    print("2. Buscar cancelaciones por espacio")
    print("0. Volver\n")

    opcion = input("Selecciona una opción: ").strip()

    if opcion == "0":
        return

    if opcion == "1":
        user_input = input("Ingresa el usuario, por ejemplo USER001 o 1: ").strip()
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

        rows = list(session.execute(query, (user_id,)))
        title = f"Reservaciones canceladas del usuario {user_id}"

    elif opcion == "2":
        space_input = input("Ingresa el espacio, por ejemplo SPC001 o 1: ").strip()
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

        rows = list(session.execute(query, (space_id,)))
        title = f"Reservaciones canceladas del espacio {space_id}"

    else:
        print("Opción inválida. Intenta de nuevo.")
        return

    rows = [
        row for row in rows
        if str(row.reservation_status).strip().lower() == "cancelled"
    ]

    if not rows:
        print("No se encontraron reservaciones canceladas para la búsqueda seleccionada.")
        return

    print(f"\n===== {title.upper()} =====\n")
    print(f"Cancelaciones encontradas: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        _print_separator()
        print(f"{index}. Reservación: {row.reservation_id}")
        print(f"Usuario: {row.user_id}")
        print(f"Espacio: {row.space_name} ({row.space_id})")
        print(f"Fecha de cancelación: {row.cancellation_timestamp}")
        print(f"Estado: {row.reservation_status}")
        print(f"Motivo: {row.cancellation_reason}")
        _print_separator()
        print()

    _print_end()


# =========================================================
# CASSANDRA R8
# Historial de participación de usuario por tipo de actividad
# =========================================================

def cassandra_r8_participacion_usuario_tipo_actividad(session):
    """
    Requerimiento 8:
    Consultar la participación histórica de un usuario filtrada por tipo de actividad
    y opcionalmente por rango de fechas, ordenada de la más reciente a la más antigua.
    """

    _ensure_cassandra_keyspace(session)

    _print_query_header(
        "CASSANDRA R8",
        "Participación de usuario por tipo de actividad",
        "Esta consulta muestra la participación histórica de un usuario en un tipo de actividad.",
        "Puedes filtrar por actividad y, si quieres, por rango de fechas.\nEjemplos de usuario: USER001, 1\nEjemplos de actividad: conferencia, taller, deporte, cultura"
    )

    user_input = input("Ingresa el usuario: ").strip()
    activity_type_input = input("Ingresa el tipo de actividad: ").strip()

    user_id = _normalize_user_id(user_input)
    activity_candidates = _activity_type_candidates(activity_type_input)

    print("\nRango de fechas opcional.")
    print("Si quieres ver todo el historial, presiona Enter en ambas preguntas.\n")

    start_date_input = input("Fecha inicial: ").strip()
    end_date_input = input("Fecha final: ").strip()

    use_date_range = start_date_input != "" or end_date_input != ""

    if use_date_range and (start_date_input == "" or end_date_input == ""):
        print("Para filtrar por rango debes ingresar fecha inicial y fecha final.")
        return

    if not use_date_range:
        query = """
            SELECT user_id,
                   activity_type,
                   event_id,
                   event_name,
                   attendance_status,
                   attendance_timestamp
            FROM participation_by_user_activity_type
            WHERE user_id = %s
              AND activity_type = %s
            ORDER BY attendance_timestamp DESC;
        """

        rows = []
        selected_activity_type = None

        for activity_type in activity_candidates:
            rows = list(session.execute(query, (user_id, activity_type)))

            if rows:
                selected_activity_type = activity_type
                break

    else:
        start_date = _parse_date_input(start_date_input)
        end_date = _parse_date_input(end_date_input)

        if start_date is None or end_date is None:
            return

        if start_date > end_date:
            print("La fecha inicial no puede ser mayor que la fecha final.")
            return

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

        query = """
            SELECT user_id,
                   activity_type,
                   event_id,
                   event_name,
                   attendance_status,
                   attendance_timestamp
            FROM participation_by_user_activity_type
            WHERE user_id = %s
              AND activity_type = %s
              AND attendance_timestamp >= %s
              AND attendance_timestamp < %s
            ORDER BY attendance_timestamp DESC;
        """

        rows = []
        selected_activity_type = None

        for activity_type in activity_candidates:
            rows = list(
                session.execute(
                    query,
                    (user_id, activity_type, start_datetime, end_datetime)
                )
            )

            if rows:
                selected_activity_type = activity_type
                break

    if not rows:
        print(f"No se encontró participación para el usuario {user_id} en la actividad ingresada.")
        print("Revisa que el tipo de actividad esté escrito igual que en tus datos.")
        return

    print("\n===== PARTICIPACIÓN POR TIPO DE ACTIVIDAD =====\n")
    print(f"Usuario consultado: {user_id}")
    print(f"Tipo de actividad: {selected_activity_type}")
    print(f"Participaciones encontradas: {len(rows)}\n")

    for index, row in enumerate(rows, start=1):
        _print_separator()
        print(f"{index}. Evento: {row.event_name} ({row.event_id})")
        print(f"Tipo de actividad: {row.activity_type}")
        print(f"Fecha de participación: {row.attendance_timestamp}")
        print(f"Estado: {row.attendance_status}")
        _print_separator()
        print()

    _print_end()