from connect import get_dgraph_client
from Queries.dgraph_queries import dgraph_r2_eventos_con_distintos_roles

client = get_dgraph_client()

dgraph_r2_eventos_con_distintos_roles(client)