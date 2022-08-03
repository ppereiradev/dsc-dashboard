import pandas as pd
import os
from datetime import datetime, timedelta

from .mongo_utils import count_tickets, get_tickets_from_db

# constants
AMOUNT_MONTHS_IN_DAYS = 120
MONTH_NUMBER_TO_NAME = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}
ZAMMAD_GROUPS_TO_STD_SECTORS = {
    "SIG@": "Sistemas",
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

# functions
def get_data_from_last_four_months():
    """
    Get the ticket data.

    Get the last four-month ticket data from the MongoDB.

    Returns
    -------
    tickets : pd.DataFrame
        Pandas Dataframe with the Zammad tickets from MongoDB.
    """ 
    tickets = get_tickets_from_db({ "$or": [ {"created_at":{"$gte": (datetime.now() - timedelta(days=AMOUNT_MONTHS_IN_DAYS)) }},
                                             {"close_at":{"$gte": (datetime.now() - timedelta(days=AMOUNT_MONTHS_IN_DAYS)) }} ]})
    return tickets

def clean_data(tickets):
    """
    Clean the ticket data.

    Convert MongoDB date into Pandas Datetime,
    map the tickets states.

    Returns
    -------
    tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.
    """ 
    # substituing null values for None
    tickets['created_at'] = tickets['created_at'].map(lambda x: x if x != "null" else None)
    tickets['close_at'] = tickets['close_at'].map(lambda x: x if x != "null" else None)
    tickets['updated_at'] = tickets['updated_at'].map(lambda x: x if x != "null" else None)
    
    # converting into pandas date format 
    # and adding an offset to the hour 
    # in order to meet brazilian time
    tickets['created_at'] = pd.to_datetime(tickets['created_at']) + pd.DateOffset(hours=-3)
    tickets['close_at'] = pd.to_datetime(tickets['close_at']) + pd.DateOffset(hours=-3)
    tickets['updated_at'] = pd.to_datetime(tickets['updated_at']) + pd.DateOffset(hours=-3)

    ticket_states_to_portuguese = {
        "closed":"Fechado",
        "open":"Aberto",
        "resolvido":"Resolvido",
        "new":"Novo",
        "aguardando resposta":"Aguardando Resposta",
        "pendente":"Pendente",
        "retorno":"Retorno",
    }

    tickets['state'] = tickets['state'].map(ticket_states_to_portuguese)
    tickets['group'] = tickets['group'].map(ZAMMAD_GROUPS_TO_STD_SECTORS)

    return tickets

def get_by_state(tickets, sector="Diretoria"):
    """
    Group data by state.

    Separate the data by states of the tickets, then
    return the grouped data.

    Parameters
    ----------
    tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.
    DATES_FROM_LAST_FOUR_MONTHS : list of str
        List of strings that represent the date of the last 4 months.

    Returns
    -------
    estados : pd.DataFrame
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
    open_tickets_previous = closed_tickets_previous = closed_tickets_total = 0
    dates_three_months_ago_from_today = pd.period_range(pd.Timestamp.now().to_period('m')-3,freq='M', 
                                                        periods=4).strftime('%Y-%m-%d').tolist()
    last_day_three_months_ago = datetime.strptime(dates_three_months_ago_from_today[0] + " 23:59:59",
                                                '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)

    if sector == "Diretoria":
        open_tickets_previous = count_tickets(
            { "created_at": { "$lte": last_day_three_months_ago } }
        )

        closed_tickets_previous = count_tickets(
            { "close_at": { "$lte": last_day_three_months_ago } }
        )
        
        closed_tickets_total = count_tickets({ "state": "closed" })
    
    else:
        tickets = tickets[tickets['group'] == sector]
       
        # getting keys from values
        zammad_groups = [key for key,value in  ZAMMAD_GROUPS_TO_STD_SECTORS.items() if value == sector]
        for group in zammad_groups:
            # getting old open tickets of Sistemas to calculate the acumulados
            open_tickets_previous += count_tickets(
                { "$and": [ 
                            {"group": group}, { "created_at": { "$lte": last_day_three_months_ago } } 
                    ] 
                } )
            closed_tickets_previous += count_tickets(
                { "$and": [ 
                            {"group": group}, { "close_at": { "$lte": last_day_three_months_ago } } 
                    ] 
                })
            closed_tickets_total += count_tickets(
                { "$and": [ 
                            {"group": group}, { "state": "closed" } 
                    ] 
                })

    # open tickets
    open_tickets = tickets.copy(deep=True)
    open_tickets = open_tickets[(open_tickets['created_at'] <= datetime.now())]
    open_tickets = open_tickets[['created_at', 'state', 'id']]
    
    open_dict = {}
    for date in dates_three_months_ago_from_today:
        date_aux = pd.to_datetime(date).date().strftime('%y-%m')
        open_dict[
                MONTH_NUMBER_TO_NAME[int(date_aux.split('-')[1])] + '/' +  date_aux.split('-')[0]
            ] = open_tickets[
                        (open_tickets['created_at'].dt.month == pd.to_datetime(date).month)
                    ]['id'].count()

    open_tickets = pd.DataFrame(open_dict.values(), index=open_dict.keys(), columns=['qnt'])
    open_tickets.index.name = 'mes/ano'

    open_tickets_current_month = open_tickets['qnt'][-1]
    
    # closed tickets
    closed_tickets = tickets.copy(deep=True)
    closed_tickets = closed_tickets[(closed_tickets['close_at'] <= datetime.now()) & (closed_tickets['state'] == "Fechado")]
    closed_tickets = closed_tickets[['close_at', 'state', 'id']]
    
    closed_dict = {}
    for date in dates_three_months_ago_from_today:
        date_aux = pd.to_datetime(date).date().strftime('%y-%m')
        closed_dict[
                MONTH_NUMBER_TO_NAME[int(date_aux.split('-')[1])] + '/' +  date_aux.split('-')[0]
            ] = closed_tickets[
                        (closed_tickets['close_at'].dt.month == pd.to_datetime(date).month)
                    ]['id'].count()
    
    closed_tickets = pd.DataFrame(closed_dict.values(), index=closed_dict.keys(), columns=['qnt'])
    closed_tickets.index.name = 'mes/ano'
    
    closed_tickets_current_month = closed_tickets['qnt'][-1]
    
    # accumulated
    accumulated_tickets = open_tickets.copy(deep=True)
    accumulated_tickets.iloc[0, 0] += open_tickets_previous - (closed_tickets.iloc[0, 0] + closed_tickets_previous)
    
    for i in range(1, len(dates_three_months_ago_from_today)):
        accumulated_tickets.iloc[i, 0] += accumulated_tickets.iloc[i - 1, 0] - closed_tickets.iloc[i, 0]

    accumulated = accumulated_tickets['qnt'][-1]

    # COMPLETE DATAFRAME
    num_tickets_by_state = pd.merge(open_tickets,closed_tickets, on='mes/ano',how='inner')
    num_tickets_by_state = pd.merge(num_tickets_by_state,accumulated_tickets, on='mes/ano',how='inner')
    num_tickets_by_state.columns = ['abertos', 'fechados', 'acumulados']    

    return num_tickets_by_state, open_tickets_current_month, closed_tickets_current_month, closed_tickets_total, accumulated

def get_leadtime(tickets, sector=None):
    """
    Calculate the leadtime of the tickets.

    Get the tickets then calculate the 
    leadtime of each sector. Also map sectors name.

    Parameters
    ----------
    tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.
    MONTH_NUMBER_TO_NAME : dict of {int : str}
        Dictionary with the number of month and its name in portuguese.

    Returns
    -------
    tickets_setores : pd.DataFrame
        Pandas Dataframe with the leadtime of each sector.
    tickets_unidades : pd.DataFrame
        Pandas Dataframe with the leadtime of each campus of 
        UFRPE.
    """
    tickets = tickets.dropna(axis=0, subset=['close_at'])
    
    tickets = tickets[tickets['state'] == 'Fechado']
    tickets = tickets[['state', 'group', 'created_at', 'close_at']]
    
    # keeping tickets from last 6 months only
    tickets = tickets[tickets['close_at'] > (datetime.now() - timedelta(days=210))]
    #tickets = tickets[tickets['created_at'] > datetime(2021, 8, 1, 0, 0, 0, 0)]

    tickets['diff'] = tickets['close_at'] - tickets['created_at']
    tickets['diff'] = tickets['diff'].astype('timedelta64[h]')

    if sector is None:
        tickets_aux = pd.DataFrame(columns=['mes/ano', 'group', 'diff'])
        for i in range(0, len(tickets['diff'])):
            tickets_aux.loc[i] = [tickets['close_at'].iloc[i].date().strftime('%y-%m'), tickets['group'].iloc[i], tickets['diff'].iloc[i]]

        tickets_aux = tickets_aux.groupby(['mes/ano', 'group']).mean().reset_index()
        tickets_aux['diff'] = tickets_aux['diff']/24
        tickets_aux['diff'] = tickets_aux['diff'].astype(int)

        tickets_scatter = tickets.copy(deep=True)
        tickets_scatter['diff'] = tickets_scatter['diff']/24
        tickets_scatter['diff'] = tickets_scatter['diff'].astype(int)

        tickets_scatter["mes/ano"] = tickets_scatter['close_at'].dt.strftime('%y-%m')
        tickets_scatter = tickets_scatter.sort_values(by='mes/ano').reset_index(drop=True)
        tickets_scatter["mes/ano"] = tickets_scatter["mes/ano"].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        
        setores_list = ["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade","CODAI","UABJ","UAST","UACSA","UAEADTec"]
        
        for mes in tickets_aux['mes/ano']:
            for setor in setores_list:
                if setor not in tickets_aux[(tickets_aux['mes/ano'] == mes)]['group'].to_list():
                    tickets_aux = tickets_aux.append({"mes/ano": mes, "group": setor, "diff": 0}, ignore_index=True)
            
        tickets_aux = tickets_aux.sort_values(by='mes/ano').reset_index(drop=True)

        tickets_setores = tickets_aux.loc[tickets_aux['group'].isin(["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade"])]
        tickets_unidades = tickets_aux.loc[tickets_aux['group'].isin(["CODAI","UABJ","UAST","UACSA","UAEADTec"])]

        tickets_setores = tickets_setores.pivot_table('diff', 'mes/ano', 'group')
        tickets_unidades = tickets_unidades.pivot_table('diff', 'mes/ano', 'group')

        tickets_setores = tickets_setores.reset_index(level=[0])
        tickets_unidades = tickets_unidades.reset_index(level=[0])
        tickets_setores['mes/ano'] = tickets_setores['mes/ano'].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        tickets_unidades['mes/ano'] = tickets_unidades['mes/ano'].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
        
        return tickets_setores, tickets_unidades, tickets_scatter

    elif sector == "Sistemas":
        tickets = tickets[tickets['group'] == "Sistemas"]

    elif sector == "Suporte ao Usuário":
        tickets = tickets[tickets['group'] == "Suporte ao Usuário"]
    
    elif sector == "Serviços Computacionais":
        tickets = tickets[tickets['group'] == "Serviços Computacionais"]

    elif sector == "Micro Informática":
        tickets = tickets[tickets['group'] == "Micro Informática"]

    elif sector == "Conectividade":
        tickets = tickets[tickets['group'] == "Conectividade"]

    tickets = tickets.reset_index(drop=True)
    tickets_scatter = tickets.copy(deep=True)
    tickets_scatter["mes/ano"] = tickets_scatter['close_at'].dt.strftime('%y-%m')
    tickets_scatter = tickets_scatter.sort_values(by='mes/ano').reset_index(drop=True)
    tickets_scatter["mes/ano"] = tickets_scatter["mes/ano"].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])

    tickets_scatter['diff'] = tickets_scatter['diff']/24
    tickets_scatter['diff'] = tickets_scatter['diff'].astype(int)

    tickets['diff'] = tickets['diff']/24
    tickets['diff'] = tickets['diff'].astype(int)

    tickets_aux = pd.DataFrame(columns=['mes/ano', 'diff'])
    for i in range(0, len(tickets['diff'])):
        tickets_aux.loc[i] = [tickets['close_at'].iloc[i].date().strftime('%y-%m'), tickets['diff'].iloc[i]]

    tickets_aux = tickets_aux.groupby(['mes/ano']).mean().reset_index()
    tickets_aux['mes/ano'] = tickets_aux['mes/ano'].apply(lambda x: MONTH_NUMBER_TO_NAME[int(x.split('-')[1])] + '/' + x.split('-')[0])
    tickets = tickets_aux
    tickets['diff'] = tickets['diff'].astype(int)
    
    return tickets, tickets_scatter


    # checking if the ticket was closed at the same month that it was created (0 or 1)
    #tickets['flag'] = (tickets['close_at'].dt.month == tickets['created_at'].dt.month).astype(int)
    
    # removing tickets that were not created in the same month that they were closed
    #tickets = tickets[tickets['flag'] == 1]
    
    

def get_by_week(tickets):
    """
    Calculate the amount of tickets by weekday.

    Calculate the number of tickets opened in each
    week dayi.e., Monday, Tuesday, Wednesday, Thursday,
    Friday, Saturday, and Sunday). It separetes the tickets
    opened by web and by telephone.

    Parameters
    ----------
    tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.

    Returns
    -------
    tickets_portal_semana : pd.DataFrame
        Pandas Dataframe with the amount of tickets opended
        over the web in each weekday (i.e., Monday, Tuesday,
        Wednesday, Thursday, Friday, Saturday, and Sunday).
    tickets_telefone_semana : pd.DataFrame
        Pandas Dataframe with the amount of tickets opended
        over the telephone in each weekday (i.e., Monday, Tuesday,
        Wednesday, Thursday, Friday, Saturday, and Sunday).
    """
    tickets_semana = tickets.copy(deep=True)
    tickets_semana = tickets_semana[['created_at', 'create_article_type']]
    tickets_semana.columns = ['criado', 'tipo']
    
    tickets_semana['dia'] = tickets_semana['criado'].dt.day_name()
    tickets_semana = tickets_semana[tickets_semana["criado"] >= (pd.to_datetime("now") - pd.Timedelta(days=30))]

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


    tickets_semana['tipo'] = tickets_semana['tipo'].map(type_translation)

    tickets_portal_semana = tickets_semana.loc[tickets_semana['tipo'] == "Portal", 'dia'].value_counts().rename_axis('dia').reset_index(name='total')
    tickets_telefone_semana = tickets_semana.loc[tickets_semana['tipo'] == "Telefone", 'dia'].value_counts().rename_axis('dia').reset_index(name='total')
    
    tickets_portal_semana['dia'] = tickets_portal_semana['dia'].map(day_translation)
    tickets_telefone_semana['dia'] = tickets_telefone_semana['dia'].map(day_translation)

    return tickets_portal_semana, tickets_telefone_semana

def get_by_hour(tickets):
    """
    Calculate the amount tickets by hour.

    Calculate the amount of tickets opened by hour
    of the day, the data is divided into two groups:
    web and telephone.

    Parameters
    ----------
    tickets : pd.DataFrame
        Pandas Dataframe with the clean data of the Zammad tickets.

    Returns
    -------
    tickets_horas : pd.DataFrame
        Pandas Dataframe with the amount of tickets opended
        each hour of day. The tickets are divided into two groups
        (i.e., web and telephone).
    """
    tickets_horas = tickets.copy(deep=True)
    tickets_horas = tickets_horas[['created_at', 'create_article_type']]
    tickets_horas.columns = ['criado', 'tipo']
    tickets_horas = tickets_horas[tickets_horas["criado"] >= (pd.to_datetime("now") - pd.Timedelta(days=30))]

    type_translation = {"email":"Portal",
                    "web":"Portal",
                    "note":"Portal",
                    "phone":"Telefone",
                    }
    tickets_horas['tipo'] = tickets_horas['tipo'].map(type_translation)

    hours_day = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
                '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                '20', '21', '22', '23']

    tickets_portal_horas = tickets_horas['criado'][tickets_horas['tipo'] == "Portal"].dt.hour.value_counts().rename_axis('hora').reset_index(name='qnt')
    tickets_telefone_horas = tickets_horas['criado'][tickets_horas['tipo'] == "Telefone"].dt.hour.value_counts().rename_axis('hora').reset_index(name='qnt')

    for hour in hours_day:
        if int(hour) not in tickets_portal_horas['hora'].to_list():
            tickets_portal_horas = tickets_portal_horas.append({'hora': int(hour), 'qnt': 0}, ignore_index=True)

        if int(hour) not in tickets_telefone_horas['hora'].to_list():
            tickets_telefone_horas = tickets_telefone_horas.append({'hora': int(hour), 'qnt': 0}, ignore_index=True)

    tickets_portal_horas = tickets_portal_horas.sort_values(by='hora').reset_index(drop=True)
    tickets_telefone_horas = tickets_telefone_horas.sort_values(by='hora').reset_index(drop=True)

    tickets_horas = pd.merge(tickets_portal_horas,tickets_telefone_horas, on='hora',how='inner', suffixes=('_portal', '_telefone'))

    return tickets_horas

def get_satisfaction(tickets, sector=None):
    """
    Get the customers' satisfaction data.

    Get the customers' satisfaction data from the
    Google Forms.

    Returns
    -------
    tickets_satisfacao : pd.DataFrame
        Pandas Dataframe with the customers' satisfaction
        information.
    """
    tickets_satisfacao_aux = tickets.copy(deep=True)

    url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}/gviz/tq?tqx=out:csv&sheet={os.getenv('GOOGLE_SHEET_NAME')}"
    tickets_aux = pd.read_csv(url)
    score_column = tickets_aux.columns[1]
    ticket_number_column = tickets_aux.columns[-1]
    tickets_aux = tickets_aux.drop_duplicates(subset=ticket_number_column, keep="last")
    tickets_satisfacao = pd.DataFrame(None, index =[0,1,2,3,4,5,6,7,8,9,10], columns =['qnt'])

    tickets_satisfacao_aux['number'], tickets_aux[ticket_number_column] = tickets_satisfacao_aux['number'].astype(int), tickets_aux[ticket_number_column].astype(int)
    tickets_satisfacao_aux = pd.merge(tickets_satisfacao_aux, tickets_aux, left_on='number', right_on=ticket_number_column,how='inner')

    if sector is None: 
        tickets_satisfacao['qnt'] = tickets_satisfacao.index.map(tickets_aux[score_column].value_counts()).fillna(0).astype(int)
        tickets_satisfacao['percentage'] = tickets_satisfacao.index.map(tickets_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)
        
    elif sector == "Sistemas":
        tickets_satisfacao_aux = tickets_satisfacao_aux[tickets_satisfacao_aux['group'] == "Sistemas"]
        
        tickets_satisfacao['qnt'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts()).fillna(0).astype(int)
        tickets_satisfacao['percentage'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)

    elif sector == "Suporte ao Usuário":
        tickets_satisfacao_aux = tickets_satisfacao_aux[tickets_satisfacao_aux['group'] == "Suporte ao Usuário"]
        
        tickets_satisfacao['qnt'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts()).fillna(0).astype(int)
        tickets_satisfacao['percentage'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)
    
    elif sector == "Serviços Computacionais":
        tickets_satisfacao_aux = tickets_satisfacao_aux[tickets_satisfacao_aux['group'] == "Serviços Computacionais"]
        
        tickets_satisfacao['qnt'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts()).fillna(0).astype(int)
        tickets_satisfacao['percentage'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)

    elif sector == "Micro Informática":
        tickets_satisfacao_aux = tickets_satisfacao_aux[tickets_satisfacao_aux['group'] == "Micro Informática"]
        
        tickets_satisfacao['qnt'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts()).fillna(0).astype(int)
        tickets_satisfacao['percentage'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)

    elif sector == "Conectividade":
        tickets_satisfacao_aux = tickets_satisfacao_aux[tickets_satisfacao_aux['group'] == "Conectividade"]
        
        tickets_satisfacao['qnt'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts()).fillna(0).astype(int)
        tickets_satisfacao['percentage'] = tickets_satisfacao.index.map(tickets_satisfacao_aux[score_column].value_counts(normalize=True) * 100).fillna(0).astype(float)

    return tickets_satisfacao



def get_data(tab="app_1"):
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
    tickets = get_data_from_last_four_months()
    tickets = clean_data(tickets)

    if tab == "app_1":
        tickets_estados, abertos_mes_atual, fechados_mes_atual, total_fechados, acumulados = get_by_state(tickets)
        tickets_leadtime_setores, tickets_leadtime_unidades, tickets_leadtime_scatter = get_leadtime(tickets)
        tickets_portal_semana, tickets_telefone_semana = get_by_week(tickets)
        tickets_horas = get_by_hour(tickets)
        tickets_satisfacao = get_satisfaction(tickets)

        return {'total-fechados': total_fechados,
            'df-satisfacao': tickets_satisfacao,
            'df-estados': tickets_estados,
            'abertos-mes-atual': abertos_mes_atual,
            'fechados-mes-atual': fechados_mes_atual,
            'acumulados': acumulados,
            'df-leadtime-setores': tickets_leadtime_setores,
            'df-leadtime-unidades': tickets_leadtime_unidades,
            'df-leadtime-scatter': tickets_leadtime_scatter,
            'df-portal-semana': tickets_portal_semana,
            'df-telefone-semana': tickets_telefone_semana,
            'df-horas': tickets_horas,
        }

    # getting data by sector of STD

    elif tab == "app_2":
    # conectividade
        tickets_estados_conectividade, abertos_mes_atual_conectividade, fechados_mes_atual_conectividade, \
            total_fechados_conectividade, acumulados_conectividade = get_by_state(tickets, "Conectividade")
    
        tickets_leadtime_conectividade_bar, tickets_leadtime_conectividade_scatter = get_leadtime(tickets, "Conectividade")
        tickets_satisfacao_conectividade = get_satisfaction(tickets, "Conectividade")

        return {
            # conectividade
            'total-fechados-conectividade': total_fechados_conectividade,
            'df-estados-conectividade': tickets_estados_conectividade,
            'abertos-mes-atual-conectividade': abertos_mes_atual_conectividade,
            'fechados-mes-atual-conectividade': fechados_mes_atual_conectividade,
            'acumulados-conectividade': acumulados_conectividade,
            'df-leadtime-conectividade-bar': tickets_leadtime_conectividade_bar,
            'df-leadtime-conectividade-scatter': tickets_leadtime_conectividade_scatter,
            'df-satisfacao-conectividade': tickets_satisfacao_conectividade,
        }
    

    elif tab == "app_3":    
        # sistemas
        tickets_estados_sistemas, abertos_mes_atual_sistemas, fechados_mes_atual_sistemas, \
            total_fechados_sistemas, acumulados_sistemas = get_by_state(tickets, "Sistemas")

        tickets_leadtime_sistemas_bar, tickets_leadtime_sistemas_scatter = get_leadtime(tickets, "Sistemas")
        tickets_satisfacao_sistemas = get_satisfaction(tickets, "Sistemas")

        return {
            # sistemas
            'total-fechados-sistemas': total_fechados_sistemas,
            'df-estados-sistemas': tickets_estados_sistemas,
            'abertos-mes-atual-sistemas': abertos_mes_atual_sistemas,
            'fechados-mes-atual-sistemas': fechados_mes_atual_sistemas,
            'acumulados-sistemas': acumulados_sistemas,
            'df-leadtime-sistemas-bar':tickets_leadtime_sistemas_bar,
            'df-leadtime-sistemas-scatter':tickets_leadtime_sistemas_scatter,
            'df-satisfacao-sistemas': tickets_satisfacao_sistemas,
        }

    elif tab == "app_4":
        # servicos
        tickets_estados_servicos, abertos_mes_atual_servicos, fechados_mes_atual_servicos, \
            total_fechados_servicos, acumulados_servicos = get_by_state(tickets, "Serviços Computacionais")

        tickets_leadtime_servicos_bar, tickets_leadtime_servicos_scatter = get_leadtime(tickets, "Serviços Computacionais")
        tickets_satisfacao_servicos = get_satisfaction(tickets, "Serviços Computacionais")

        return {
            # Serviços Computacionais
            'total-fechados-servicos': total_fechados_servicos,
            'df-estados-servicos': tickets_estados_servicos,
            'abertos-mes-atual-servicos': abertos_mes_atual_servicos,
            'fechados-mes-atual-servicos': fechados_mes_atual_servicos,
            'acumulados-servicos': acumulados_servicos,
            'df-leadtime-servicos-bar':tickets_leadtime_servicos_bar,
            'df-leadtime-servicos-scatter':tickets_leadtime_servicos_scatter,
            'df-satisfacao-servicos': tickets_satisfacao_servicos,
        }
    
    elif tab == "app_5":
        # micro
        tickets_estados_micro, abertos_mes_atual_micro, fechados_mes_atual_micro, \
            total_fechados_micro, acumulados_micro = get_by_state(tickets, "Micro Informática")
        
        tickets_leadtime_micro_bar, tickets_leadtime_micro_scatter = get_leadtime(tickets, "Micro Informática")
        tickets_satisfacao_micro = get_satisfaction(tickets, "Micro Informática")

        return {
            # Micro Informática
            'total-fechados-micro': total_fechados_micro,
            'df-estados-micro': tickets_estados_micro,
            'abertos-mes-atual-micro': abertos_mes_atual_micro,
            'fechados-mes-atual-micro': fechados_mes_atual_micro,
            'acumulados-micro': acumulados_micro,
            'df-leadtime-micro-bar':tickets_leadtime_micro_bar,
            'df-leadtime-micro-scatter':tickets_leadtime_micro_scatter,
            'df-satisfacao-micro': tickets_satisfacao_micro,
        }

    elif tab == "app_6":
        # suporte
        tickets_estados_suporte, abertos_mes_atual_suporte, fechados_mes_atual_suporte, \
            total_fechados_suporte, acumulados_suporte = get_by_state(tickets, "Suporte ao Usuário")
        
        tickets_leadtime_suporte_bar, tickets_leadtime_suporte_scatter = get_leadtime(tickets, "Suporte ao Usuário")
        tickets_satisfacao_suporte = get_satisfaction(tickets, "Suporte ao Usuário")

        tickets_leadtime_setores, tickets_leadtime_unidades, tickets_leadtime_scatter = get_leadtime(tickets)
        tickets_portal_semana, tickets_telefone_semana = get_by_week(tickets)

        tickets_horas = get_by_hour(tickets)
        tickets_satisfacao = get_satisfaction(tickets)

        return {
            # Suporte ao Usuário
            'total-fechados-suporte': total_fechados_suporte,
            'df-estados-suporte': tickets_estados_suporte,
            'abertos-mes-atual-suporte': abertos_mes_atual_suporte,
            'fechados-mes-atual-suporte': fechados_mes_atual_suporte,
            'acumulados-suporte': acumulados_suporte,
            'df-leadtime-suporte-bar':tickets_leadtime_suporte_bar,
            'df-leadtime-suporte-scatter':tickets_leadtime_suporte_scatter,
            'df-satisfacao-suporte': tickets_satisfacao_suporte,
            'df-leadtime-setores': tickets_leadtime_setores,
            'df-portal-semana':tickets_portal_semana,
            'df-telefone-semana':tickets_telefone_semana,
            'df-horas':tickets_horas,
        }
