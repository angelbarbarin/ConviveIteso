CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS attendance_by_user (
        user_id text,
        attendance_timestamp timestamp,
        event_id text,
        event_name text,
        event_type text,
        attendance_status text,
        event_date date,
        PRIMARY KEY (user_id, attendance_timestamp)
    ) WITH CLUSTERING ORDER BY (attendance_timestamp DESC);
    """,
    """
    CREATE TABLE IF NOT EXISTS reservations_by_user (
        user_id text,
        reservation_timestamp timestamp,
        reservation_id text,
        space_id text,
        space_name text,
        space_type text,
        reservation_type text,
        reservation_status text,
        usage_date date,
        PRIMARY KEY (user_id, reservation_timestamp)
    ) WITH CLUSTERING ORDER BY (reservation_timestamp DESC);
    """,
    """
    CREATE TABLE IF NOT EXISTS attendance_by_event_date (
        event_id text,
        event_date date,
        attendance_timestamp timestamp,
        user_id text,
        event_name text,
        attendance_status text,
        PRIMARY KEY ((event_id, event_date), attendance_timestamp)
    ) WITH CLUSTERING ORDER BY (attendance_timestamp ASC);
    """,
    """
    CREATE TABLE IF NOT EXISTS space_usage_by_space_date (
        space_id text,
        usage_date date,
        usage_timestamp timestamp,
        user_id text,
        space_name text,
        activity_type text,
        related_event_id text,
        status text,
        PRIMARY KEY ((space_id, usage_date), usage_timestamp)
    ) WITH CLUSTERING ORDER BY (usage_timestamp ASC);
    """,
    """
    CREATE TABLE IF NOT EXISTS user_activity_by_date (
        user_id text,
        activity_date date,
        activity_timestamp timestamp,
        activity_type text,
        related_id text,
        details text,
        PRIMARY KEY ((user_id, activity_date), activity_timestamp)
    ) WITH CLUSTERING ORDER BY (activity_timestamp DESC);
    """,
    """
    CREATE TABLE IF NOT EXISTS checkins_by_space (
        space_id text,
        checkin_timestamp timestamp,
        user_id text,
        space_name text,
        activity_context text,
        status text,
        PRIMARY KEY (space_id, checkin_timestamp)
    ) WITH CLUSTERING ORDER BY (checkin_timestamp DESC);
    """,
    """
    CREATE TABLE IF NOT EXISTS cancelled_reservations_by_user (
        user_id text,
        cancellation_timestamp timestamp,
        reservation_id text,
        space_id text,
        reservation_status text,
        cancellation_reason text,
        PRIMARY KEY (user_id, cancellation_timestamp)
    ) WITH CLUSTERING ORDER BY (cancellation_timestamp DESC);
    """,
    """
    CREATE TABLE IF NOT EXISTS cancelled_reservations_by_space (
        space_id text,
        cancellation_timestamp timestamp,
        reservation_id text,
        user_id text,
        space_name text,
        reservation_status text,
        cancellation_reason text,
        PRIMARY KEY (space_id, cancellation_timestamp)
    ) WITH CLUSTERING ORDER BY (cancellation_timestamp DESC);
    """,
    """
    CREATE TABLE IF NOT EXISTS participation_by_user_activity_type (
        user_id text,
        activity_type text,
        attendance_timestamp timestamp,
        event_id text,
        event_name text,
        attendance_status text,
        PRIMARY KEY ((user_id, activity_type), attendance_timestamp)
    ) WITH CLUSTERING ORDER BY (attendance_timestamp DESC);
    """
]


def create_schema(session):
    for query in CREATE_TABLES:
        session.execute(query)
    print("[OK] Esquema de Cassandra creado")