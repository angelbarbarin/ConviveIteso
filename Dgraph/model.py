import pydgraph

DGRAPH_SCHEMA = """
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
  role_name
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

user_id: int @index(int) .
user_name: string @index(term) .
email: string @index(hash) .
status: string .
campus_id: string .

role_id: int @index(int) .
role_name: string @index(hash) .
role_scope: string .

event_id: int @index(int) .
event_name: string @index(term) .
event_type: string @index(hash) .
event_date: datetime @index(hour) .
event_status: string .

organizer_id: int @index(int) .
organizer_name: string @index(term) .
department: string @index(hash) .

space_id: int @index(int) .
space_name: string @index(term) .
space_type: string @index(hash) .
capacity: int .
location: geo .

has_role: uid @reverse .
participates_in: uid @reverse .
organized_by: uid @reverse .
takes_place_in: uid @reverse .
uses_space: uid @reverse .
"""


def create_schema(client):
    op = client.alter(pydgraph.Operation(schema=DGRAPH_SCHEMA))
    print("[OK] Esquema de Dgraph creado")