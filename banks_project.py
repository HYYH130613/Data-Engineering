import pandas as pd
from bs4 import BeautifulSoup
import requests
import sqlite3
import numpy as np
from datetime import datetime


def log_progress(message):
    
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    timestamp = datetime.now().strftime(timestamp_format) 
    
    with open("./code_log.txt","a") as f: 
        f.write(timestamp + ' : ' + message + '\n')
    
def extract(url, table_attribs):
    
    html_page = requests.get(url).text
    data = BeautifulSoup(html_page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')
    
    data_list = []

    for row in rows:
        col = row.find_all('td')
        if len(col)!=0:
            if col[1].find('a') is not None and '—' not in col[2]:
                x = col[2].get_text(strip=True)
                try:
                    if pd.isna(x):
                        x = float("nan")
                    x = str(x)
                    x = x.replace(",", "").replace(" ", "").replace("\n", "")
                    x = float(x)
                except Exception:
                    x = float("nan")
            
                data_dict = {
                    "BankName": col[1].get_text(strip=True),
                    "Market Cap": x
                }
                data_list.append(data_dict)

    
    df = pd.DataFrame(data_list, columns=table_attribs)
    return df

def transform(df, csv_path):
    
    df.rename(columns={"Market Cap": "MC_USD_Billion"}, inplace=True)
    
    exchange_df = pd.read_csv(csv_path)
    exchange_rate = exchange_df.set_index('Currency').to_dict()['Rate']
    
    df['MC_GBP_Billion'] = [np.round(x*exchange_rate['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x*exchange_rate['EUR'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x*exchange_rate['INR'],2) for x in df['MC_USD_Billion']]
    
    return df

def load_to_csv(df, output_path):
    df.to_csv(output_path)
    
def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)    
    
def run_query(query_statement, sql_connection):
    
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)



url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["BankName","Market Cap"]
csv_path = 'D:\Test_Projects\python_data_eng\coursera_projects\exchange_rate.csv'
output_path = 'D:\Test_Projects\python_data_eng\coursera_projects\load_to.csv'

table_name = 'Largest_banks'

log_progress('Preliminaries complete. Initiating ETL process')
df = extract(url, table_attribs)
# print(df.head())
log_progress('Data extraction complete. Initiating Transformation process')
df = transform(df, csv_path)
# print(df.head())
# print(df['MC_EUR_Billion'][4])
log_progress('Data transformation complete. Initiating loading process')
load_to_csv(df, output_path)
log_progress('Data saved to CSV file')

log_progress('Data saved to CSV file')
sql_connection = sqlite3.connect('Banks.db')
log_progress('SQL Connection initiated.')
load_to_db(df, sql_connection, table_name)
log_progress('Data loaded to Database as table. Running the query')

query_statement1 = f"SELECT * from {table_name}"
query_statement2 = f"SELECT AVG(MC_GBP_Billion) FROM {table_name}"
query_statement3 = f"SELECT BankName from {table_name} LIMIT 5"
run_query(query_statement1, sql_connection)
run_query(query_statement2, sql_connection)
run_query(query_statement3, sql_connection)
log_progress('Process Complete.')
sql_connection.close()