import pandas as pd
import shlex
import subprocess
import json
import os
from dateutil.tz import gettz
from datetime import datetime
from tickets.models import Ticket
from .data_processing.processed_data import ProcessedData
from dateutil.parser import parse
import pytz

processed_data = ProcessedData()

def all_tickets():
    """
    Get all tickets from Zammad.

    Get all tickets from Zammad using its API, put into
    a Pandas DataFrame, then call :func:`save_data_tickets`
    to put all data on MongoDB. This function also converts
    the date string from Zammad into datetime, which is needed
    for the MongoDB.
    """
    df = pd.DataFrame()
    page = 1

    print('FETCHING ALL TICKET DATA FROM ZAMMAD...')
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

        df = pd.concat([df, df_aux])

        print("[GETTING PAGE: " + str(page) + "]")
        page += 1
    
    print('ENDED FETCHING ALL TICKET DATA FROM ZAMMAD...')

    df = df[['created_at', 'close_at', 'updated_at', 'create_article_type', 'state', 'id', 'number', 'group']]
    
    df_records = df.to_dict('records')
    
    for record in df_records:
        ticket, created = Ticket.objects.update_or_create(
            number=record['number'],
            defaults={
                'id_ticket': record['id'],
                'number': record['number'],
                'created_at': parse(record['created_at']) if record['created_at'] else None,
                'close_at': parse(record['close_at']) if record['close_at'] else None,
                'updated_at': parse(record['updated_at']) if record['updated_at'] else None,
                'create_article_type': record['create_article_type'],
                'state': record['state'],
                'group': record['group'],
            })
        if created:
            print("[", ticket, "] Ticket added to database...")
        else:
            print("[", ticket, "] Ticket updated...")
        
    processed_data.get_processed_data_all()


def interval_tickets(dias=120):
    """
    Get ticket data from a date to today.

    Get tickets from Zammad using its API, getting it from 
    last ``dias`` util today, then put them into a Pandas DataFrame,
    call :func:`save_data_tickets` to put data on MongoDB.
    This function also converts the date string from Zammad
    into datetime, which is needed for the MongoDB.

    Parameters
    ----------
    dias : int
        Integer that represents how many days before today
        it will get the tickets.
    """
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

        for id in json.loads(stdout.decode())['assets']['Ticket'].keys():
            cmd_aux =  "curl -u " + os.getenv("ZAMMAD_EMAIL") + ":" + os.getenv("ZAMMAD_PASSWORD") + " " + os.getenv("ZAMMAD_HOST") + "/api/v1/tickets/" + str(id) + "?expand=true"
        
            args_aux = shlex.split(cmd_aux)
            process_aux = subprocess.Popen(args_aux, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_aux, stderr_aux = process_aux.communicate()
            process_aux.wait()
            
            if 'error' in json.loads(stdout_aux.decode()).keys():
                print("Error fetching ticket by id!")
                break
            
            columns_interest = ['created_at', 'close_at', 'updated_at', 'create_article_type', 'state', 'id', 'number', 'group']
            dict_aux = {}
            for k, v in json.loads(stdout_aux.decode()).items():
                if k in columns_interest:
                    dict_aux[k] = v

            df_aux = pd.DataFrame([dict_aux])

            if len(df_aux.columns) > 52:
                df_aux.drop(columns=df_aux.columns[-1], axis=1, inplace=True)

            if df_aux.empty:    
                break

            df = pd.concat([df, df_aux])
        
        if df.empty:    
            break

        print("[GETTING PAGE: " + str(page) + "]")
        page += 1

    df = df[['created_at', 'close_at', 'updated_at', 'create_article_type', 'state', 'id', 'number', 'group']]

    print('END FETCHING TICKET DATA FROM ZAMMAD...')
    if not df.empty:
        df_records = df.to_dict('records')

        for record in df_records:
            ticket, created = Ticket.objects.update_or_create(
                number=record['number'],
                defaults={
                    'id_ticket': record['id'],
                    'number': record['number'],
                    'created_at': parse(record['created_at']) if record['created_at'] else None,
                    'close_at': parse(record['close_at']) if record['close_at'] else None,
                    'updated_at': parse(record['updated_at']) if record['updated_at'] else None,
                    'create_article_type': record['create_article_type'],
                    'state': record['state'],
                    'group': record['group'],
                })
            if created:
                print("[", ticket, "] Ticket added to database...")
            else:
                print("[", ticket, "] Ticket updated...")

    processed_data.get_processed_data_all()