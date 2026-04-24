import logging
import pydgraph

log = logging.getLogger()

SCHEMA = """
user_id: int @index(int) .
user_name: string @index(term) .
email: string @index(exact) .

role_id: int @index(int) .
role_name: string @index(term) .

event_id: int @index(int) .
event_name: string @index(term) .
event_type: string @index(term) .

space_id: int @index(int) .
space_name: string @index(term) .
space_type: string @index(term) .

organizer_id: int @index(int) .
organizer_name: string @index(term) .

has_role: uid @reverse .
participates_in: [uid] @reverse .
uses_space: [uid] @reverse .
organized_by: uid @reverse .

type User {
    user_id
    user_name
    email
    has_role
    participates_in
    uses_space
}

type Role {
    role_id
    role_name
}

type Event {
    event_id
    event_name
    event_type
    organized_by
}

type Space {
    space_id
    space_name
    space_type
}

type Organizer {
    organizer_id
    organizer_name
}
"""

def create_schema(client):
    log.info("Creating Dgraph schema for Convive ITESO")
    client.alter(pydgraph.Operation(schema=SCHEMA))
