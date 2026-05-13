# =========================================================
# CONVIVE ITESO - DGRAPH QUERIES
# =========================================================

import json


# =========================================================
# UTILIDADES GENERALES
# =========================================================

def ensure_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def resolve_user_input(client, user_input):
    """
    Permite buscar usuario por:
    - USER001
    - A001 / D066 / AD081 / EXT091
    - Nombre, ejemplo: Diego Alvarez
    """

    user_input = user_input.strip()

    if not user_input:
        return None

    # Caso 1: USER001
    if user_input.upper().startswith("USER"):
        try:
            user_id = int(user_input.upper().replace("USER", ""))
            return user_id
        except ValueError:
            return None

    # Caso 2: Buscar por campus_id o nombre
    query = """
    query buscarUsuario($value: string) {
      user_by_campus(func: eq(campus_id, $value)) {
        user_id
        user_name
        campus_id
      }

      user_by_name(func: eq(user_name, $value)) {
        user_id
        user_name
        campus_id
      }
    }
    """

    variables = {
        "$value": user_input
    }

    response = client.txn(read_only=True).query(query, variables=variables)
    data = json.loads(response.json)

    results = data.get("user_by_campus", []) + data.get("user_by_name", [])

    if not results:
        return None

    return results[0]["user_id"]


# =========================================================
# DGRAPH R1
# Usuarios que coinciden en eventos con un usuario
# =========================================================

def dgraph_r1_users_coinciden(client):

    print("\n===== DGRAPH R1 =====")
    print("Usuarios que coinciden en eventos con un usuario")

    user_input = input("Ingresa el usuario (ej. USER001, A001 o Diego Alvarez): ").strip()

    user_id = resolve_user_input(client, user_input)

    if user_id is None:
        print("No se encontró el usuario. Intenta con USER001, A001 o el nombre completo.")
        return

    query = """
    query usuariosCoinciden($user_id: int) {
      target_user(func: eq(user_id, $user_id)) {

        user_id
        user_name

        participates_in {

          event_id
          event_name

          ~participates_in {

            related_user_id: user_id
            related_user_name: user_name
          }
        }
      }
    }
    """

    variables = {
        "$user_id": str(user_id)
    }

    response = client.txn(read_only=True).query(query, variables=variables)
    data = json.loads(response.json)

    users_count = {}

    target_users = data.get("target_user", [])

    if not target_users:
        print("Usuario no encontrado.")
        return

    target_user = target_users[0]

    for event in ensure_list(target_user.get("participates_in", [])):

        for related_user in ensure_list(event.get("~participates_in", [])):

            related_id = related_user.get("related_user_id")
            related_name = related_user.get("related_user_name")

            if related_id == user_id:
                continue

            if related_id not in users_count:

                users_count[related_id] = {
                    "user_name": related_name,
                    "shared_events_count": 0
                }

            users_count[related_id]["shared_events_count"] += 1

    results = sorted(
        users_count.items(),
        key=lambda x: x[1]["shared_events_count"],
        reverse=True
    )

    print("\n===== PERSONAS CON LAS QUE HAS COINCIDIDO =====\n")

    if not results:
        print("No se encontraron coincidencias.")
        return

    for index, (related_id, info) in enumerate(results, start=1):

        formatted_id = f"USER{related_id:03d}"

        cantidad = info["shared_events_count"]
        evento_texto = "evento universitario" if cantidad == 1 else "eventos universitarios"

        print(f"{index}. {info['user_name']} ({formatted_id})")
        print(f"   Has compartido {cantidad} {evento_texto} con esta persona.")

# =========================================================
# DGRAPH R2
# Eventos en los que coinciden usuarios de distintos roles
# =========================================================

def dgraph_r2_eventos_con_distintos_roles(client):
    print("\n===== DGRAPH R2 =====")
    print("Eventos en los que coinciden usuarios de distintos roles")
    print("\nEsta consulta muestra eventos donde participaron personas con diferentes tipos de rol.")
    print("Ejemplo: estudiantes con docentes, invitados con administrativos, etc.\n")

    query = """
    {
      events(func: type(Event)) {
        event_id
        event_name
        event_type

        ~participates_in {
          user_id
          user_name

          has_role {
            role_type
          }
        }
      }
    }
    """

    response = client.txn(read_only=True).query(query)
    data = json.loads(response.json)

    events = data.get("events", [])

    if not events:
        print("No se encontraron eventos registrados.")
        return

    found_results = False

    print("\n===== EVENTOS CON PARTICIPANTES DE DISTINTOS ROLES =====\n")

    for event in events:
        role_counts = {}

        participants = ensure_list(event.get("~participates_in", []))

        for participant in participants:
            roles = ensure_list(participant.get("has_role", []))

            for role in roles:
                role_type = role.get("role_type")

                if not role_type:
                    continue

                if role_type not in role_counts:
                    role_counts[role_type] = 0

                role_counts[role_type] += 1

        # Solo nos interesan eventos con mínimo 2 roles diferentes
        if len(role_counts) < 2:
            continue

        found_results = True

        event_id = event.get("event_id")
        event_name = event.get("event_name")
        event_type = event.get("event_type")

        formatted_event_id = f"EVT{event_id:03d}"

        print("--------------------------------------------------")
        print(f"Evento: {event_name} ({formatted_event_id})")
        print(f"Tipo de evento: {event_type}")
        print("\nRoles que coincidieron en este evento:")

        for role_type, count in role_counts.items():
            participante_texto = "participante" if count == 1 else "participantes"
            print(f"- {role_type}: {count} {participante_texto}")

        print("\nResumen:")
        print(
            f"En este evento coincidieron {len(role_counts)} tipos de usuarios diferentes."
        )
        print("--------------------------------------------------\n")

    if not found_results:
        print("No se encontraron eventos donde coincidan usuarios de distintos roles.")

# =========================================================
# DGRAPH R3
# Usuarios vinculados a eventos organizados por cierta área
# =========================================================

def dgraph_r3_usuarios_por_area_organizadora(client):
    print("\n===== DGRAPH R3 =====")
    print("Usuarios vinculados a eventos organizados por cierta área")
    print("\nEsta consulta muestra participantes de eventos organizados por un departamento específico.")
    print("Ejemplos de departamento: Ingenieria, Cultura, Deportes, Bienestar, Negocios\n")

    department = input("Ingresa el departamento o área organizadora: ").strip()

    if not department:
        print("Debes ingresar un departamento válido.")
        return

    query = """
    query usuariosPorArea($department: string) {
      organizers(func: eq(department, $department)) {
        organizer_id
        organizer_name
        department

        ~organized_by {
          event_id
          event_name
          event_type

          ~participates_in {
            user_id
            user_name
          }
        }
      }
    }
    """

    variables = {
        "$department": department
    }

    response = client.txn(read_only=True).query(query, variables=variables)
    data = json.loads(response.json)

    organizers = data.get("organizers", [])

    if not organizers:
        print(f"No se encontraron organizadores para el departamento: {department}")
        return

    found_results = False

    print("\n===== USUARIOS VINCULADOS A EVENTOS DEL ÁREA =====\n")

    for organizer in organizers:
        organizer_id = organizer.get("organizer_id")
        organizer_name = organizer.get("organizer_name")
        organizer_department = organizer.get("department")

        formatted_organizer_id = f"ORG{organizer_id:03d}"

        print("==================================================")
        print(f"Área organizadora: {organizer_name} ({formatted_organizer_id})")
        print(f"Departamento: {organizer_department}")
        print("==================================================")

        events = ensure_list(organizer.get("~organized_by", []))

        if not events:
            print("No hay eventos asociados a esta área.\n")
            continue

        for event in events:
            participants = ensure_list(event.get("~participates_in", []))

            if not participants:
                continue

            found_results = True

            formatted_event_id = f"EVT{event.get('event_id'):03d}"

            print(f"\nEvento: {event.get('event_name')} ({formatted_event_id})")
            print(f"Tipo de evento: {event.get('event_type')}")
            print(f"Total de participantes encontrados: {len(participants)}")
            print("Participantes vinculados:")

            for participant in participants:
                formatted_user_id = f"USER{participant.get('user_id'):03d}"
                print(f"- {participant.get('user_name')} ({formatted_user_id})")

        print()

    if not found_results:
        print("No se encontraron participantes asociados a eventos de esta área.")

# =========================================================
# DGRAPH R4
# Participación de usuarios externos en eventos universitarios
# =========================================================

def dgraph_r4_participacion_usuarios_externos(client):
    print("\n===== DGRAPH R4 =====")
    print("Participación de usuarios externos en eventos universitarios")
    print("\nEsta consulta muestra eventos donde participaron usuarios externos o invitados.\n")

    query = """
    {
    external_users(func: eq(role_type, "invitado")) {
        role_type
        role_scope

        ~has_role {
        user_id
        user_name
        campus_id

        participates_in {
            event_id
            event_name
            event_type
        }
        }
    }
    }
    """

    response = client.txn(read_only=True).query(query)
    data = json.loads(response.json)

    roles = data.get("external_users", [])

    if not roles:
        print("No se encontraron roles externos registrados.")
        return

    events_map = {}

    for role in roles:
        users = ensure_list(role.get("~has_role", []))

        for user in users:
            user_id = user.get("user_id")
            user_name = user.get("user_name")
            campus_id = user.get("campus_id")

            events = ensure_list(user.get("participates_in", []))

            for event in events:
                event_id = event.get("event_id")
                event_name = event.get("event_name")
                event_type = event.get("event_type")

                if event_id not in events_map:
                    events_map[event_id] = {
                        "event_id": event_id,
                        "event_name": event_name,
                        "event_type": event_type,
                        "external_users": []
                    }

                events_map[event_id]["external_users"].append({
                    "user_id": user_id,
                    "user_name": user_name,
                    "campus_id": campus_id
                })

    if not events_map:
        print("No se encontraron eventos con participación de usuarios externos.")
        return

    print("\n===== EVENTOS CON PARTICIPACIÓN EXTERNA =====\n")

    for event in events_map.values():
        formatted_event_id = f"EVT{event['event_id']:03d}"

        print("--------------------------------------------------")
        print(f"Evento: {event['event_name']} ({formatted_event_id})")
        print(f"Tipo de evento: {event['event_type']}")
        print(f"Total de usuarios externos: {len(event['external_users'])}")
        print("\nUsuarios externos participantes:")

        for user in event["external_users"]:
            formatted_user_id = f"USER{user['user_id']:03d}"
            print(
                f"- {user['user_name']} ({formatted_user_id}) "
                f"| Código externo: {user['campus_id']}"
            )

        print("--------------------------------------------------\n")


# =========================================================
# DGRAPH R5
# Espacios usados por usuarios según tipo de evento
# =========================================================

def dgraph_r5_espacios_por_usuario_y_tipo_evento(client):
    print("\n===== DGRAPH R5 =====")
    print("Espacios usados por usuarios según tipo de evento")
    print("\nEsta consulta muestra qué espacios ha utilizado un usuario según los eventos en los que participa.")
    print("Puedes buscar por nombre, código institucional o código interno.")
    print("Ejemplos válidos: Diego Alvarez, A001, USER001\n")

    user_input = input("Ingresa el usuario: ").strip()

    user_id = resolve_user_input(client, user_input)

    if user_id is None:
        print("No se encontró el usuario. Intenta con USER001, A001 o el nombre completo.")
        return

    query = """
    query espaciosPorUsuario($user_id: int) {
      user(func: eq(user_id, $user_id)) {
        user_id
        user_name
        campus_id

        participates_in {
          event_id
          event_name
          event_type

          takes_place_in {
            space_id
            space_name
            space_type
            capacity
          }
        }
      }
    }
    """

    variables = {
        "$user_id": str(user_id)
    }

    response = client.txn(read_only=True).query(query, variables=variables)
    data = json.loads(response.json)

    users = data.get("user", [])

    if not users:
        print("No se encontró información del usuario.")
        return

    user = users[0]
    user_name = user.get("user_name")
    campus_id = user.get("campus_id")

    events = ensure_list(user.get("participates_in", []))

    if not events:
        print(f"{user_name} no tiene eventos registrados.")
        return

    print("\n===== ESPACIOS USADOS SEGÚN TIPO DE EVENTO =====\n")
    print(f"Usuario: {user_name}")
    print(f"Código institucional: {campus_id}")
    print(f"Total de eventos encontrados: {len(events)}\n")

    grouped_by_type = {}

    for event in events:
        event_type = event.get("event_type", "Sin tipo")

        if event_type not in grouped_by_type:
            grouped_by_type[event_type] = []

        spaces = ensure_list(event.get("takes_place_in", []))

        for space in spaces:
            grouped_by_type[event_type].append({
                "event_id": event.get("event_id"),
                "event_name": event.get("event_name"),
                "space_id": space.get("space_id"),
                "space_name": space.get("space_name"),
                "space_type": space.get("space_type"),
                "capacity": space.get("capacity")
            })

    for event_type, records in grouped_by_type.items():
        print("--------------------------------------------------")
        print(f"Tipo de evento: {event_type}")
        print(f"Espacios relacionados: {len(records)}\n")

        for record in records:
            formatted_event_id = f"EVT{record['event_id']:03d}"
            formatted_space_id = f"SPC{record['space_id']:03d}"

            print(f"- Evento: {record['event_name']} ({formatted_event_id})")
            print(
                f"  Espacio utilizado: {record['space_name']} ({formatted_space_id})"
            )
            print(f"  Tipo de espacio: {record['space_type']}")
            print(f"  Capacidad: {record['capacity']} personas\n")

    print("Consulta finalizada.")


# =========================================================
# DGRAPH R6
# Organizadores relacionados con tipos de usuarios participantes
# =========================================================

def dgraph_r6_organizadores_por_tipo_usuario(client):
    print("\n===== DGRAPH R6 =====")
    print("Organizadores relacionados con tipos de usuarios participantes")
    print("\nEsta consulta muestra qué tipos de usuarios participan en eventos de cada organizador.")
    print("Roles posibles: estudiante, docente, administrativo, invitado")
    print("Puedes dejar vacío el filtro para mostrar todos los roles.\n")

    role_filter = input("Filtrar por tipo de rol (opcional): ").strip().lower()

    query = """
    {
      organizers(func: type(Organizer)) {
        organizer_id
        organizer_name
        department

        ~organized_by {
          event_id
          event_name

          ~participates_in {
            user_id
            user_name

            has_role {
              role_type
            }
          }
        }
      }
    }
    """

    response = client.txn(read_only=True).query(query)
    data = json.loads(response.json)

    organizers = data.get("organizers", [])

    if not organizers:
        print("No se encontraron organizadores registrados.")
        return

    print("\n===== ORGANIZADORES Y TIPOS DE USUARIOS PARTICIPANTES =====\n")

    found_results = False

    for organizer in organizers:
        organizer_id = organizer.get("organizer_id")
        organizer_name = organizer.get("organizer_name")
        department = organizer.get("department")

        events = ensure_list(organizer.get("~organized_by", []))

        role_stats = {}

        for event in events:
            participants = ensure_list(event.get("~participates_in", []))

            for participant in participants:
                roles = ensure_list(participant.get("has_role", []))

                for role in roles:
                    role_type = role.get("role_type")

                    if not role_type:
                        continue

                    role_type_normalized = role_type.lower()

                    if role_filter and role_type_normalized != role_filter:
                        continue

                    if role_type not in role_stats:
                        role_stats[role_type] = {
                            "event_ids": set(),
                            "participant_ids": set()
                        }

                    role_stats[role_type]["event_ids"].add(event.get("event_id"))
                    role_stats[role_type]["participant_ids"].add(participant.get("user_id"))

        if not role_stats:
            continue

        found_results = True

        formatted_organizer_id = f"ORG{organizer_id:03d}"

        print("--------------------------------------------------")
        print(f"Organizador: {organizer_name} ({formatted_organizer_id})")
        print(f"Departamento: {department}")
        print("\nTipos de usuarios relacionados:")

        for role_type, stats in role_stats.items():
            event_count = len(stats["event_ids"])
            participant_count = len(stats["participant_ids"])

            evento_texto = "evento" if event_count == 1 else "eventos"
            participante_texto = "participante" if participant_count == 1 else "participantes"

            print(
                f"- {role_type}: presente en {event_count} {evento_texto}, "
                f"con {participant_count} {participante_texto} únicos."
            )

        print("--------------------------------------------------\n")

    if not found_results:
        if role_filter:
            print(f"No se encontraron organizadores relacionados con el rol: {role_filter}")
        else:
            print("No se encontraron relaciones entre organizadores y tipos de usuarios.")

# =========================================================
# DGRAPH R7
# Usuarios vinculados por un mismo evento o espacio
# =========================================================

def dgraph_r7_usuarios_vinculados_evento_o_espacio(client):
    print("\n===== DGRAPH R7 =====")
    print("Usuarios vinculados por un mismo evento o espacio")
    print("\nEsta consulta muestra personas relacionadas contigo por haber compartido eventos o espacios.")
    print("Puedes buscar por nombre, código institucional o código interno.")
    print("Ejemplos válidos: Diego Alvarez, A001, USER001\n")

    user_input = input("Ingresa el usuario: ").strip()

    user_id = resolve_user_input(client, user_input)

    if user_id is None:
        print("No se encontró el usuario. Intenta con USER001, A001 o el nombre completo.")
        return

    query = """
    query usuariosRelacionados($user_id: int) {
      user(func: eq(user_id, $user_id)) {
        user_id
        user_name
        campus_id

        participates_in {
          event_id
          event_name

          ~participates_in {
            related_user_id: user_id
            related_user_name: user_name
          }
        }

        uses_space {
          space_id
          space_name

          ~uses_space {
            related_user_id: user_id
            related_user_name: user_name
          }
        }
      }
    }
    """

    variables = {
        "$user_id": str(user_id)
    }

    response = client.txn(read_only=True).query(query, variables=variables)
    data = json.loads(response.json)

    users = data.get("user", [])

    if not users:
        print("No se encontró información del usuario.")
        return

    user = users[0]
    user_name = user.get("user_name")
    campus_id = user.get("campus_id")

    related_users = {}

    # Relación por eventos compartidos
    for event in ensure_list(user.get("participates_in", [])):
        event_name = event.get("event_name")
        event_id = event.get("event_id")

        for related_user in ensure_list(event.get("~participates_in", [])):
            related_id = related_user.get("related_user_id")
            related_name = related_user.get("related_user_name")

            if related_id == user_id:
                continue

            if related_id not in related_users:
                related_users[related_id] = {
                    "user_name": related_name,
                    "shared_events": set(),
                    "shared_spaces": set()
                }

            related_users[related_id]["shared_events"].add(
                f"{event_name} (EVT{event_id:03d})"
            )

    # Relación por espacios compartidos
    for space in ensure_list(user.get("uses_space", [])):
        space_name = space.get("space_name")
        space_id = space.get("space_id")

        for related_user in ensure_list(space.get("~uses_space", [])):
            related_id = related_user.get("related_user_id")
            related_name = related_user.get("related_user_name")

            if related_id == user_id:
                continue

            if related_id not in related_users:
                related_users[related_id] = {
                    "user_name": related_name,
                    "shared_events": set(),
                    "shared_spaces": set()
                }

            related_users[related_id]["shared_spaces"].add(
                f"{space_name} (SPC{space_id:03d})"
            )

    if not related_users:
        print(f"No se encontraron usuarios relacionados con {user_name}.")
        return

    sorted_related = sorted(
        related_users.items(),
        key=lambda item: (
            len(item[1]["shared_events"]) + len(item[1]["shared_spaces"])
        ),
        reverse=True
    )

    print("\n===== USUARIOS RELACIONADOS POR EVENTOS O ESPACIOS =====\n")
    print(f"Usuario base: {user_name}")
    print(f"Código institucional: {campus_id}")
    print(f"Usuarios relacionados encontrados: {len(sorted_related)}\n")

    event_relations = sum(
        1 for info in related_users.values()
        if len(info["shared_events"]) > 0
    )

    space_relations = sum(
        1 for info in related_users.values()
        if len(info["shared_spaces"]) > 0
    )

    print(f"Relaciones por eventos: {event_relations}")
    print(f"Relaciones por espacios: {space_relations}\n")

    for index, (related_id, info) in enumerate(sorted_related, start=1):
        formatted_related_id = f"USER{related_id:03d}"

        shared_events = sorted(info["shared_events"])
        shared_spaces = sorted(info["shared_spaces"])

        print("--------------------------------------------------")
        print(f"{index}. {info['user_name']} ({formatted_related_id})")

        if shared_events:
            print(f"Eventos compartidos ({len(shared_events)}):")
            for event in shared_events[:5]:
                print(f"  - {event}")

        if shared_spaces:
            print(f"Espacios compartidos ({len(shared_spaces)}):")
            for space in shared_spaces[:5]:
                print(f"  - {space}")

        if shared_events and shared_spaces:
            print("Relación detectada: coincidencia por evento y espacio.")
        elif shared_events:
            print("Relación detectada: coincidencia por evento.")
        elif shared_spaces:
            print("Relación detectada: coincidencia por espacio.")

        print("--------------------------------------------------\n")

    print("Consulta finalizada.")  


# =========================================================
# DGRAPH R8
# Tipos de eventos que conectan más usuarios
# =========================================================

def dgraph_r8_tipos_eventos_conectan_usuarios(client):
    print("\n===== DGRAPH R8 =====")
    print("Tipos de eventos que conectan más usuarios")
    print("\nEsta consulta analiza qué tipos de eventos generan más conexiones entre participantes.\n")

    query = """
    {
      events(func: type(Event)) {
        event_id
        event_name
        event_type

        ~participates_in {
          user_id
          user_name
        }
      }
    }
    """

    response = client.txn(read_only=True).query(query)
    data = json.loads(response.json)

    events = data.get("events", [])

    if not events:
        print("No se encontraron eventos registrados.")
        return

    event_type_stats = {}

    for event in events:
        event_type = event.get("event_type", "Sin tipo")
        participants = ensure_list(event.get("~participates_in", []))

        participant_ids = {
            participant.get("user_id")
            for participant in participants
            if participant.get("user_id") is not None
        }

        participant_count = len(participant_ids)

        # Fórmula de conexiones posibles entre usuarios:
        # n * (n - 1) / 2
        shared_participation_count = (
            participant_count * (participant_count - 1)
        ) // 2

        if event_type not in event_type_stats:
            event_type_stats[event_type] = {
                "connected_users": set(),
                "shared_participation_count": 0,
                "events_count": 0
            }

        event_type_stats[event_type]["connected_users"].update(participant_ids)
        event_type_stats[event_type]["shared_participation_count"] += shared_participation_count
        event_type_stats[event_type]["events_count"] += 1

    results = []

    for event_type, stats in event_type_stats.items():
        results.append({
            "event_type": event_type,
            "connected_users_count": len(stats["connected_users"]),
            "shared_participation_count": stats["shared_participation_count"],
            "events_count": stats["events_count"]
        })

    results = sorted(
        results,
        key=lambda x: x["shared_participation_count"],
        reverse=True
    )

    print("\n===== TIPOS DE EVENTO CON MAYOR CONEXIÓN ENTRE USUARIOS =====\n")

    for index, result in enumerate(results, start=1):
        tipo_evento = result["event_type"]
        connected_users_count = result["connected_users_count"]
        shared_participation_count = result["shared_participation_count"]
        events_count = result["events_count"]

        print("--------------------------------------------------")
        print(f"{index}. Tipo de evento: {tipo_evento}")
        print(f"Eventos analizados: {events_count}")
        print(f"Usuarios conectados: {connected_users_count}")
        print(f"Conexiones generadas entre participantes: {shared_participation_count}")

        if index == 1:
            print("Este es el tipo de evento que más conecta usuarios en la plataforma.")

        print("--------------------------------------------------\n")

    print("Consulta finalizada.")