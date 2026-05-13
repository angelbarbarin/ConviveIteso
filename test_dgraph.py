from connect import get_dgraph_client
from Queries.dgraph_queries import *

client = get_dgraph_client()

dgraph_r1_users_coinciden(client)