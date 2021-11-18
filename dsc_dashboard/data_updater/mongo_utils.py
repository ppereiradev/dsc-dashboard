import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient
import os
from datetime import datetime

def _db_connection():
    client = MongoClient("mongodb://" + os.getenv("MONGODB_HOST")   + ":" + os.getenv('MONGODB_PORT') + "/",
                            username=os.getenv('MONGODB_USER'),
                            password=os.getenv('MONGODB_PASSWORD'), authSource='admin', authMechanism='SCRAM-SHA-256')
    db = client[os.getenv('MONGODB_DB')]
    return db
    

def _timestamp_datetime(df_dict):
    for i in range(len(df_dict)):
        df_dict[i]['created_at'] = datetime.strptime(str(df_dict[i]['created_at']), "%Y-%m-%d %H:%M:%S.%f") \
            if df_dict[i]['created_at'] != 'null' else 'null'

        df_dict[i]['close_at'] = datetime.strptime(str(df_dict[i]['close_at']), "%Y-%m-%d %H:%M:%S.%f") \
            if df_dict[i]['close_at'] != 'null' else 'null'

        df_dict[i]['updated_at'] = datetime.strptime(str(df_dict[i]['updated_at']), "%Y-%m-%d %H:%M:%S.%f") \
            if df_dict[i]['updated_at'] != 'null' else 'null'
    
    return df_dict

def save_data_tickets(df):
    db = _db_connection()
    my_collection = db['tickets']

    # comparando os tickets do banco com os tickets do zammad
    # se o tickets já estiver no banco, ele não será inserido novamente
    df = df[df['number'].notna()]
    numbers = df['number'].tolist()
    df_banco = get_many_tickets({"number": {"$in": numbers}})

    if df_banco.empty:
        print("Inserindo tickets...")
        df.reset_index(inplace=True)
        data_dict = df.to_dict("records")
        my_collection.insert_many(data_dict)
        print("Finalizado...")
        return

    common = df.merge(df_banco, how = 'inner', on=["number"])
    common = common[['created_at_x', 'close_at_x', 'updated_at_x', 'create_article_type_x', 'state_x', 'id_x', 'number', 'group_x']]
    common.columns = ['created_at', 'close_at', 'updated_at', 'create_article_type', 'state', 'id', 'number', 'group']

    df_result = pd.concat([df,common]).drop_duplicates(keep=False)

    if not common.empty:
        print("Atualizando registros dos tickets...")

        common.reset_index(drop=True, inplace=True)
        df_common_data_dict = common.to_dict("records")
        df_common_data_dict = _timestamp_datetime(df_common_data_dict)

        for i in range(0,len(df_common_data_dict)):
            my_collection.replace_one({"number": common['number'][i]},df_common_data_dict[i])
            
    if not df_result.empty:
        print("Inserindo novos tickets...")
        df_result.reset_index(drop=True, inplace=True)
        data_dict = df_result.to_dict("records")
        
        data_dict = _timestamp_datetime(data_dict)
        my_collection.insert_many(data_dict)
    else:
        print("Nenhum novo ticket!")

    print('Finalizado atualização do MongoDB...')


def get_many_tickets(query=None):
    db = _db_connection()
    my_collection = db['tickets']
    
    if query is None:
        data_from_db = my_collection.find()
    else:
        data_from_db = my_collection.find(query)
    
    df = pd.DataFrame(data_from_db)
    
    return df
