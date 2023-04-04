import requests
import pandas as pd
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Get USDT (or other ERC-20 token) transaction data from EtherScan API
def get_token_data(**kwargs):

    api_key = 'your_API_key' # INPUT your EtherScan API key
    contract_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'  # USDT (Replace with desired ERC-20 token)

    url = 'https://api.etherscan.io/api'
    params = {
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': contract_address,
        'sort': 'desc',  # Sort transactions (most recent for 'desc')
        'offset': 1,  # Set number of records get from page (maximum = 10000)
        'page': 1,  # Set page number (most recent page)
        'apikey': api_key
    }

    # Get data in JSON format
    response = requests.get(url, params=params)
    json_data = response.json()

    kwargs['ti'].xcom_push(key='json_data', value=json_data) # Using XCom to pass data into next task

# Working on simple data transformation processes
def transform_token_data(**kwargs):

    json_data = kwargs['ti'].xcom_pull(key='json_data') # Using XCom to pull data from previous task

    # Pass data into a list for transformation
    data_list = json_data['result']
    for data in data_list:
        data['value'] = float(data['value'])/10**6 # Get USDT value
        # Get timestamp into desired format
        data['timeStamp'] = datetime \
            .fromtimestamp(int(data['timeStamp'])) \
            .strftime('%Y-%m-%dT%H:%M:%S')

    # Pass data into a df for transformation - rename PostgreSQL reserved keywords
    df = pd.DataFrame(data_list)
    df = df.rename(columns={'from': 'fromAddress'})
    df = df.rename(columns={'to': 'toAddress'})

    df_json = df.to_json(orient='records') # Pass data back to JSON form to enable serialisation
    
    kwargs['ti'].xcom_push(key='df', value=df_json) # Using XCom to pass data into next task

# Write data into PostgreSQL database
def write_token_data_postgresql(**kwargs):

    # Pull serialised data and pass it back into a df
    df_json = kwargs['ti'].xcom_pull(key='df')
    df = pd.read_json(df_json, orient='records')

    col_names = tuple(df.columns)

    # Define PostgreSQL connection properties
    pg_conn_id = 'erc20_conn'
    table = 'erc20_transactions'
    schema = 'erc20'

    # SQL INSERT query
    insert_query = 'INSERT INTO {}.{} ({}) VALUES ({})'.format(
        schema,
        table,
        ', '.join(map(str, col_names)),
        ', '.join(['%s'] * len(col_names))
    )

    # Commit the INSERT query into PostgreSQL database
    pg_hook = PostgresHook(postgres_conn_id=pg_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    values = [tuple(x) for x in df.values]

    cursor.executemany(insert_query, values)

    conn.commit()
    cursor.close()
    conn.close()