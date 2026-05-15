from datetime import datetime


def _parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def mongo_r1_evento_especifico(mongo_db):
    event_id = input("Ingresa el event_id: ").strip()

    result = mongo_db.events.find_one(
        {"event_id": event_id},
        {
            "_id": 0,
            "event_id": 1,
            "event_name": 1,
            "event_type": 1,
            "description": 1,
            "date": 1,
            "time": 1,
            "space_info": 1,
            "organizer_info": 1,
            "capacity": 1
        }
    )

    if result:
        print("\nResultado:")
        print(result)
    else:
        print("\nNo se encontró un evento con ese event_id.")


def mongo_r2_eventos_por_tipo_y_fecha(mongo_db):
    event_type = input("Ingresa el tipo de evento: ").strip()
    start_date = input("Ingresa la fecha inicial (YYYY-MM-DD): ").strip()
    end_date = input("Ingresa la fecha final (YYYY-MM-DD) o deja vacío si es solo un día: ").strip()

    start = _parse_date(start_date)
    end = _parse_date(end_date) if end_date else start

    results = mongo_db.events.find(
        {
            "event_type": event_type,
            "date": {"$gte": start, "$lte": end}
        },
        {
            "_id": 0,
            "event_id": 1,
            "event_name": 1,
            "date": 1,
            "space_name": "$space_info.space_name",
            "space_info.space_name": 1,
            "available_seats": 1
        }
    )

    resultados = list(results)

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print({
                "event_id": doc.get("event_id"),
                "event_name": doc.get("event_name"),
                "date": doc.get("date"),
                "space_name": doc.get("space_info", {}).get("space_name"),
                "available_seats": doc.get("available_seats")
            })
    else:
        print("\nNo se encontraron eventos para ese tipo y fecha.")


def mongo_r3_espacios_disponibles_para_reserva(mongo_db):
    space_type = input("Ingresa el tipo de espacio: ").strip()
    fecha = input("Ingresa la fecha deseada (YYYY-MM-DD): ").strip()
    hora = input("Ingresa la hora deseada (HH:MM): ").strip()

    fecha_dt = _parse_date(fecha)

    results = mongo_db.spaces.find(
        {
            "space_type": space_type,
            "availability_status": "available",
            "available_slots": {
                "$elemMatch": {
                    "date": fecha_dt,
                    "start_time": {"$lte": hora},
                    "end_time": {"$gte": hora},
                    "status": "available"
                }
            }
        },
        {
            "_id": 0,
            "space_id": 1,
            "space_name": 1,
            "capacity": 1,
            "availability_status": 1
        }
    )

    resultados = list(results)

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print(doc)
    else:
        print("\nNo se encontraron espacios disponibles para ese horario.")


def mongo_r4_reservaciones_espacio_fecha(mongo_db):
    space_id = input("Ingresa el space_id: ").strip()
    fecha = input("Ingresa la fecha (YYYY-MM-DD): ").strip()

    fecha_dt = _parse_date(fecha)

    results = mongo_db.reservations.find(
        {
            "space_id": space_id,
            "date": fecha_dt
        },
        {
            "_id": 0,
            "reservation_id": 1,
            "user": 1,
            "time": 1,
            "status": 1
        }
    )

    resultados = list(results)

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print(doc)
    else:
        print("\nNo se encontraron reservaciones para ese espacio en esa fecha.")


def mongo_r5_eventos_por_organizador(mongo_db):
    department = input("Ingresa el departamento o área organizadora: ").strip()

    results = mongo_db.events.find(
        {
            "organizer_info.department": department
        },
        {
            "_id": 0,
            "event_id": 1,
            "event_name": 1,
            "date": 1,
            "space_info.space_name": 1
        }
    )

    resultados = list(results)

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print({
                "event_id": doc.get("event_id"),
                "event_name": doc.get("event_name"),
                "date": doc.get("date"),
                "space_name": doc.get("space_info", {}).get("space_name")
            })
    else:
        print("\nNo se encontraron eventos para ese departamento.")


def mongo_r6_total_eventos_por_tipo(mongo_db):
    start_date = input("Ingresa la fecha inicial (YYYY-MM-DD): ").strip()
    end_date = input("Ingresa la fecha final (YYYY-MM-DD): ").strip()

    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": _parse_date(start_date),
                    "$lte": _parse_date(end_date)
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

    resultados = list(mongo_db.events.aggregate(pipeline))

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print(doc)
    else:
        print("\nNo se encontraron eventos en ese periodo.")


def mongo_r7_total_reservaciones_por_tipo_espacio(mongo_db):
    start_date = input("Ingresa la fecha inicial (YYYY-MM-DD): ").strip()
    end_date = input("Ingresa la fecha final (YYYY-MM-DD): ").strip()

    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": _parse_date(start_date),
                    "$lte": _parse_date(end_date)
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

    resultados = list(mongo_db.reservations.aggregate(pipeline))

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print(doc)
    else:
        print("\nNo se encontraron reservaciones en ese periodo.")


def mongo_r8_eventos_mayor_demanda(mongo_db):
    event_type = input("Ingresa el tipo de evento (opcional, enter para omitir): ").strip()

    pipeline = []

    if event_type:
        pipeline.append({
            "$match": {
                "event_type": event_type
            }
        })

    pipeline.extend([
        {
            "$addFields": {
                "occupancy_percentage": {
                    "$cond": [
                        {"$gt": ["$capacity", 0]},
                        {
                            "$multiply": [
                                {"$divide": ["$registered_attendees", "$capacity"]},
                                100
                            ]
                        },
                        0
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

    resultados = list(mongo_db.events.aggregate(pipeline))

    if resultados:
        print("\nResultados:")
        for doc in resultados:
            print(doc)
    else:
        print("\nNo se encontraron eventos para ese criterio.")