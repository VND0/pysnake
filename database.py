import sqlite3 as sql


def get_connections(filename: str):
    while True:
        with sql.connect(filename) as conn:
            yield conn


def init_db(conn: sql.Connection) -> None:
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY_KEY AUTO_INCREMENT,
        last_score INTEGER DEFAULT 0 NOT NULL,
        best_score INTEGER DEFAULT 0 NOT NULL
    );
    """
    cursor.execute(query)

    # Если в базе ничего нет, добавить строчку
    query = """SELECT id FROM stats LIMIT 1;"""
    result = cursor.execute(query).fetchall()
    if not result:
        query = """
        INSERT INTO stats DEFAULT VALUES;"""
        cursor.execute(query)
    conn.commit()


def get_last_score(conn: sql.Connection) -> int:
    query = """SELECT last_score FROM stats;"""
    cursor = conn.cursor()
    result = cursor.execute(query).fetchone()[0]
    return result


def set_last_score(conn: sql.Connection, score: int) -> None:
    query = """UPDATE stats SET last_score = ?;"""
    cursor = conn.cursor()
    cursor.execute(query, (score,))
    conn.commit()


def get_best_score(conn: sql.Connection) -> int:
    query = """SELECT best_score FROM stats;"""
    cursor = conn.cursor()
    result = cursor.execute(query).fetchone()[0]
    return result


def set_best_score(conn: sql.Connection, score: int) -> None:
    query = """UPDATE stats SET best_score = ?;"""
    cursor = conn.cursor()
    cursor.execute(query, (score,))
    conn.commit()
