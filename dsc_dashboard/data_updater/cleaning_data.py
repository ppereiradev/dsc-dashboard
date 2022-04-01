import pandas as pd
import os
from datetime import datetime, timedelta

from .mongo_utils import count_tickets, get_many_tickets
import calendar

def weekday_count(start, end):
    """
    Count week days.

    Count how many week days have between a start and 
    end date. In other words, it counts how many Monday,
    Tuesday, Wednesday, Thursday, Friday, Saturday, 
    and Sunday were in the date interval.

    Parameters
    ----------
    start : str
        String that has a date format (e.g., 01/01/2020)
        representing the start date of the interval,
        it has to be less than end date.
    end : str
        String that has a date format (e.g., 01/01/2020)
        representing the end date of the interval,
        it has to be greater than start date.

    Returns
    -------
    dict of {str : int}
        Dictionary with the amount of week days in the
        date interval.

    Examples
    --------
    >>> _weekday_count('01/01/2020','31/01/2021')
    {'Monday': 4, 'Tuesday': 4, 'Friday': 5, 'Wednesday': 4,
    Thursday': 5, 'Sunday': 4, 'Saturday': 4}
    >>> _weekday_count('01/01/2020','31/12/2021')
    {'Monday': 52, 'Tuesday': 52, 'Friday': 52, 'Wednesday': 52,
    'Thursday': 53, 'Sunday': 52, 'Saturday': 52}
    """
    start_date = datetime.strptime(start, '%d/%m/%Y')
    end_date = datetime.strptime(end, '%d/%m/%Y')
    week = {}
    for i in range((end_date - start_date).days):
        day = calendar.day_name[(start_date + timedelta(days=i+1)).weekday()]
        week[day] = week[day] + 1 if day in week else 1
    return week

def clean_data():
    """
    Get, convert, and clean the ticket data.

    Get the last four-month ticket data from 
    the MongoDB, convert MongoDB date into Pandas Datetime,
    map the tickets states, create the mapping for the months, 
    and also create a date list of the last 4 months.

    Returns
    -------
    df_tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.
    mes_map : dict of {int : str}
        Dictionary with the number of month and its name in portuguese.
    date_list : list of str
        List of strings that represent the date of the last 4 months.
    """
    df_tickets = get_many_tickets({ "$or": [ {"created_at":{"$gte": (datetime.now() - timedelta(days=120)) }},
                                             {"close_at":{"$gte": (datetime.now() - timedelta(days=120)) }} ]})
        
    df_tickets['created_at'] = df_tickets['created_at'].map(lambda x: x if x != "null" else None)
    df_tickets['close_at'] = df_tickets['close_at'].map(lambda x: x if x != "null" else None)
    df_tickets['updated_at'] = df_tickets['updated_at'].map(lambda x: x if x != "null" else None)
    
    df_tickets['created_at'] = pd.to_datetime(df_tickets['created_at'])
    df_tickets['close_at'] = pd.to_datetime(df_tickets['close_at'])
    df_tickets['updated_at'] = pd.to_datetime(df_tickets['updated_at'])

    df_tickets['created_at'] = df_tickets['created_at'] + pd.DateOffset(hours=-3)
    df_tickets['close_at'] = df_tickets['close_at'] + pd.DateOffset(hours=-3)
    df_tickets['updated_at'] = df_tickets['updated_at'] + pd.DateOffset(hours=-3)

    estados = {"closed":"Fechado",
                  "open":"Aberto",
                  "resolvido":"Resolvido",
                  "new":"Novo",
                  "aguardando resposta":"Aguardando Resposta",
                  "pendente":"Pendente",
                  "retorno":"Retorno",
                  }

    df_tickets['state'] = df_tickets['state'].map(estados)
    
    mes_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
               5: "Maio",  6: "Junho",  7: "Julho",  8: "Agosto",  
               9: "Setembro",  10: "Outubro", 11: "Novembro",  12: "Dezembro"}
    date_list = pd.period_range(pd.Timestamp.now().to_period('m')-3, freq='M', periods=4).strftime('%Y-%m-%d').tolist()

    return df_tickets, mes_map, date_list

def get_by_state(df_tickets, mes_map, date_list, sector=None):
    """
    Group data by state.

    Separate the data by states of the tickets, then
    return the grouped data.

    Parameters
    ----------
    df_tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.
    mes_map : dict of {int : str}
        Dictionary with the number of month and its name in portuguese.
    date_list : list of str
        List of strings that represent the date of the last 4 months.

    Returns
    -------
    df_estados : pd.DataFrame
        Pandas Dataframe the amount of tickets grouped by ticket states
        and month of the year (last four months).
    abertos_mes_atual : int
        Integer that represents how many open tickets the current months has.
    fechados_mes_atual : int
        Integer that represents how many closed tickets the current months has.
    total_fechados : int
        Integer that represents the number of tickets that 
        was closed.
    acumulados : int
        Integer represents the number of tickets that is still open.
    """
    df_tickets_aux = df_tickets.copy()
    map_setores = {"SIG@": "Sistemas",
               "SIGAA": "Sistemas",
               "SIPAC": "Sistemas",
               "SIGRH": "Sistemas",
               "Sistemas Diversos": "Sistemas",
               "Web Sites": "Sistemas",
               "Triagem": "Suporte ao Usuário",
               "Serviços Computacionais": "Serviços Computacionais",
               "Micro Informática": "Micro Informática",
               "Conectividade": "Conectividade",
               "CODAI": "CODAI",
               "UABJ": "UABJ",
               "UAST": "UAST",
               "UACSA": "UACSA",
               "UAEADTec": "UAEADTec"
               }

    df_tickets_aux['group'] = df_tickets_aux['group'].map(map_setores)
    
    if sector == "Sistemas":
        df_tickets_aux = df_tickets_aux[df_tickets_aux['group'] == "Sistemas"]
    
    elif sector == "Suporte ao Usuário":
        df_tickets_aux = df_tickets_aux[df_tickets_aux['group'] == "Suporte ao Usuário"]
    
    elif sector == "Serviços Computacionais":
        df_tickets_aux = df_tickets_aux[df_tickets_aux['group'] == "Serviços Computacionais"]
    
    elif sector == "Micro Informática":
        df_tickets_aux = df_tickets_aux[df_tickets_aux['group'] == "Micro Informática"]

    elif sector == "Conectividade":
        df_tickets_aux = df_tickets_aux[df_tickets_aux['group'] == "Conectividade"]


    # ABERTOS
    df_abertos = df_tickets_aux.copy()
    df_abertos = df_abertos[(df_abertos['created_at'] <= datetime.now())]
    df_abertos = df_abertos[['created_at', 'state', 'id']]
    
    aux_abertos = {}
    for date in date_list:
        aux_abertos[pd.to_datetime(date).date().strftime('%y-%m')] = df_abertos[(df_abertos['created_at'].dt.month == pd.to_datetime(date).month)]['id'].count()

    abertos_dict = {}
    for key in aux_abertos.keys():
        abertos_dict[mes_map[int(key.split('-')[1])] + '/' +  key.split('-')[0]] = aux_abertos[key]

    df_abertos = pd.DataFrame(abertos_dict.values(), index=abertos_dict.keys(), columns=['qnt'])
    df_abertos.index.name = 'mes/ano'

    abertos_mes_atual = df_abertos['qnt'][-1]
    
    # FECHADOS
    df_fechados = df_tickets_aux.copy()
    df_fechados = df_fechados[(df_fechados['close_at'] <= datetime.now()) & (df_fechados['state'] == "Fechado")]
    df_fechados = df_fechados[['close_at', 'state', 'id']]
    
    aux_fechados = {}
    for date in date_list:
        aux_fechados[pd.to_datetime(date).date().strftime('%y-%m')] = df_fechados[(df_fechados['close_at'].dt.month == pd.to_datetime(date).month)]['id'].count()

    fechados_dict = {}
    for key in aux_fechados.keys():
        fechados_dict[mes_map[int(key.split('-')[1])] + '/' +  key.split('-')[0]] = aux_fechados[key]

    
    df_fechados = pd.DataFrame(fechados_dict.values(), index=fechados_dict.keys(), columns=['qnt'])
    df_fechados.index.name = 'mes/ano'
    
    fechados_mes_atual = df_fechados['qnt'][-1]
    total_fechados = count_tickets({ "state": "closed" })
    
    # ACUMULADOS
    df_acumulados = df_abertos.copy()
    
    abertos_antigos = count_tickets({ "created_at": { "$lte":  (datetime.strptime(date_list[0] + " 23:59:59", '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)) } })
    fechados_antigos = count_tickets({ "close_at": { "$lte":  (datetime.strptime(date_list[0] + " 23:59:59", '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)) } })
    
    df_acumulados.iloc[0, 0] += abertos_antigos - (df_fechados.iloc[0, 0] + fechados_antigos)

    for i in range(1, len(date_list)):
        df_acumulados.iloc[i, 0] += df_acumulados.iloc[i - 1, 0] - df_fechados.iloc[i, 0]

    acumulados = df_acumulados['qnt'][-1]

    # COMPLETE DATAFRAME
    df_estados = pd.merge(df_abertos,df_fechados, on='mes/ano',how='inner')
    df_estados = pd.merge(df_estados,df_acumulados, on='mes/ano',how='inner')
    df_estados.columns = ['abertos', 'fechados', 'acumulados']    
    
    return df_estados, abertos_mes_atual, fechados_mes_atual, total_fechados, acumulados

def get_leadtime(df_tickets, mes_map):
    """
    Calculate the leadtime of the tickets.

    Get the tickets then calculate the 
    leadtime of each sector. Also map sectors name.

    Parameters
    ----------
    df_tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.
    mes_map : dict of {int : str}
        Dictionary with the number of month and its name in portuguese.

    Returns
    -------
    df_leadtime_setores : pd.DataFrame
        Pandas Dataframe with the leadtime of each sector.
    df_leadtime_unidades : pd.DataFrame
        Pandas Dataframe with the leadtime of each campus of 
        UFRPE.
    """
    df_leadtime = df_tickets.copy()
    df_leadtime = df_leadtime.dropna(axis=0, subset=['close_at'])
    
    map_setores = {"SIG@": "Sistemas",
               "SIGAA": "Sistemas",
               "SIPAC": "Sistemas",
               "SIGRH": "Sistemas",
               "Sistemas Diversos": "Sistemas",
               "Web Sites": "Sistemas",
               "Triagem": "Suporte ao Usuário",
               "Serviços Computacionais": "Serviços Computacionais",
               "Micro Informática": "Micro Informática",
               "Conectividade": "Conectividade",
               "CODAI": "CODAI",
               "UABJ": "UABJ",
               "UAST": "UAST",
               "UACSA": "UACSA",
               "UAEADTec": "UAEADTec"
               }

    df_leadtime['group'] = df_leadtime['group'].map(map_setores)
    
    df_leadtime = df_leadtime[df_leadtime['state'] == 'Fechado']
    df_leadtime = df_leadtime[['state', 'group', 'created_at', 'close_at']]
    
    # keeping tickets from last 3 months only
    df_leadtime = df_leadtime[df_leadtime['close_at'] > (datetime.now() - timedelta(days=90))]

    df_leadtime['diff'] = df_leadtime['close_at'] - df_leadtime['created_at']
    df_leadtime['diff'] = df_leadtime['diff'].astype('timedelta64[h]')

    # checking if the ticket was closed at the same month that it was created (0 or 1)
    #df_leadtime['flag'] = (df_leadtime['close_at'].dt.month == df_leadtime['created_at'].dt.month).astype(int)
    
    # removing tickets that were not created in the same month that they were closed
    #df_leadtime = df_leadtime[df_leadtime['flag'] == 1]
    
    df_leadtime_aux = pd.DataFrame(columns=['mes/ano', 'group', 'diff'])
    for i in range(0, len(df_leadtime['diff'])):
        df_leadtime_aux.loc[i] = [df_leadtime['close_at'].iloc[i].date().strftime('%y-%m'), df_leadtime['group'].iloc[i], df_leadtime['diff'].iloc[i]]

    df_leadtime_aux = df_leadtime_aux.groupby(['mes/ano', 'group']).mean().reset_index()
    df_leadtime_aux['diff'] = df_leadtime_aux['diff']/24
    df_leadtime_aux['diff'] = df_leadtime_aux['diff'].astype(int)
    
    setores_list = ["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade","CODAI","UABJ","UAST","UACSA","UAEADTec"]
    
    for mes in df_leadtime_aux['mes/ano']:
        for setor in setores_list:
            if setor not in df_leadtime_aux[(df_leadtime_aux['mes/ano'] == mes)]['group'].to_list():
                df_leadtime_aux = df_leadtime_aux.append({"mes/ano": mes, "group": setor, "diff": 0}, ignore_index=True)
        
    df_leadtime_aux = df_leadtime_aux.sort_values(by='mes/ano').reset_index(drop=True)

    df_leadtime_setores = df_leadtime_aux.loc[df_leadtime_aux['group'].isin(["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade"])]
    df_leadtime_unidades = df_leadtime_aux.loc[df_leadtime_aux['group'].isin(["CODAI","UABJ","UAST","UACSA","UAEADTec"])]

    df_leadtime_setores = df_leadtime_setores.pivot_table('diff', 'mes/ano', 'group')
    df_leadtime_unidades = df_leadtime_unidades.pivot_table('diff', 'mes/ano', 'group')

    df_leadtime_setores = df_leadtime_setores.reset_index(level=[0])
    df_leadtime_unidades = df_leadtime_unidades.reset_index(level=[0])
    df_leadtime_setores['mes/ano'] = df_leadtime_setores['mes/ano'].apply(lambda x: mes_map[int(x.split('-')[1])] + '/' + x.split('-')[0])
    df_leadtime_unidades['mes/ano'] = df_leadtime_unidades['mes/ano'].apply(lambda x: mes_map[int(x.split('-')[1])] + '/' + x.split('-')[0])

    return df_leadtime_setores, df_leadtime_unidades

def get_by_week(df_tickets):
    """
    Calculate the amount of tickets by weekday.

    Calculate the number of tickets opened in each
    week dayi.e., Monday, Tuesday, Wednesday, Thursday,
    Friday, Saturday, and Sunday). It separetes the tickets
    opened by web and by telephone.

    Parameters
    ----------
    df_tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.

    Returns
    -------
    df_portal_semana : pd.DataFrame
        Pandas Dataframe with the amount of tickets opended
        over the web in each weekday (i.e., Monday, Tuesday,
        Wednesday, Thursday, Friday, Saturday, and Sunday).
    df_telefone_semana : pd.DataFrame
        Pandas Dataframe with the amount of tickets opended
        over the telephone in each weekday (i.e., Monday, Tuesday,
        Wednesday, Thursday, Friday, Saturday, and Sunday).
    """
    df_semana = df_tickets.copy()
    df_semana = df_semana[['created_at', 'create_article_type']]
    df_semana.columns = ['criado', 'tipo']

    df_semana['dia'] = df_semana['criado'].dt.day_name()
    df_semana = df_semana[df_semana["criado"] >= (pd.to_datetime("now") - pd.Timedelta(days=30))]


    day_translation = {"Monday":"Segunda",
                    "Tuesday":"Terça",
                    "Wednesday":"Quarta",
                    "Thursday":"Quinta",
                    "Friday":"Sexta",
                    "Saturday":"Sábado",
                    "Sunday":"Domingo",
                    }

    type_translation = {"email":"Portal",
                    "web":"Portal",
                    "note":"Portal",
                    "phone":"Telefone",
                    }


    df_semana['tipo'] = df_semana['tipo'].map(type_translation)

    df_portal_semana = df_semana.loc[df_semana['tipo'] == "Portal", 'dia'].value_counts().rename_axis('dia').reset_index(name='total')
    df_telefone_semana = df_semana.loc[df_semana['tipo'] == "Telefone", 'dia'].value_counts().rename_axis('dia').reset_index(name='total')
    
    df_portal_semana['dia'] = df_portal_semana['dia'].map(day_translation)
    df_telefone_semana['dia'] = df_telefone_semana['dia'].map(day_translation)

    return df_portal_semana, df_telefone_semana

def get_by_hour(df_tickets):
    """
    Calculate the amount tickets by hour.

    Calculate the amount of tickets opened by hour
    of the day, the data is divided into two groups:
    web and telephone.

    Parameters
    ----------
    df_tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.

    Returns
    -------
    df_horas : pd.DataFrame
        Pandas Dataframe with the amount of tickets opended
        each hour of day. The tickets are divided into two groups
        (i.e., web and telephone).
    """
    df_horas = df_tickets.copy()
    df_horas = df_horas[['created_at', 'create_article_type']]
    df_horas.columns = ['criado', 'tipo']
    df_horas = df_horas[df_horas["criado"] >= (pd.to_datetime("now") - pd.Timedelta(days=30))]

    type_translation = {"email":"Portal",
                    "web":"Portal",
                    "note":"Portal",
                    "phone":"Telefone",
                    }
    df_horas['tipo'] = df_horas['tipo'].map(type_translation)

    hours_day = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                '20', '21', '22', '23']

    df_portal_horas = df_horas['criado'][df_horas['tipo'] == "Portal"].dt.hour.value_counts().rename_axis('hora').reset_index(name='qnt')
    df_telefone_horas = df_horas['criado'][df_horas['tipo'] == "Telefone"].dt.hour.value_counts().rename_axis('hora').reset_index(name='qnt')

    for hour in hours_day:
        if int(hour) not in df_portal_horas['hora'].to_list():
            df_portal_horas = df_portal_horas.append({'hora': int(hour), 'qnt': 0}, ignore_index=True)

        if int(hour) not in df_telefone_horas['hora'].to_list():
            df_telefone_horas = df_telefone_horas.append({'hora': int(hour), 'qnt': 0}, ignore_index=True)

    df_portal_horas = df_portal_horas.sort_values(by='hora').reset_index(drop=True)
    df_telefone_horas = df_telefone_horas.sort_values(by='hora').reset_index(drop=True)

    df_horas = pd.merge(df_portal_horas,df_telefone_horas, on='hora',how='inner', suffixes=('_portal', '_telefone'))

    return df_horas

def get_satisfaction():
    """
    Get the customers' satisfaction data.

    Get the customers' satisfaction data from the
    Google Forms.

    Returns
    -------
    df_satisfacao : pd.DataFrame
        Pandas Dataframe with the customers' satisfaction
        information.
    """
    url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}/gviz/tq?tqx=out:csv&sheet={os.getenv('GOOGLE_SHEET_NAME')}"
    df_aux = pd.read_csv(url)
    score_column = df_aux.columns[1]
    ticket_number_column = df_aux.columns[-1]
    df_aux = df_aux.drop_duplicates(subset=ticket_number_column, keep="last")

    df_satisfacao = pd.DataFrame(None, index =[0,1,2,3,4,5,6,7,8,9,10], columns =['qnt'])
    df_satisfacao['qnt'] = df_satisfacao.index.map(df_aux[score_column].value_counts()).fillna(0).astype(int)
    df_satisfacao['percentage'] = df_satisfacao.index.map(df_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)

    return df_satisfacao

def get_data():
    """
    Return the processed data.

    Make use of internal functions to get the processed data, 
    and pass to the dashboard.

    Returns
    -------
    dict of {str : int or pd.DataFrame}
        Dictionary with integers and Pandas DataFrame
        composed of the processed data.
    """
    df_tickets, mes_map, date_list = clean_data()
    df_estados, abertos_mes_atual, fechados_mes_atual, total_fechados, acumulados = get_by_state(df_tickets, mes_map, date_list)
    df_leadtime_setores, df_leadtime_unidades = get_leadtime(df_tickets, mes_map)
    df_portal_semana, df_telefone_semana = get_by_week(df_tickets)
    df_horas = get_by_hour(df_tickets)
    df_satisfacao = get_satisfaction()

    # getting data by sector of STD

    # conectividade
    df_estados_conectividade, abertos_mes_atual_conectividade, fechados_mes_atual_conectividade, \
        total_fechados_conectividade, acumulados_conectividade = get_by_state(df_tickets, mes_map, date_list, "Conectividade")
    
    # sistemas
    df_estados_sistemas, abertos_mes_atual_sistemas, fechados_mes_atual_sistemas, \
        total_fechados_sistemas, acumulados_sistemas = get_by_state(df_tickets, mes_map, date_list, "Sistemas")

    # suporte
    df_estados_suporte, abertos_mes_atual_suporte, fechados_mes_atual_suporte, \
        total_fechados_suporte, acumulados_suporte = get_by_state(df_tickets, mes_map, date_list, "Suporte ao Usuário")

    # servicos
    df_estados_servicos, abertos_mes_atual_servicos, fechados_mes_atual_servicos, \
        total_fechados_servicos, acumulados_servicos = get_by_state(df_tickets, mes_map, date_list, "Serviços Computacionais")
    
    # micro
    df_estados_micro, abertos_mes_atual_micro, fechados_mes_atual_micro, \
        total_fechados_micro, acumulados_micro = get_by_state(df_tickets, mes_map, date_list, "Micro Informática")

    return {'total-fechados': total_fechados,
            'df-satisfacao': df_satisfacao,
            'df-estados': df_estados,
            'abertos-mes-atual': abertos_mes_atual,
            'fechados-mes-atual': fechados_mes_atual,
            'acumulados': acumulados,
            'df-leadtime-setores': df_leadtime_setores,
            'df-leadtime-unidades': df_leadtime_unidades,
            'df-portal-semana': df_portal_semana,
            'df-telefone-semana': df_telefone_semana,
            'df-horas': df_horas,

            # conectividade
            'total-fechados-conectividade': total_fechados_conectividade,
            'df-estados-conectividade': df_estados_conectividade,
            'abertos-mes-atual-conectividade': abertos_mes_atual_conectividade,
            'fechados-mes-atual-conectividade': fechados_mes_atual_conectividade,
            'acumulados-conectividade': acumulados_conectividade,

            # sistemas
            'total-fechados-sistemas': total_fechados_sistemas,
            'df-estados-sistemas': df_estados_sistemas,
            'abertos-mes-atual-sistemas': abertos_mes_atual_sistemas,
            'fechados-mes-atual-sistemas': fechados_mes_atual_sistemas,
            'acumulados-sistemas': acumulados_sistemas,

            # Suporte ao Usuário
            'total-fechados-suporte': total_fechados_suporte,
            'df-estados-suporte': df_estados_suporte,
            'abertos-mes-atual-suporte': abertos_mes_atual_suporte,
            'fechados-mes-atual-suporte': fechados_mes_atual_suporte,
            'acumulados-suporte': acumulados_sistemas,

            # Serviços Computacionais
            'total-fechados-servicos': total_fechados_servicos,
            'df-estados-servicos': df_estados_servicos,
            'abertos-mes-atual-servicos': abertos_mes_atual_servicos,
            'fechados-mes-atual-servicos': fechados_mes_atual_servicos,
            'acumulados-servicos': acumulados_servicos,

            # Micro Informática
            'total-fechados-micro': total_fechados_micro,
            'df-estados-micro': df_estados_micro,
            'abertos-mes-atual-micro': abertos_mes_atual_micro,
            'fechados-mes-atual-micro': fechados_mes_atual_micro,
            'acumulados-micro': acumulados_micro,
            }
