import pandas as pd
import shlex
import subprocess
import json
import os
from datetime import datetime

from .mongo_utils import save_data_tickets

def all_tickets():
    df = pd.DataFrame()
    page = 1

    print('FETCHING TICKET DATA FROM ZAMMAD...')
    while True:
        
        cmd =  "curl -u " + os.getenv("ZAMMAD_EMAIL") + ":" + os.getenv("ZAMMAD_PASSWORD") + " " + os.getenv("ZAMMAD_HOST") + "/api/v1/tickets?expand=true&page=" + str(page) + "&per_page=100"

        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        process.wait()

        df_aux = pd.DataFrame(json.loads(stdout.decode()))

        if len(df_aux.columns) > 52:
            df_aux.drop(columns=df_aux.columns[-1], axis=1, inplace=True)

        
        if df_aux.empty:    
            break

        df = df.append(df_aux, ignore_index=True)

        print("[GETTING PAGE: " + str(page) + "]")
        page += 1
    
    print('ENDED FETCHING TICKET DATA FROM ZAMMAD...')

    df = df[['created_at', 'close_at', 'updated_at', 'create_article_type', 'state', 'id', 'number', 'group']]

    for i in range(0, len(df['created_at'])):
        if df.at[i, 'created_at'] is not None:
            df.at[i, 'created_at'] = datetime.strptime(df.at[i, 'created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        elif df.at[i, 'created_at'] is None:
            df.at[i, 'created_at'] = "null"
            
        if df.at[i, 'close_at'] is not None:
            df.at[i, 'close_at'] = datetime.strptime(df.at[i, 'close_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        elif df.at[i, 'close_at'] is None:
            df.at[i, 'close_at'] = "null"

        if df.at[i, 'updated_at'] is not None:
            df.at[i, 'updated_at'] = datetime.strptime(df.at[i, 'updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        elif df.at[i, 'updated_at'] is None:
            df.at[i, 'updated_at'] = "null"

    save_data_tickets(df)


def interval_tickets(dias=120):
    
    df = pd.DataFrame()
    page = 1

    print('FETCHING TICKET DATA FROM ZAMMAD...')
    while True:
        cmd =  "curl -u " + os.getenv("ZAMMAD_EMAIL") + ":" + os.getenv("ZAMMAD_PASSWORD") + " " + os.getenv("ZAMMAD_HOST") + "/api/v1/tickets/search?query=" + \
                "created_at%3A%3E" + (pd.to_datetime("now") - pd.Timedelta(days=dias)).strftime("%Y-%m-%d") + \
                "%20OR%20updated_at%3A%3E" + (pd.to_datetime("now") - pd.Timedelta(days=dias)).strftime("%Y-%m-%d") + \
                "%20OR%20close_at%3A%3E" + (pd.to_datetime("now") - pd.Timedelta(days=dias)).strftime("%Y-%m-%d") + \
                "?expand=true&page=" + str(page) + "&per_page=200"
        
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        process.wait()
        
        if json.loads(stdout.decode())['tickets_count'] == 0:
            break

        df_aux = pd.DataFrame()
        for id in json.loads(stdout.decode())['assets']['Ticket'].keys():
            cmd_aux =  "curl -u " + os.getenv("ZAMMAD_EMAIL") + ":" + os.getenv("ZAMMAD_PASSWORD") + " " + os.getenv("ZAMMAD_HOST") + "/api/v1/tickets/" + str(id) + "?expand=true"
        
            args_aux = shlex.split(cmd_aux)
            process_aux = subprocess.Popen(args_aux, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_aux, stderr_aux = process_aux.communicate()
            process_aux.wait()
            
            if 'error' in json.loads(stdout_aux.decode()).keys():
                print("Error fetching ticket by id!")
                break
            
            dict_aux = { your_key: json.loads(stdout_aux.decode())[your_key] for your_key in ['created_at', 'close_at', 'updated_at', 'create_article_type', 'state', 'id', 'number', 'group'] }

            if len(dict_aux) == 0:
                break

            if dict_aux['created_at'] is not None:
                dict_aux['created_at'] = datetime.strptime(dict_aux['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            elif dict_aux['created_at'] is None:
                dict_aux['created_at'] = "null"

            if dict_aux['close_at'] is not None:
                dict_aux['close_at'] = datetime.strptime(dict_aux['close_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            elif dict_aux['close_at'] is None:
                dict_aux['close_at'] = "null"
        
            if dict_aux['updated_at'] is not None:
                dict_aux['updated_at'] = datetime.strptime(dict_aux['updated_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            elif dict_aux['updated_at'] is None:
                dict_aux['updated_at'] = "null"
   
            df_aux = df_aux.append(dict_aux, ignore_index=True)

        df = df.append(df_aux, ignore_index=True)
        
        if df.empty:    
            break

        print("[GETTING PAGE: " + str(page) + "]")
        page += 1

    print('END FETCHING TICKET DATA FROM ZAMMAD...')
    if not df.empty:
        save_data_tickets(df)