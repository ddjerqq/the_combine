import sqlite3
import pandas as pd

# Used To create Training DB with required columns
# Tables must have the following schema: [name, attribute_type, attribute_value]
tables = ['asuna', 'hape']
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

# Creates a df with the union of all tables
df = pd.DataFrame(execute_query(make_union_select(tables), db), columns=["name", "number", "attribute_type", "attribute_value"])

# df with all the column distinct variables
distinct_df = df['attribute_type'].drop_duplicates()
# print(distinct_df.describe())

# Make sure that every item has a value for every distinct variable
name_number_df = df[['name', 'number']].drop_duplicates()

# Creates df, making sure every item all the distinct attribute types
joined_df = name_number_df.merge(distinct_df, how='cross')
training_df = joined_df.merge(df, how='left', on=['name', 'number', 'attribute_type'])

# create Dataframe for training data
training_df["attributes"] = list(zip(training_df['attribute_type'], training_df['attribute_value']))
training_df.drop(columns=['attribute_type', 'attribute_value'], inplace=True)
training_df = training_df.groupby(['name', 'number']).agg(lambda x: dict(list(x))).reset_index()

# Generates excel file, with the training data for later data analysis
training_df.to_excel('training_db.xlsx')