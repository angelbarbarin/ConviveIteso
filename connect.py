from pymongo import MongoClient
from cassandra.cluster import Cluster

def connect_mongo(uri="mongodb://localhost:27017/", db_name="convive_iteso"):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print("MongoDB conectado")
        return db
    except Exception as e:
        print(f"Error conectando a MongoDB: {e}")
        return None

def connect_cassandra(hosts=None, keyspace="convive_iteso"):
    if hosts is None:
        hosts = ["127.0.0.1"]
    try:
        cluster = Cluster(hosts)
        session = cluster.connect()
        session.set_keyspace(keyspace)
        print("Cassandra conectado")
        return session
    except Exception as e:
        print(f"Error conectando a Cassandra: {e}")
        return None

def connect_dgraph():
    print("Conexión a Dgraph pendiente de implementar")
    return None