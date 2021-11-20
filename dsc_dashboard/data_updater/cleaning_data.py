import pandas as pd
import os
from datetime import datetime, timedelta

from .mongo_utils import count_tickets, get_many_tickets
from .data_zammad import all_tickets
import calendar

def weekday_count(start, end):
    start_date = datetime.strptime(start, '%d/%m/%Y')
    end_date = datetime.strptime(end, '%d/%m/%Y')
    week = {}
    for i in range((end_date - start_date).days):
        day = calendar.day_name[(start_date + timedelta(days=i+1)).weekday()]
        week[day] = week[day] + 1 if day in week else 1
    return week

def cleaning_data():
    
    ###############################################  LOADING DATAFRAMES #############################################

    ##################################################################################################################
    ##################################################################################################################
    ##########                                                                                              ##########
    ##########                                          TICKETS                                             ##########
    ##########                                                                                              ##########
    ##################################################################################################################
    ##################################################################################################################

    # pegando somente os tickets dos últimos 4 meses
    df_tickets = get_many_tickets({ "$or": [ {"created_at":{"$gte": (datetime.now() - timedelta(days=120)) }},
                                             {"close_at":{"$gte": (datetime.now() - timedelta(days=120)) }} ]})
    
    ###################################### consertando os dados ##################################################
    df_tickets['created_at'] = df_tickets['created_at'].map(lambda x: x if x != "null" else None)
    df_tickets['close_at'] = df_tickets['close_at'].map(lambda x: x if x != "null" else None)
    df_tickets['updated_at'] = df_tickets['updated_at'].map(lambda x: x if x != "null" else None)
    
    df_tickets['created_at'] = pd.to_datetime(df_tickets['created_at'])
    df_tickets['close_at'] = pd.to_datetime(df_tickets['close_at'])
    df_tickets['updated_at'] = pd.to_datetime(df_tickets['updated_at'])

    estados = {"closed":"Fechado",
                  "open":"Aberto",
                  "resolvido":"Resolvido",
                  "new":"Novo",
                  "aguardando resposta":"Aguardando Resposta",
                  "pendente":"Pendente",
                  "retorno":"Retorno",
                  }

    df_tickets['state'] = df_tickets['state'].map(estados)


    mes_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio",  6: "Junho",  7: "Julho",  8: "Agosto",  9: "Setembro",  10: "Outubro", 11: "Novembro",  12: "Dezembro"}
    date_list = pd.period_range(pd.Timestamp.now().to_period('m')-3, freq='M', periods=4).strftime('%Y-%m-%d').tolist()

    ############################### ABERTOS ##################################
    df_abertos = df_tickets.copy()
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
    
    ############################### FECHADOS ##################################
    df_fechados = df_tickets.copy()
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
    total_fechados = df_fechados['qnt'].sum()
    
    ########################### ACUMULADOS ######################
    df_acumulados = df_abertos.copy()
    
    abertos_antigos = count_tickets({ "created_at": { "$lte":  (datetime.strptime(date_list[0] + " 23:59:59", '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)) } })
    fechados_antigos = count_tickets({ "close_at": { "$lte":  (datetime.strptime(date_list[0] + " 23:59:59", '%Y-%m-%d %H:%M:%S').replace(day=1) - timedelta(days=1)) } })
    
    df_acumulados.iloc[0, 0] += abertos_antigos - (df_fechados.iloc[0, 0] + fechados_antigos)

    for i in range(1, len(date_list)):
        df_acumulados.iloc[i, 0] += df_acumulados.iloc[i - 1, 0] - df_fechados.iloc[i, 0]

    acumulados = df_acumulados['qnt'][-1]


    ''' DF COMPLETO DOS ESTADOS '''
    df_estados = pd.merge(df_abertos,df_fechados, on='mes/ano',how='inner')
    df_estados = pd.merge(df_estados,df_acumulados, on='mes/ano',how='inner')
    df_estados.columns = ['abertos', 'fechados', 'acumulados']    
    #################################################################

    ################################# LEADTIME #################################################
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
    
    """ 
    map_setores = {"SIG@": "CSIS",
               "SIGAA": "CSIS",
               "SIPAC": "CSIS",
               "SIGRH": "CSIS",
               "Sistemas Diversos": "CSIS",
               "Web Sites": "CSIS",
               "Triagem": "CSUP",
               "Serviços Computacionais": "CSC",
               "Micro Informática": "CMI",
               "Conectividade": "CCON",
               "CODAI": "CODAI",
               "UABJ": "UABJ",
               "UAST": "UAST",
               "UACSA": "UACSA",
               "UAEADTec": "UAEADTec"
               }
    """

    df_leadtime['group'] = df_leadtime['group'].map(map_setores)
    
    df_leadtime = df_leadtime[df_leadtime['state'] == 'Fechado']
    df_leadtime = df_leadtime[['state', 'group', 'created_at', 'close_at']]
    
    df_leadtime['diff'] = df_leadtime['close_at'] - df_leadtime['created_at']
    df_leadtime['diff'] = df_leadtime['diff'].astype('timedelta64[h]')
    
    df_leadtime_aux = pd.DataFrame(columns=['mes/ano', 'group', 'diff'])
    for i in range(0, len(df_leadtime['diff'])):
        df_leadtime_aux.loc[i] = [df_leadtime['created_at'].iloc[i].date().strftime('%y-%m'), df_leadtime['group'].iloc[i], df_leadtime['diff'].iloc[i]]

    df_leadtime_aux = df_leadtime_aux.groupby(['mes/ano', 'group']).mean().reset_index()
    df_leadtime_aux['diff'] = df_leadtime_aux['diff']/24
    df_leadtime_aux['diff'] = df_leadtime_aux['diff'].astype(int)
    

    setores_list = ["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade","CODAI","UABJ","UAST","UACSA","UAEADTec"]
    #setores_list = ["CSIS","CSUP","CSC","CMI","CCON","CODAI","UABJ","UAST","UACSA","UAEADTec"]

    for mes in df_leadtime_aux['mes/ano']:
        for setor in setores_list:
            if setor not in df_leadtime_aux[(df_leadtime_aux['mes/ano'] == mes)]['group'].to_list():
                df_leadtime_aux = df_leadtime_aux.append({"mes/ano": mes, "group": setor, "diff": 0}, ignore_index=True)
        
    df_leadtime_aux = df_leadtime_aux.sort_values(by='mes/ano').reset_index(drop=True)

    df_leadtime_setores = df_leadtime_aux.loc[df_leadtime_aux['group'].isin(["Sistemas","Suporte ao Usuário","Serviços Computacionais","Micro Informática","Conectividade"])]
    #df_leadtime_setores = df_leadtime_aux.loc[df_leadtime_aux['group'].isin(["CSIS","CSUP","CSC","CMI","CCON"])]
    df_leadtime_unidades = df_leadtime_aux.loc[df_leadtime_aux['group'].isin(["CODAI","UABJ","UAST","UACSA","UAEADTec"])]

    df_leadtime_setores = df_leadtime_setores.pivot_table('diff', 'mes/ano', 'group')
    df_leadtime_unidades = df_leadtime_unidades.pivot_table('diff', 'mes/ano', 'group')

    df_leadtime_setores = df_leadtime_setores.reset_index(level=[0])
    df_leadtime_unidades = df_leadtime_unidades.reset_index(level=[0])
    df_leadtime_setores['mes/ano'] = df_leadtime_setores['mes/ano'].apply(lambda x: mes_map[int(x.split('-')[1])] + '/' + x.split('-')[0])
    df_leadtime_unidades['mes/ano'] = df_leadtime_unidades['mes/ano'].apply(lambda x: mes_map[int(x.split('-')[1])] + '/' + x.split('-')[0])

    ################################# END LEADTIME #################################################

    ######################## QUANTIDADE CHAMADOS ABERTOS DIA DA SEMANA ##############################################
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
    
    ########### calculating the mean tickets opened last 30 days ################################
    '''
    frenquecy_days = weekday_count(df_semana['criado'].min().strftime('%d/%m/%Y'), df_semana['criado'].max().strftime('%d/%m/%Y'))
    for day in frenquecy_days.keys():
        try:
            df_portal_semana.loc[df_portal_semana['dia'] == day, 'media'] = int(df_portal_semana.loc[df_portal_semana['dia'] == day, 'media'].iloc[0]/frenquecy_days[day])
        except Exception as e:
            continue

    for day in frenquecy_days.keys():
        try:
            df_telefone_semana.loc[df_telefone_semana['dia'] == day, 'media'] = int(df_telefone_semana.loc[df_telefone_semana['dia'] == day, 'media'].iloc[0]/frenquecy_days[day])
        except Exception as e:
            continue
    '''    
    
    df_portal_semana['dia'] = df_portal_semana['dia'].map(day_translation)
    df_telefone_semana['dia'] = df_telefone_semana['dia'].map(day_translation)
    
    ######################## END QUANTIDADE CHAMADOS ABERTOS DIA DA SEMANA ##############################################

    ######################## QUANTIDADE CHAMADOS ABERTOS HORA DO DIA ##############################################
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
    ######################## END QUANTIDADE CHAMADOS ABERTOS HORA DO DIA ##############################################


    ##################################################################################################################
    ##################################################################################################################
    ##########                                                                                              ##########
    ##########                                     GOOGLE FORMS                                             ##########
    ##########                                                                                              ##########
    ##################################################################################################################
    ##################################################################################################################

    ##################################### GOOGLE FORMS ######################################################
    url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}/gviz/tq?tqx=out:csv&sheet={os.getenv('GOOGLE_SHEET_NAME')}"
    df_aux = pd.read_csv(url)
    df_aux.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    df_aux = df_aux.drop_duplicates(subset='h', keep="last")

    df_satisfacao = pd.DataFrame(None, index =[0,1,2,3,4,5,6,7,8,9,10], columns =['qnt'])
    df_satisfacao['qnt'] = df_satisfacao.index.map(df_aux['b'].value_counts()).fillna(0).astype(int)
    df_satisfacao['percentage'] = df_satisfacao.index.map(df_aux['b'].value_counts(normalize=True) * 100).fillna(0).astype(float)
    ##################################### END GOOGLE FORMS ######################################################


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
            }
