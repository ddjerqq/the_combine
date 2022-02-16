import sqlite3

# function for executing sql query
def execute_query(query, db):
    connection = sqlite3.connect(db, check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()

query = "SELECT * FROM asuna"