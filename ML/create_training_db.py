import sqlite3
import pandas as pd
import numpy as np

# Used To create Training DB with required columns

# Tables must have the following schema: [name, attribute_type, attribute_value]
tables = ['asuna', 'hape', 'zipcy']
db = 'nft.db'

# function for executing sql query
def execute_query(query, db):
    connection = sqlite3.connect(db, check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()


# Makes Unioned select of all tables, with required columns
def make_union_select(tables):
    union_select = ''
    for table in tables:
        union_select += f"SELECT SUBSTR(name, 0, INSTR(name, '#')-1) AS name, CAST(SUBSTR(name, INSTR(name, '#')+1) AS INTEGER) AS number, attribute_type, attribute_value FROM {table} UNION "
    return union_select[:-7]+' ORDER BY name, number'

df = pd.DataFrame(execute_query(make_union_select(tables), db), columns=["name", "number", "attribute_type", "attribute_value"])
df['attributes'] = df["attribute_type"].astype(str) + ":" + df["attribute_value"].astype(str)
df.drop(columns=['attribute_type', 'attribute_value'], inplace=True)

df = df.groupby(['name', 'number']).agg(lambda x: x.tolist()).reset_index()


df.to_excel('training_db.xlsx')
