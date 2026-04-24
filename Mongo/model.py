from pymongo import ASCENDING, DESCENDING


EVENT_SCHEMA_EXAMPLE = {
    "event_id": "EV001",
    "event_name": "Conferencia de Innovación",
    "event_type": "académico",
    "description": "Evento enfocado en innovación universitaria",
    "date": "2026-05-10",
    "time": "10:00",
    "capacity": 200,
    "registered_attendees": 150,
    "available_seats": 50,
    "space_info": {
        "space_id": "SP001",
        "space_name": "Auditorio A",
        "space_type": "auditorio"
    },
    "organizer_info": {
        "organizer_id": "ORG001",
        "organizer_name": "Coordinación de Ingeniería",
        "department": "Ingeniería"
    }
}

SPACE_SCHEMA_EXAMPLE = {
    "space_id": "SP001",
    "space_name": "Auditorio A",
    "space_type": "auditorio",
    "capacity": 200,
    "availability_status": "available",
    "available_slots": [
        {
            "date": "2026-05-10",
            "start_time": "08:00",
            "end_time": "10:00",
            "status": "available"
        }
    ]
}

RESERVATION_SCHEMA_EXAMPLE = {
    "reservation_id": "RS001",
    "space_id": "SP001",
    "space_name": "Auditorio A",
    "space_type": "auditorio",
    "user": {
        "user_id": "U001",
        "user_name": "Fabián"
    },
    "date": "2026-05-10",
    "time": "12:00",
    "status": "confirmed",
    "reservation_type": "academic"
}


def create_indexes(db):
    db.events.create_index([("event_id", ASCENDING)], unique=True)
    db.events.create_index([("event_type", ASCENDING), ("date", ASCENDING)])
    db.events.create_index([("organizer_info.department", ASCENDING), ("date", ASCENDING)])
    db.events.create_index([("event_type", ASCENDING), ("registered_attendees", DESCENDING)])

    db.spaces.create_index([("space_type", ASCENDING), ("availability_status", ASCENDING)])
    db.spaces.create_index([("available_slots.date", ASCENDING), ("available_slots.status", ASCENDING)])

    db.reservations.create_index([("space_id", ASCENDING), ("date", ASCENDING)])
    db.reservations.create_index([("space_type", ASCENDING), ("date", ASCENDING)])

    print("[OK] Índices de MongoDB creados")


def aggregation_total_events_by_type(start_date, end_date):
    return [
        {
            "$match": {
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": "$event_type",
                "total_events": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "event_type": "$_id",
                "total_events": 1
            }
        }
    ]


def aggregation_total_reservations_by_space_type(start_date, end_date):
    return [
        {
            "$match": {
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": "$space_type",
                "total_reservations": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "space_type": "$_id",
                "total_reservations": 1
            }
        }
    ]


def aggregation_top_demand_events(event_type=None):
    pipeline = []

    if event_type:
        pipeline.append({
            "$match": {"event_type": event_type}
        })

    pipeline.extend([
        {
            "$addFields": {
                "occupancy_percentage": {
                    "$multiply": [
                        {"$divide": ["$registered_attendees", "$capacity"]},
                        100
                    ]
                }
            }
        },
        {
            "$sort": {
                "occupancy_percentage": -1
            }
        },
        {
            "$project": {
                "_id": 0,
                "event_name": 1,
                "capacity": 1,
                "registered_attendees": 1,
                "occupancy_percentage": 1
            }
        }
    ])

    return pipeline