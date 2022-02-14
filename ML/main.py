import tensorflow as tf
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from collections import Counter

db = "nft.db"
table = "training_db"

def execute_query(query, db):
    connection = sqlite3.connect("nft.db", check_same_thread = False)
    cursor = connection.cursor()
    cursor.execute(query)

    data = cursor.fetchall()

    return data


# Get all Distinct Values in DF
query = f"SELECT DISTINCT(attribute_type) FROM {table}"
distinct_attributes = [x[0] for x in execute_query(query, db)]
distinct_tensor = tf.Variable(distinct_attributes, tf.string)

Get xk of Data, for training Data,
data_k = 100000
query = f"SELECT name as Name, attribute_type as Attribute, attribute_value as AttributeValue FROM {table} ORDER BY name, attribute_type, attribute_value limit {data_k}"
top_k_training = pd.DataFrame(execute_query(query, db), columns=['Name', 'Attribute', 'AttributeValue'])

query = f"SELECT attribute_type, COUNT(attribute_type) AS count FROM {table} GROUP BY attribute_type ORDER BY count ASC"
attributes_w_count = pd.DataFrame(execute_query(query, db), columns=["Attribute","Count"])

#print(top_k_training.head())
#print(top_k_training.describe())


#print(attributes_w_count['Count'])


# Just bar chart stuff
plt.bar(range(10), attributes_w_count['Count'][:10])
plt.title("Bar Chart Of Attributes")
plt.xticks(range(10), attributes_w_count['Attribute'][:10])
plt.show()

