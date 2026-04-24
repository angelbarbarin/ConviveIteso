from pymongo import MongoClient
from cassandra.cluster import Cluster
import pydgraph


def connect_mongo(uri="mongodb://localhost:27017/", db_name="convive_iteso"):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print("[OK] Conexión a MongoDB establecida")
        return db
    except Exception as e:
        print(f"[ERROR] MongoDB: {e}")
        return None


def connect_cassandra(hosts=None, keyspace="convive_iteso"):
    try:
        if hosts is None:
            hosts = ["127.0.0.1"]
        cluster = Cluster(hosts)
        session = cluster.connect()
        session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
        """)
        session.set_keyspace(keyspace)
        print("[OK] Conexión a Cassandra establecida")
        return session
    except Exception as e:
        print(f"[ERROR] Cassandra: {e}")
        return None


def connect_dgraph(host="localhost", port=9080):
    try:
        stub = pydgraph.DgraphClientStub(f"{host}:{port}")
        client = pydgraph.DgraphClient(stub)
        print("[OK] Conexión a Dgraph establecida")
        return client
    except Exception as e:
        print(f"[ERROR] Dgraph: {e}")
        return None