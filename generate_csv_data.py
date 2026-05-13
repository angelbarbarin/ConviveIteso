import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)


EVENT_TYPES = ["Academico", "Cultural", "Deportivo", "Emprendimiento", "Recreativo"]
RESERVATION_TYPES = ["study", "meeting", "sports", "event"]
CHECKIN_CONTEXTS = ["study_session", "meeting", "practice", "event_attendance", "team_work"]
STATUSES = ["scheduled", "completed"]


def read_csv(filename):
    path = DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(filename, fieldnames, rows):
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{filename} generado con {len(rows)} registros.")


def generate_events(spaces, organizers, total_events=40):
    rows = []
    base_date = datetime(2026, 5, 20)

    event_names = [
        "Hackathon IA", "Torneo Tocho", "Obra Teatro", "Networking Startup",
        "Seminario Datos", "Conferencia Sustentabilidad", "Taller Liderazgo",
        "Mesa Dialogo", "Expo Proyectos", "Clase Magistral",
        "Festival Cultural", "Carrera Campus", "Torneo Basquet",
        "Presentacion Danza", "Foro Innovacion", "Charla Emprendimiento",
        "Panel Egresados", "Taller UX", "Laboratorio Maker",
        "Encuentro Internacional", "Retiro Bienestar", "Cine Foro",
        "Debate Universitario", "Feria Voluntariado", "Demo Day",
        "Taller Finanzas", "Capacitacion Servicio", "Sesión Mentoría",
        "Torneo Ajedrez", "Concierto Campus", "Jornada Salud",
        "Expo Arquitectura", "Seminario Inteligencia Artificial",
        "Charla Ciberseguridad", "Foro Humanidades", "Taller Robotica",
        "Presentacion Teatro", "Clase Abierta", "Festival Deportivo",
        "Encuentro Comunidad"
    ]

    for i in range(1, total_events + 1):
        space = spaces[(i - 1) % len(spaces)]
        organizer = organizers[(i - 1) % len(organizers)]
        event_type = EVENT_TYPES[(i - 1) % len(EVENT_TYPES)]
        capacity = int(space["capacity"])
        registered = random.randint(max(5, capacity // 3), capacity)
        date = base_date + timedelta(days=i // 2)
        hour = random.choice(["09:00", "10:00", "11:00", "13:00", "16:00", "18:00"])

        rows.append({
            "event_id": f"EVT{i:03d}",
            "event_name": event_names[i - 1],
            "event_type": event_type,
            "description": f"Evento universitario de tipo {event_type}",
            "date": date.strftime("%Y-%m-%d"),
            "time": hour,
            "capacity": capacity,
            "registered_attendees": registered,
            "available_seats": capacity - registered,
            "space_id": space["space_id"],
            "space_name": space["space_name"],
            "space_type": space["space_type"],
            "organizer_id": organizer["organizer_id"],
            "organizer_name": organizer["organizer_name"],
            "department": organizer["department"],
            "event_status": random.choice(STATUSES)
        })

    return rows


def generate_attendance(users, events, rows_per_event=10):
    rows = []

    # Usuarios externos para garantizar Dgraph R4
    external_users = [u for u in users if u["role_id"] == "ROLE004"]
    internal_users = [u for u in users if u["role_id"] != "ROLE004"]

    for event_index, event in enumerate(events):
        event_date = datetime.strptime(event["date"], "%Y-%m-%d")

        # Overlap intencional: usuarios se repiten en varios eventos
        start_index = (event_index * 4) % len(internal_users)
        selected_users = []

        for j in range(rows_per_event):
            selected_users.append(internal_users[(start_index + j) % len(internal_users)])

        # Cada 4 eventos metemos invitados externos
        if event_index % 4 == 0:
            selected_users.extend(random.sample(external_users, min(3, len(external_users))))

        for idx, user in enumerate(selected_users):
            attendance_time = event_date.replace(
                hour=random.choice([8, 9, 10, 11, 13, 16, 18]),
                minute=random.randint(0, 55),
                second=0
            )

            rows.append({
                "user_id": user["user_id"],
                "attendance_timestamp": attendance_time.strftime("%Y-%m-%d %H:%M:%S"),
                "event_id": event["event_id"],
                "event_name": event["event_name"],
                "event_type": event["event_type"],
                "attendance_status": "checked_in",
                "event_date": event["date"]
            })

    return rows


def generate_reservations(users, spaces, events, total_reservations=200):
    rows = []
    base_date = datetime(2026, 5, 10)

    for i in range(1, total_reservations + 1):
        user = users[(i - 1) % len(users)]
        space = spaces[(i - 1) % len(spaces)]
        event = random.choice(events)

        reservation_type = random.choice(RESERVATION_TYPES)
        status = "cancelled" if random.random() < 0.15 else "confirmed"

        date = base_date + timedelta(days=i % 30)
        reservation_timestamp = date - timedelta(days=random.randint(1, 7))
        time = random.choice(["09:00", "10:00", "11:00", "13:00", "15:00", "17:00", "18:00"])

        cancellation_timestamp = ""
        cancellation_reason = ""

        if status == "cancelled":
            cancellation_timestamp = (
                reservation_timestamp + timedelta(hours=random.randint(2, 36))
            ).strftime("%Y-%m-%d %H:%M:%S")
            cancellation_reason = random.choice([
                "Cambio de horario",
                "Espacio ya no requerido",
                "Evento cancelado",
                "Conflicto de agenda"
            ])

        related_event_id = event["event_id"] if reservation_type == "event" else ""

        rows.append({
            "reservation_id": f"RES{i:03d}",
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "space_id": space["space_id"],
            "space_name": space["space_name"],
            "space_type": space["space_type"],
            "date": date.strftime("%Y-%m-%d"),
            "time": time,
            "status": status,
            "reservation_type": reservation_type,
            "reservation_timestamp": reservation_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "cancellation_timestamp": cancellation_timestamp,
            "cancellation_reason": cancellation_reason,
            "related_event_id": related_event_id
        })

    return rows


def generate_checkins(users, spaces, total_checkins=250):
    rows = []
    base_date = datetime(2026, 5, 10)

    for i in range(1, total_checkins + 1):
        user = users[(i - 1) % len(users)]
        space = spaces[(i - 1) % len(spaces)]

        checkin_date = base_date + timedelta(days=i % 30)
        checkin_time = checkin_date.replace(
            hour=random.choice([8, 9, 10, 11, 13, 15, 17, 18]),
            minute=random.randint(0, 55),
            second=0
        )

        rows.append({
            "space_id": space["space_id"],
            "checkin_timestamp": checkin_time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user["user_id"],
            "space_name": space["space_name"],
            "activity_context": random.choice(CHECKIN_CONTEXTS),
            "status": random.choice(["active", "completed"])
        })

    return rows


def main():
    users = read_csv("users.csv")
    spaces = read_csv("spaces.csv")
    organizers = read_csv("organizers.csv")

    events = generate_events(spaces, organizers, total_events=40)
    attendance = generate_attendance(users, events, rows_per_event=10)
    reservations = generate_reservations(users, spaces, events, total_reservations=200)
    checkins = generate_checkins(users, spaces, total_checkins=250)

    write_csv(
        "events.csv",
        [
            "event_id", "event_name", "event_type", "description", "date", "time",
            "capacity", "registered_attendees", "available_seats",
            "space_id", "space_name", "space_type",
            "organizer_id", "organizer_name", "department", "event_status"
        ],
        events
    )

    write_csv(
        "attendance.csv",
        [
            "user_id", "attendance_timestamp", "event_id", "event_name",
            "event_type", "attendance_status", "event_date"
        ],
        attendance
    )

    write_csv(
        "reservations.csv",
        [
            "reservation_id", "user_id", "user_name", "space_id", "space_name",
            "space_type", "date", "time", "status", "reservation_type",
            "reservation_timestamp", "cancellation_timestamp",
            "cancellation_reason", "related_event_id"
        ],
        reservations
    )

    write_csv(
        "checkins.csv",
        [
            "space_id", "checkin_timestamp", "user_id", "space_name",
            "activity_context", "status"
        ],
        checkins
    )

    print("\nCSV generados correctamente.")
    print("Ahora puedes ejecutar: python populate.py")


if __name__ == "__main__":
    main()