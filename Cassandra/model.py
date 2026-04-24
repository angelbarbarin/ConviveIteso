import logging

log = logging.getLogger(__name__)

CREATE_KEYSPACE = """
CREATE KEYSPACE IF NOT EXISTS convive_iteso
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
"""

CREATE_ATTENDANCE_BY_USER = """
CREATE TABLE IF NOT EXISTS attendance_by_user (
    userid TEXT,
    attendancetimestamp TIMESTAMP,
    eventid TEXT,
    eventname TEXT,
    eventtype TEXT,
    attendancestatus TEXT,
    PRIMARY KEY ((userid), attendancetimestamp)
) WITH CLUSTERING ORDER BY (attendancetimestamp DESC)
"""

CREATE_RESERVATIONS_BY_USER = """
CREATE TABLE IF NOT EXISTS reservations_by_user (
    userid TEXT,
    reservationtimestamp TIMESTAMP,
    reservationid TEXT,
    spaceid TEXT,
    spacename TEXT,
    spacetype TEXT,
    reservationtype TEXT,
    reservationstatus TEXT,
    PRIMARY KEY ((userid), reservationtimestamp)
) WITH CLUSTERING ORDER BY (reservationtimestamp DESC)
"""

CREATE_USAGE_BY_SPACE_DATE = """
CREATE TABLE IF NOT EXISTS usage_by_space_date (
    spaceid TEXT,
    usagedate DATE,
    usagetimestamp TIMESTAMP,
    userid TEXT,
    spacename TEXT,
    activitytype TEXT,
    relatedeventid TEXT,
    status TEXT,
    PRIMARY KEY ((spaceid, usagedate), usagetimestamp)
) WITH CLUSTERING ORDER BY (usagetimestamp DESC)
"""

def create_keyspace(session):
    log.info("Creating keyspace convive_iteso")
    session.execute(CREATE_KEYSPACE)

def create_schema(session):
    log.info("Creating Cassandra schema for Convive ITESO")
    session.execute(CREATE_ATTENDANCE_BY_USER)
    session.execute(CREATE_RESERVATIONS_BY_USER)
    session.execute(CREATE_USAGE_BY_SPACE_DATE)
