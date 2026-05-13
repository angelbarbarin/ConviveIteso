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
# Usuarios vinculados a eventos por área
# =========================================================

# TODO


# =========================================================
# DGRAPH R4
# Participación de usuarios externos
# =========================================================

# TODO


# =========================================================
# DGRAPH R5
# Espacios usados por usuarios según tipo de evento
# =========================================================

# TODO


# =========================================================
# DGRAPH R6
# Organizadores relacionados con tipos de usuarios
# =========================================================

# TODO


# =========================================================
# DGRAPH R7
# Usuarios vinculados por mismo evento o espacio
# =========================================================

# TODO


# =========================================================
# DGRAPH R8
# Tipos de eventos que conectan más usuarios
# =========================================================

# TODO