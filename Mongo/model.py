import logging

log = logging.getLogger()

EVENT_SCHEMA = {
    "eventid": "EVT001",
    "eventname": "Taller de Bases No Relacionales",
    "eventtype": "academico",
    "description": "Sesión introductoria sobre MongoDB, Cassandra y Dgraph",
    "date": "2026-04-23",
    "time": "10:00",
    "capacity": 40,
    "registeredattendees": 28,
    "spaceinfo": {
        "spaceid": "SPC101",
        "spacename": "Sala de Colaboración segundo piso",
        "spacetype": "sala_estudio",
        "location": "Edificio T"
    },
    "organizerinfo": {
        "organizerid": "ORG01",
        "organizername": "Departamento de Ingeniería",
        "organizerarea": "Académica"
    },
    "status": "active"
}

def create_indexes(db):
    log.info("Creating indexes for MongoDB collection events")
    db.events.create_index("eventid", unique=True)
    db.events.create_index([("eventtype", 1), ("date", 1)])
    db.events.create_index([("organizerinfo.organizername", 1)])
