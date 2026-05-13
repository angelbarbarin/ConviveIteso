from pymongo import MongoClient
from cassandra.cluster import Cluster
import pydgraph


# =========================
# MONGODB
# =========================

def get_mongo_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["conviveiteso"]
    return db


# =========================
# CASSANDRA
# =========================

def get_cassandra_session():
    cluster = Cluster(["127.0.0.1"])
    session = cluster.connect()
    return session


# =========================
# DGRAPH
# =========================

def get_dgraph_client():
    stub = pydgraph.DgraphClientStub("localhost:9080")
    client = pydgraph.DgraphClient(stub)
    return client