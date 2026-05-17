from datetime import datetime, timedelta


def _parse_date(date_str):
    return datetime.strptime(date_str.strip(), "%Y-%m-%d")


def _format_date(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _print_no_results(message):
    print("\n===== SIN RESULTADOS =====")
    print(message)
    print("Prueba con otro dato de ejemplo o verifica que la base esté poblada.")


def mongo_r1_evento_especifico(mongo_db):
    print("\n===== MONGODB R1 =====")
    print("Consulta de un evento específico")
    print("\nEsta consulta permite buscar un evento usando su código.")
    print("Ejemplo válido: EVT001\n")

    event_id = input("Ingresa el event_id: ").strip().upper()

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
            "capacity": 1,
            "registered_attendees": 1,
            "available_seats": 1
        }
    )

    if not result:
        _print_no_results(f"No se encontró un evento con el código {event_id}.")
        return

    space_info = result.get("space_info", {})
    organizer_info = result.get("organizer_info", {})

    print("\n===== EVENTO ENCONTRADO =====\n")
    print("--------------------------------------------------")
    print(f"Evento: {result.get('event_name')} ({result.get('event_id')})")
    print(f"Tipo de evento: {result.get('event_type')}")
    print(f"Descripción: {result.get('description')}")
    print(f"Fecha: {_format_date(result.get('date'))}")
    print(f"Hora: {result.get('time')}")
    print(f"Espacio: {space_info.get('space_name')} ({space_info.get('space_id')})")
    print(f"Tipo de espacio: {space_info.get('space_type')}")
    print(f"Organizador: {organizer_info.get('organizer_name')}")
    print(f"Departamento: {organizer_info.get('department')}")
    print(f"Capacidad: {result.get('capacity')} personas")
    print(f"Asistentes registrados: {result.get('registered_attendees')}")
    print(f"Lugares disponibles: {result.get('available_seats')}")
    print("--------------------------------------------------")
    print("\nConsulta finalizada.")


def mongo_r2_eventos_por_tipo_y_fecha(mongo_db):
    print("\n===== MONGODB R2 =====")
    print("Eventos por tipo y fecha")
    print("\nEsta consulta busca eventos de cierto tipo dentro de una fecha o rango de fechas.")
    print("Ejemplos válidos:")
    print("- Tipo de evento: Academico")
    print("- Fecha inicial: 2026-05-20")
    print("- Fecha final: 2026-06-10")
    print("Si solo quieres un día, deja vacía la fecha final.\n")

    event_type = input("Ingresa el tipo de evento: ").strip()
    start_date = input("Ingresa la fecha inicial (YYYY-MM-DD): ").strip()
    end_date = input("Ingresa la fecha final (YYYY-MM-DD) o deja vacío si es solo un día: ").strip()

    start = _parse_date(start_date)

    if end_date:
        end = _parse_date(end_date)
    else:
        end = start

    # Incluye todo el día final.
    end = end + timedelta(hours=23, minutes=59, seconds=59)

    resultados = list(mongo_db.events.find(
        {
            "event_type": event_type,
            "date": {"$gte": start, "$lte": end}
        },
        {
            "_id": 0,
            "event_id": 1,
            "event_name": 1,
            "event_type": 1,
            "date": 1,
            "time": 1,
            "space_info": 1,
            "available_seats": 1
        }
    ).sort("date", 1))

    if not resultados:
        _print_no_results("No se encontraron eventos para ese tipo y fecha.")
        return

    print("\n===== EVENTOS ENCONTRADOS =====\n")
    print(f"Tipo solicitado: {event_type}")
    print(f"Eventos encontrados: {len(resultados)}\n")

    for index, event in enumerate(resultados, start=1):
        space_info = event.get("space_info", {})

        print("--------------------------------------------------")
        print(f"{index}. Evento: {event.get('event_name')} ({event.get('event_id')})")
        print(f"Tipo: {event.get('event_type')}")
        print(f"Fecha: {_format_date(event.get('date'))}")
        print(f"Hora: {event.get('time')}")
        print(f"Espacio: {space_info.get('space_name')}")
        print(f"Lugares disponibles: {event.get('available_seats')}")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")


def mongo_r3_espacios_disponibles_para_reserva(mongo_db):
    print("\n===== MONGODB R3 =====")
    print("Espacios disponibles para reserva")
    print("\nEsta consulta permite buscar espacios disponibles según tipo, fecha y hora.")
    print("Ejemplos válidos:")
    print("- Tipo de espacio: auditorio")
    print("- Fecha: 2026-05-10")
    print("- Hora: 10:00\n")

    space_type = input("Ingresa el tipo de espacio: ").strip()
    fecha = input("Ingresa la fecha deseada (YYYY-MM-DD): ").strip()
    hora = input("Ingresa la hora deseada (HH:MM): ").strip()

    fecha_dt = _parse_date(fecha)

    resultados = list(mongo_db.spaces.find(
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
            "space_type": 1,
            "capacity": 1,
            "availability_status": 1
        }
    ))

    if not resultados:
        _print_no_results("No se encontraron espacios disponibles para ese horario.")
        return

    print("\n===== ESPACIOS DISPONIBLES ENCONTRADOS =====\n")
    print(f"Tipo de espacio solicitado: {space_type}")
    print(f"Fecha solicitada: {fecha}")
    print(f"Hora solicitada: {hora}")
    print(f"Espacios encontrados: {len(resultados)}\n")

    for index, space in enumerate(resultados, start=1):
        print("--------------------------------------------------")
        print(f"{index}. Espacio: {space.get('space_name')} ({space.get('space_id')})")
        print(f"Tipo de espacio: {space.get('space_type')}")
        print(f"Capacidad: {space.get('capacity')} personas")
        print(f"Estado: {space.get('availability_status')}")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")


def mongo_r4_reservaciones_espacio_fecha(mongo_db):
    print("\n===== MONGODB R4 =====")
    print("Reservaciones de un espacio en una fecha")
    print("\nEsta consulta muestra las reservaciones registradas para un espacio específico.")
    print("Ejemplos válidos:")
    print("- Space ID: SPC001")
    print("- Fecha: 2026-05-10\n")

    space_id = input("Ingresa el space_id: ").strip().upper()
    fecha = input("Ingresa la fecha (YYYY-MM-DD): ").strip()

    fecha_dt = _parse_date(fecha)

    resultados = list(mongo_db.reservations.find(
        {
            "space_id": space_id,
            "date": fecha_dt
        },
        {
            "_id": 0,
            "reservation_id": 1,
            "space_id": 1,
            "space_name": 1,
            "user": 1,
            "time": 1,
            "status": 1,
            "reservation_type": 1
        }
    ).sort("time", 1))

    if not resultados:
        _print_no_results("No se encontraron reservaciones para ese espacio en esa fecha.")
        return

    print("\n===== RESERVACIONES ENCONTRADAS =====\n")
    print(f"Espacio solicitado: {space_id}")
    print(f"Fecha solicitada: {fecha}")
    print(f"Reservaciones encontradas: {len(resultados)}\n")

    for index, reservation in enumerate(resultados, start=1):
        user = reservation.get("user", {})

        print("--------------------------------------------------")
        print(f"{index}. Reservación: {reservation.get('reservation_id')}")
        print(f"Espacio: {reservation.get('space_name')} ({reservation.get('space_id')})")
        print(f"Usuario: {user.get('user_name')} ({user.get('user_id')})")
        print(f"Hora: {reservation.get('time')}")
        print(f"Tipo de reservación: {reservation.get('reservation_type')}")
        print(f"Estado: {reservation.get('status')}")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")


def mongo_r5_eventos_por_organizador(mongo_db):
    print("\n===== MONGODB R5 =====")
    print("Eventos por organizador o departamento")
    print("\nEsta consulta muestra eventos organizados por un departamento o área específica.")
    print("Ejemplos válidos:")
    print("- Ingenieria")
    print("- Cultura")
    print("- Deportes")
    print("- Bienestar")
    print("- Negocios\n")

    department = input("Ingresa el departamento o área organizadora: ").strip()

    resultados = list(mongo_db.events.find(
        {
            "organizer_info.department": department
        },
        {
            "_id": 0,
            "event_id": 1,
            "event_name": 1,
            "event_type": 1,
            "date": 1,
            "time": 1,
            "space_info": 1,
            "organizer_info": 1
        }
    ).sort("date", 1))

    if not resultados:
        _print_no_results(f"No se encontraron eventos para el departamento {department}.")
        return

    print("\n===== EVENTOS POR DEPARTAMENTO =====\n")
    print(f"Departamento solicitado: {department}")
    print(f"Eventos encontrados: {len(resultados)}\n")

    for index, event in enumerate(resultados, start=1):
        space_info = event.get("space_info", {})
        organizer_info = event.get("organizer_info", {})

        print("--------------------------------------------------")
        print(f"{index}. Evento: {event.get('event_name')} ({event.get('event_id')})")
        print(f"Tipo: {event.get('event_type')}")
        print(f"Fecha: {_format_date(event.get('date'))}")
        print(f"Hora: {event.get('time')}")
        print(f"Espacio: {space_info.get('space_name')}")
        print(f"Organizador: {organizer_info.get('organizer_name')}")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")


def mongo_r6_total_eventos_por_tipo(mongo_db):
    print("\n===== MONGODB R6 =====")
    print("Total de eventos por tipo")
    print("\nEsta agregación cuenta cuántos eventos existen por tipo dentro de un periodo.")
    print("Ejemplo válido:")
    print("- Fecha inicial: 2026-05-01")
    print("- Fecha final: 2026-06-30\n")

    start_date = input("Ingresa la fecha inicial (YYYY-MM-DD): ").strip()
    end_date = input("Ingresa la fecha final (YYYY-MM-DD): ").strip()

    start = _parse_date(start_date)
    end = _parse_date(end_date) + timedelta(hours=23, minutes=59, seconds=59)

    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": start,
                    "$lte": end
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
        },
        {
            "$sort": {
                "total_events": -1
            }
        }
    ]

    resultados = list(mongo_db.events.aggregate(pipeline))

    if not resultados:
        _print_no_results("No se encontraron eventos en ese periodo.")
        return

    print("\n===== TOTAL DE EVENTOS POR TIPO =====\n")
    print(f"Periodo analizado: {start_date} a {end_date}")
    print(f"Tipos de evento encontrados: {len(resultados)}\n")

    for index, doc in enumerate(resultados, start=1):
        evento_texto = "evento" if doc.get("total_events") == 1 else "eventos"

        print("--------------------------------------------------")
        print(f"{index}. Tipo de evento: {doc.get('event_type')}")
        print(f"Total: {doc.get('total_events')} {evento_texto}")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")


def mongo_r7_total_reservaciones_por_tipo_espacio(mongo_db):
    print("\n===== MONGODB R7 =====")
    print("Total de reservaciones por tipo de espacio")
    print("\nEsta agregación cuenta reservaciones agrupadas por tipo de espacio dentro de un periodo.")
    print("Ejemplo válido:")
    print("- Fecha inicial: 2026-05-01")
    print("- Fecha final: 2026-06-30\n")

    start_date = input("Ingresa la fecha inicial (YYYY-MM-DD): ").strip()
    end_date = input("Ingresa la fecha final (YYYY-MM-DD): ").strip()

    start = _parse_date(start_date)
    end = _parse_date(end_date) + timedelta(hours=23, minutes=59, seconds=59)

    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": start,
                    "$lte": end
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
        },
        {
            "$sort": {
                "total_reservations": -1
            }
        }
    ]

    resultados = list(mongo_db.reservations.aggregate(pipeline))

    if not resultados:
        _print_no_results("No se encontraron reservaciones en ese periodo.")
        return

    print("\n===== RESERVACIONES POR TIPO DE ESPACIO =====\n")
    print(f"Periodo analizado: {start_date} a {end_date}")
    print(f"Tipos de espacio encontrados: {len(resultados)}\n")

    for index, doc in enumerate(resultados, start=1):
        reserva_texto = "reservación" if doc.get("total_reservations") == 1 else "reservaciones"

        print("--------------------------------------------------")
        print(f"{index}. Tipo de espacio: {doc.get('space_type')}")
        print(f"Total: {doc.get('total_reservations')} {reserva_texto}")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")


def mongo_r8_eventos_mayor_demanda(mongo_db):
    print("\n===== MONGODB R8 =====")
    print("Eventos con mayor demanda")
    print("\nEsta agregación calcula el porcentaje de ocupación de los eventos.")
    print("Puedes filtrar por tipo de evento o dejar vacío para ver todos.")
    print("Ejemplos válidos:")
    print("- Academico")
    print("- Cultural")
    print("- Deportivo")
    print("- Enter para ver todos\n")

    event_type = input("Ingresa el tipo de evento (opcional): ").strip()

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
                "event_id": 1,
                "event_name": 1,
                "event_type": 1,
                "capacity": 1,
                "registered_attendees": 1,
                "occupancy_percentage": 1
            }
        },
        {
            "$limit": 10
        }
    ])

    resultados = list(mongo_db.events.aggregate(pipeline))

    if not resultados:
        _print_no_results("No se encontraron eventos para ese criterio.")
        return

    print("\n===== EVENTOS CON MAYOR DEMANDA =====\n")

    if event_type:
        print(f"Filtro aplicado: {event_type}")
    else:
        print("Filtro aplicado: todos los tipos de evento")

    print(f"Eventos mostrados: {len(resultados)}\n")

    for index, event in enumerate(resultados, start=1):
        occupancy = event.get("occupancy_percentage", 0)

        print("--------------------------------------------------")
        print(f"{index}. Evento: {event.get('event_name')} ({event.get('event_id')})")
        print(f"Tipo: {event.get('event_type')}")
        print(f"Capacidad: {event.get('capacity')} personas")
        print(f"Asistentes registrados: {event.get('registered_attendees')}")
        print(f"Ocupación: {occupancy:.2f}%")
        print("--------------------------------------------------\n")

    print("Consulta finalizada.")