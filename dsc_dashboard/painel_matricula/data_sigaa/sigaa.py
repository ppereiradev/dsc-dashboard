import psycopg2
import pandas as pd

''' PostgreSQL - SIGAA '''
class ConsultaSIGAA:
    
    query = '''SELECT sm.id_discente, 
               CONCAT ( 
                    min(date_part('year', sm.data_solicitacao)), 
                    '-', min(date_part('month', sm.data_solicitacao)), 
                    '-', min(date_part('day', sm.data_solicitacao)), 
                    ' ', min(date_part('hour', sm.data_solicitacao)), 
                    ':', min(date_part('minute', sm.data_solicitacao)), 
                    ':', min(date_part('second', sm.data_solicitacao)) 
                ) as DATA_SOLICITACAO 
                FROM graduacao.solicitacao_matricula sm 
                INNER JOIN discente d 
                ON sm.id_discente  = d.id_discente 
                WHERE sm.data_solicitacao > '2022-10-25' 
                AND sm.data_solicitacao < '2022-10-28' 
                GROUP BY sm.id_discente 
                ORDER BY DATA_SOLICITACAO;'''

    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
    

    def search(self):
        df = pd.DataFrame()
        
        try:
            conn = psycopg2.connect(host=self.host,database=self.database,user=self.user,password=self.password)
            cur = conn.cursor()
        except Exception as e:
            print("Error to connect to Postgres:", e)
        
        try:
            cur.execute(self.query)
            df = pd.DataFrame(cur.fetchall()) 
        except:
            print("Can't SELECT from SIGAA")

        return df

    def get_matriculas(self):
        matriculas = self.search()
        matriculas.columns = ['id','data']
        matriculas['data'] = pd.to_datetime(matriculas['data'], format='%Y-%m-%d %H:%M:%S.%f')
    
        matriculas = matriculas.groupby([pd.Grouper(key='data',freq='H'),'id']).size().reset_index(name='count_id')
        matriculas = matriculas.groupby(['data','count_id']).size().reset_index(name='quantidade')
        
        return matriculas
        
