import csv
from datetime import datetime
from connect import get_mongo_db, get_cassandra_session, get_dgraph_client


DATA_PATH = "data/"


def read_csv(filename):
    with open(DATA_PATH + filename, mode="r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


# =========================
# MONGODB
# =========================

def populate_mongo():
    db = get_mongo_db()

    events = read_csv("events.csv")
    spaces = read_csv("spaces.csv")
    reservations = read_csv("reservations.csv")

    db.events.delete_many({})
    db.spaces.delete_many({})
    db.reservations.delete_many({})

    events_docs = []
    for row in events:
        events_docs.append({
            "event_id": row["event_id"],
            "event_name": row["event_name"],
            "event_type": row["event_type"],
            "description": row["description"],
            "date": datetime.strptime(row["date"], "%Y-%m-%d"),
            "time": row["time"],
            "capacity": int(row["capacity"]),
            "registered_attendees": int(row["registered_attendees"]),
            "available_seats": int(row["available_seats"]),
            "space_info": {
                "space_id": row["space_id"],
                "space_name": row["space_name"],
                "space_type": row["space_type"]
            },
            "organizer_info": {
                "organizer_id": row["organizer_id"],
                "organizer_name": row["organizer_name"],
                "department": row["department"]
            }
        })

    spaces_docs = []
    for row in spaces:
        spaces_docs.append({
            "space_id": row["space_id"],
            "space_name": row["space_name"],
            "space_type": row["space_type"],
            "capacity": int(row["capacity"]),
            "availability_status": row["availability_status"],
            "available_slots": [
                {
                    "date": datetime.strptime(row["available_date"], "%Y-%m-%d"),
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "status": row["slot_status"]
                }
            ]
        })

    reservations_docs = []
    for row in reservations:
        reservations_docs.append({
            "reservation_id": row["reservation_id"],
            "space_id": row["space_id"],
            "space_name": row["space_name"],
            "space_type": row["space_type"],
            "user": {
                "user_id": row["user_id"],
                "user_name": row["user_name"]
            },
            "date": datetime.strptime(row["date"], "%Y-%m-%d"),
            "time": row["time"],
            "status": row["status"],
            "reservation_type": row["reservation_type"]
        })

    if events_docs:
        db.events.insert_many(events_docs)

    if spaces_docs:
        db.spaces.insert_many(spaces_docs)

    if reservations_docs:
        db.reservations.insert_many(reservations_docs)

    db.events.create_index("event_id")
    db.events.create_index([("event_type", 1), ("date", 1)])
    db.events.create_index("organizer_info.department")

    db.spaces.create_index("space_type")
    db.spaces.create_index("availability_status")

    db.reservations.create_index([("space_id", 1), ("date", 1)])
    db.reservations.create_index("space_type")

    print("MongoDB poblado correctamente.")


# =========================
# CASSANDRA
# =========================

def create_cassandra_tables(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS conviveiteso
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)

    session.set_keyspace("conviveiteso")

    session.execute("""
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
    """)

    session.execute("""
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
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS attendance_by_event_date (
            event_id text,
            event_date date,
            attendance_timestamp timestamp,
            user_id text,
            event_name text,
            attendance_status text,
            PRIMARY KEY ((event_id, event_date), attendance_timestamp)
        ) WITH CLUSTERING ORDER BY (attendance_timestamp ASC);
    """)

    session.execute("""
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
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS user_activity_by_date (
            user_id text,
            activity_date date,
            activity_timestamp timestamp,
            activity_type text,
            related_id text,
            details text,
            PRIMARY KEY ((user_id, activity_date), activity_timestamp)
        ) WITH CLUSTERING ORDER BY (activity_timestamp DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS checkins_by_space (
            space_id text,
            checkin_timestamp timestamp,
            user_id text,
            space_name text,
            activity_context text,
            status text,
            PRIMARY KEY (space_id, checkin_timestamp)
        ) WITH CLUSTERING ORDER BY (checkin_timestamp DESC);
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS cancelled_reservations_by_user (
            user_id text,
            cancellation_timestamp timestamp,
            reservation_id text,
            space_id text,
            space_name text,
            reservation_status text,
            cancellation_reason text,
            PRIMARY KEY (user_id, cancellation_timestamp)
        ) WITH CLUSTERING ORDER BY (cancellation_timestamp DESC);
    """)

    session.execute("""
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
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS participation_by_user_activity_type (
            user_id text,
            activity_type text,
            attendance_timestamp timestamp,
            event_id text,
            event_name text,
            attendance_status text,
            PRIMARY KEY ((user_id, activity_type), attendance_timestamp)
        ) WITH CLUSTERING ORDER BY (attendance_timestamp DESC);
    """)


def populate_cassandra():
    session = get_cassandra_session()
    create_cassandra_tables(session)

    attendance = read_csv("attendance.csv")
    reservations = read_csv("reservations.csv")
    checkins = read_csv("checkins.csv")

    for row in attendance:
        attendance_timestamp = datetime.strptime(row["attendance_timestamp"], "%Y-%m-%d %H:%M:%S")
        event_date = datetime.strptime(row["event_date"], "%Y-%m-%d").date()

        session.execute("""
            INSERT INTO attendance_by_user
            (user_id, attendance_timestamp, event_id, event_name, event_type, attendance_status, event_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row["user_id"],
            attendance_timestamp,
            row["event_id"],
            row["event_name"],
            row["event_type"],
            row["attendance_status"],
            event_date
        ))

        session.execute("""
            INSERT INTO attendance_by_event_date
            (event_id, event_date, attendance_timestamp, user_id, event_name, attendance_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["event_id"],
            event_date,
            attendance_timestamp,
            row["user_id"],
            row["event_name"],
            row["attendance_status"]
        ))

        session.execute("""
            INSERT INTO participation_by_user_activity_type
            (user_id, activity_type, attendance_timestamp, event_id, event_name, attendance_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["user_id"],
            row["event_type"],
            attendance_timestamp,
            row["event_id"],
            row["event_name"],
            row["attendance_status"]
        ))

        session.execute("""
            INSERT INTO user_activity_by_date
            (user_id, activity_date, activity_timestamp, activity_type, related_id, details)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["user_id"],
            event_date,
            attendance_timestamp,
            "attendance",
            row["event_id"],
            f"Asistencia registrada al evento {row['event_name']}"
        ))

    for row in reservations:
        reservation_timestamp = datetime.strptime(row["reservation_timestamp"], "%Y-%m-%d %H:%M:%S")
        usage_date = datetime.strptime(row["date"], "%Y-%m-%d").date()

        session.execute("""
            INSERT INTO reservations_by_user
            (user_id, reservation_timestamp, reservation_id, space_id, space_name, space_type,
             reservation_type, reservation_status, usage_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row["user_id"],
            reservation_timestamp,
            row["reservation_id"],
            row["space_id"],
            row["space_name"],
            row["space_type"],
            row["reservation_type"],
            row["status"],
            usage_date
        ))

        session.execute("""
            INSERT INTO space_usage_by_space_date
            (space_id, usage_date, usage_timestamp, user_id, space_name, activity_type, related_event_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row["space_id"],
            usage_date,
            reservation_timestamp,
            row["user_id"],
            row["space_name"],
            row["reservation_type"],
            row.get("related_event_id", ""),
            row["status"]
        ))

        session.execute("""
            INSERT INTO user_activity_by_date
            (user_id, activity_date, activity_timestamp, activity_type, related_id, details)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["user_id"],
            usage_date,
            reservation_timestamp,
            "reservation",
            row["reservation_id"],
            f"Reservación del espacio {row['space_name']}"
        ))

        if row["status"] == "cancelled":
            cancellation_timestamp = datetime.strptime(row["cancellation_timestamp"], "%Y-%m-%d %H:%M:%S")

            session.execute("""
                INSERT INTO cancelled_reservations_by_user
                (user_id, cancellation_timestamp, reservation_id, space_id, space_name,
                 reservation_status, cancellation_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row["user_id"],
                cancellation_timestamp,
                row["reservation_id"],
                row["space_id"],
                row["space_name"],
                row["status"],
                row["cancellation_reason"]
            ))

            session.execute("""
                INSERT INTO cancelled_reservations_by_space
                (space_id, cancellation_timestamp, reservation_id, user_id, space_name,
                 reservation_status, cancellation_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row["space_id"],
                cancellation_timestamp,
                row["reservation_id"],
                row["user_id"],
                row["space_name"],
                row["status"],
                row["cancellation_reason"]
            ))

    for row in checkins:
        checkin_timestamp = datetime.strptime(row["checkin_timestamp"], "%Y-%m-%d %H:%M:%S")

        session.execute("""
            INSERT INTO checkins_by_space
            (space_id, checkin_timestamp, user_id, space_name, activity_context, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["space_id"],
            checkin_timestamp,
            row["user_id"],
            row["space_name"],
            row["activity_context"],
            row["status"]
        ))

    print("Cassandra poblado correctamente.")


# =========================
# DGRAPH
# =========================

def set_dgraph_schema(client):
    schema = """
    user_id: int @index(int) .
    user_name: string .
    email: string .
    status: string .
    campus_id: string .

    role_id: int @index(int) .
    role_type: string @index(hash) .
    role_scope: string .

    event_id: int @index(int) .
    event_name: string .
    event_type: string @index(term) .
    event_date: datetime .
    event_status: string .

    organizer_id: int @index(int) .
    organizer_name: string .
    department: string @index(hash) .

    space_id: int @index(int) .
    space_name: string .
    space_type: string .
    capacity: int .
    location: geo .

    has_role: uid @reverse .
    participates_in: uid @reverse .
    organized_by: uid @reverse .
    takes_place_in: uid @reverse .
    uses_space: uid @reverse .

    type User {
        user_id
        user_name
        email
        status
        campus_id
        has_role
        participates_in
        uses_space
    }

    type Role {
        role_id
        role_type
        role_scope
    }

    type Event {
        event_id
        event_name
        event_type
        event_date
        event_status
        organized_by
        takes_place_in
    }

    type Organizer {
        organizer_id
        organizer_name
        department
    }

    type Space {
        space_id
        space_name
        space_type
        capacity
        location
    }
    """

    client.alter_schema(schema)


def populate_dgraph():
    client = get_dgraph_client()
    client.alter_drop_all()
    set_dgraph_schema(client)

    users = read_csv("users.csv")
    roles = read_csv("roles.csv")
    spaces = read_csv("spaces.csv")
    organizers = read_csv("organizers.csv")
    events = read_csv("events.csv")
    attendance = read_csv("attendance.csv")
    reservations = read_csv("reservations.csv")

    txn = client.txn()

    try:
        mutation_objects = []

        role_uids = {}
        for row in roles:
            obj = {
                "uid": "_:" + row["role_id"],
                "dgraph.type": "Role",
                "role_id": int(row["role_id"].replace("ROLE", "")),
                "role_type": row["role_type"],
                "role_scope": row["role_scope"]
            }
            role_uids[row["role_id"]] = obj["uid"]
            mutation_objects.append(obj)

        user_uids = {}
        for row in users:
            obj = {
                "uid": "_:" + row["user_id"],
                "dgraph.type": "User",
                "user_id": int(row["user_id"].replace("USER", "")),
                "user_name": row["user_name"],
                "email": row["email"],
                "status": row["status"],
                "campus_id": row["campus_id"],
                "has_role": {
                    "uid": role_uids[row["role_id"]]
                }
            }
            user_uids[row["user_id"]] = obj["uid"]
            mutation_objects.append(obj)

        space_uids = {}
        for row in spaces:
            obj = {
                "uid": "_:" + row["space_id"],
                "dgraph.type": "Space",
                "space_id": int(row["space_id"].replace("SPC", "")),
                "space_name": row["space_name"],
                "space_type": row["space_type"],
                "capacity": int(row["capacity"])
            }
            space_uids[row["space_id"]] = obj["uid"]
            mutation_objects.append(obj)

        organizer_uids = {}
        for row in organizers:
            obj = {
                "uid": "_:" + row["organizer_id"],
                "dgraph.type": "Organizer",
                "organizer_id": int(row["organizer_id"].replace("ORG", "")),
                "organizer_name": row["organizer_name"],
                "department": row["department"]
            }
            organizer_uids[row["organizer_id"]] = obj["uid"]
            mutation_objects.append(obj)

        event_uids = {}
        for row in events:
            obj = {
                "uid": "_:" + row["event_id"],
                "dgraph.type": "Event",
                "event_id": int(row["event_id"].replace("EVT", "")),
                "event_name": row["event_name"],
                "event_type": row["event_type"],
                "event_date": row["date"] + "T" + row["time"] + ":00",
                "event_status": row["event_status"],
                "organized_by": {
                    "uid": organizer_uids[row["organizer_id"]]
                },
                "takes_place_in": {
                    "uid": space_uids[row["space_id"]]
                }
            }
            event_uids[row["event_id"]] = obj["uid"]
            mutation_objects.append(obj)

        for row in attendance:
            if row["user_id"] in user_uids and row["event_id"] in event_uids:
                mutation_objects.append({
                    "uid": user_uids[row["user_id"]],
                    "participates_in": {
                        "uid": event_uids[row["event_id"]]
                    }
                })

        for row in reservations:
            if row["user_id"] in user_uids and row["space_id"] in space_uids:
                mutation_objects.append({
                    "uid": user_uids[row["user_id"]],
                    "uses_space": {
                        "uid": space_uids[row["space_id"]]
                    }
                })

        txn.mutate(set_obj=mutation_objects)
        txn.commit()

        print("Dgraph poblado correctamente.")

    finally:
        txn.discard()


# =========================
# EJECUCIÓN GENERAL
# =========================

def main():
    print("Iniciando carga de datos en las 3 bases...\n")

    populate_mongo()
    populate_cassandra()
    populate_dgraph()

    print("\nCarga de datos finalizada correctamente.")


if __name__ == "__main__":
    main()