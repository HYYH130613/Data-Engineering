from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import sqlite3

def extract(url, table_attribs):
    
    html_page = requests.get(url).text
    data = BeautifulSoup(html_page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[2].find_all('tr')

    data_list = []   
    count = 0

    for row in rows:
        if count >= 110:   
            break

        col = row.find_all('td')
        
        if len(col) >= 3:
            
            data_dict = {
                "Country": col[0].get_text(strip=True),
                "GDPs in million USDs": col[2].get_text(strip=True)
            }
            data_list.append(data_dict)
            count += 1

    
    df = pd.DataFrame(data_list, columns=table_attribs)

    return df
    

def transform(df):
    
    df = df.copy()

    def safe_to_float(x):
        try:
            if pd.isna(x):
                return float("nan")
            x = str(x)
            x = x.replace(",", "").replace(" ", "").replace("$", "")
            return float(x)
        except Exception:
            return float("nan")

    df["GDPs in million USDs"] = df["GDPs in million USDs"].apply(safe_to_float)
    df['GDPs in million USDs'] = df['GDPs in billion USDs'].apply(lambda x: x/1000).round(2)

    return df

def load_to_csv(df, csv_path):
    
    df.to_csv(csv_path)


def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)
    
def run_query(query_statement, sql_connection):
    
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)
    
def log_progress(message):
    
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    with open("./etl_project_log.txt","a") as f: 
        f.write(timestamp + ' : ' + message + '\n')
    
    
url = 'https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
table_attribs = ["Country","GDPs in million USDs"]
csv_path = 'D:\Test_Projects\python_data_eng\coursera_projects'

table_name = 'Countries_by_GDP'

log_progress('Preliminaries complete. Initiating ETL process')
df = extract(url, table_attribs)
log_progress('Data extraction complete. Initiating Transformation process')
df = transform(df)
log_progress('Data transformation complete. Initiating loading process')
load_to_csv(df, csv_path)
log_progress('Data saved to CSV file')
sql_connection = sqlite3.connect('World_Economies.db')
log_progress('SQL Connection initiated.')
load_to_db(df, sql_connection, table_name)
log_progress('Data loaded to Database as table. Running the query')
query_statement = f"SELECT * from {table_name} WHERE GDP_USD_billions >= 100"
run_query(query_statement, sql_connection)
log_progress('Process Complete.')
sql_connection.close()
