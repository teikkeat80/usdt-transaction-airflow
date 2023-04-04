from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
import utils

# Define airflow DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Create DAG
dag = DAG(
    'ERC20-airflow-dag',
    default_args=default_args,
    description='Retrieve ERC-20 token transaction data and Write to PostgreSQL database',
    schedule_interval=timedelta(minutes=10)
)

# Task 1 - SQL CREATE TABLE & SCHEMA query using PostgresOperator
task1 = PostgresOperator(
    task_id='create_table',
    postgres_conn_id='erc20_conn',
    sql='''
        CREATE SCHEMA IF NOT EXISTS erc20;

        CREATE TABLE IF NOT EXISTS erc20.erc20_transactions (
            id SERIAL PRIMARY KEY,
            blockNumber TEXT,
            timeStamp TEXT,
            hash TEXT,
            nonce TEXT,
            blockHash TEXT,
            fromAddress TEXT,
            contractAddress TEXT,
            toAddress TEXT,
            value TEXT,
            tokenName TEXT,
            tokenSymbol TEXT,
            tokenDecimal TEXT,
            transactionIndex TEXT,
            gas TEXT,
            gasPrice TEXT,
            gasUsed TEXT,
            cumulativeGasUsed TEXT,
            input TEXT,
            confirmations TEXT
        );
    ''',
    dag=dag,
)

# Task 2 - Read EtherScan API data using PythonOperator
task2 = PythonOperator(
    task_id='read_data',
    python_callable=utils.get_token_data,
    dag=dag,
)

# Task 3 - Run data transformation process using PythonOperator
task3 = PythonOperator(
    task_id='transform_data',
    python_callable=utils.transform_token_data,
    dag=dag,
)

# Task 4 - Load data into the PostgreSQL table created in Task 1 using PythonOperator
task4 = PythonOperator(
    task_id='load_data',
    python_callable=utils.write_token_data_postgresql,
    provide_context=True,
    dag=dag,
)

# Define task flow
task1 >> task2 >> task3 >> task4