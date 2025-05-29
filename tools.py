import polars as pl
import json
import psycopg2
from dotenv import load_dotenv
import os

def query_banco_diario_oficial(query:str):
    '''
    Retorna os resultados de uma query SQL no banco de dados.
    Args:
        query (str): A query SQL a ser executada.
    '''
    def connect_to_db() -> psycopg2.extensions.connection:
        load_dotenv()
        try:
            conn = psycopg2.connect(
                user= os.getenv("DB_USER"),
                password= 'KC7Zr7796xT6KO',
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                dbname=os.getenv("DB_NAME")
            )
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
        return conn
    
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pl.DataFrame({col: [row[i] for row in result] for i, col in enumerate(column_names)})
            df = df.to_dict(as_series=False)
            df = json.dumps(df, default=str)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()
            conn.close()


   
    
    