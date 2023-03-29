# import psycopg2
# import csv

# conn = psycopg2.connect(
#     host='localhost',
#     port=54320,
#     dbname='my_database',
#     user='postgres',
#     password='decent_password',
# )

# cusor = conn.cursor()


# # store status

from sqlalchemy import create_engine
from tqdm import tqdm
import pandas as pd
engine = create_engine('postgresql+psycopg2://postgres:decent_password@localhost:54320/loop_db')
chunksize = 10**6

cnt = 0
for chunk in pd.read_csv('csvs/Menu hours.csv', chunksize=chunksize):
    # print(chunk.head())
    chunk['id'] = chunk.index

    # print(chunk.head())
    # cnt += 1
    # print(cnt)
    # if cnt == 2:
    #     break
    chunk.to_sql('store_hours', engine, if_exists='append', index=False)

for chunk in tqdm(pd.read_csv('csvs/store status.csv', chunksize=chunksize)):
    chunk['id'] = chunk.index
    chunk.to_sql('store_status', engine, if_exists='append', index=False)

for chunk in tqdm(pd.read_csv('csvs/store_timezones.csv', chunksize=chunksize)):
    chunk['id'] = chunk.index
    chunk.to_sql('store_timezones', engine, if_exists='append', index=False)
