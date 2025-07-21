# USDT transactions data pipeline
## Project Summary
This project applied Apache Airflow to build and orchestrate an ETL data pipeline for storing USDT transaction data into a PostgreSQL database. The Airflow data pipeline runs in docker containers and can be monitored on the Airflow User Interface. The pipeline is customisable - which allows you to size up the data consumption per batch, to get other ERC-20 token transaction data, etc., based on use cases.

Below is a graphical representation of the data pipeline showing on Airflow UI:

![Screenshot 2023-04-04 at 22 46 15](https://user-images.githubusercontent.com/83192718/229945022-b966028e-7d41-4b63-bae6-a55ce9237367.png)

## Running Instructions
1. Start your docker engine, then open up terminal in your directory and run command `docker-compose up airflow-init`
2. After seeing message like : 'airflow-init successfully exited with code 0', run the command `docker-compose up`, and keep this terminal open. You should see your docker app showing the containers running:

<img width="1061" alt="Screenshot 2023-04-04 at 20 09 12" src="https://user-images.githubusercontent.com/83192718/229945066-d54dc99b-8b80-4e0b-b86a-ff1bfa545e52.png">

3. Create a PostgreSQL database in your docker postgreSQL environment (you can do this by using database administration tools such as DBeaver, for this project, the database name is 'erc20'). The username and password of the user/owner of this database should be 'airflow' by default.
4. Establish the connection by going Airflow UI, select 'Admin' > 'Connections' > '+'. Then, fill in the following details:
    - Connection Id (In our case, it is 'erc20_conn'. You can edit your connection id from the scripts)
    - Connection Type: Postgres
    - Host: localhost or host.docker.internal
    - Schema: erc20 (same as the database name and variable 'schema' in the scripts)
    - Username: airflow (default)
    - Password: airflow (default)
    - Port: 5432
    - Description
5. Validate the connection by clicking on 'Test connection'
6. Go to the 'DAGs' section in the Airflow UI and check if the pipeline is running successfully.
7. Check the data is successfully uploaded in your PostgreSQL database table

![Screenshot 2023-04-04 at 22 47 12](https://user-images.githubusercontent.com/83192718/229945119-ed448536-c018-4390-a490-86497bbe5d2c.png)

To terminate the process, simply go back to the terminal and run `docker-compose down`, this will shut down and remove all the docker containers running for this project.

Note: The docker-compose.yaml file from this directory is fetched from the [apache airflow official website](https://airflow.apache.org/docs/apache-airflow/2.5.3/howto/docker-compose/index.html) with slight modifications - adding the ports into postgres service and switch off the load examples function. You can modify the other parameters such as '_AIRFLOW_WWW_USER_USERNAME', '_AIRFLOW_WWW_USER_PASSWORD', etc., based on your needs. You can also build your own docker-compose.yaml file and Dockerfile using images from [Docker Hub](https://hub.docker.com/)

**Reminder: Please input your own EtherScan API key in dags/utils.py, line 9**

### Pre-requisites
- Airflow Python packages
- EtherScan API key
- PostgreSQL database
- Docker (Warning for mac users: by default docker will have a memory of 3.9GB, which is not sufficient for the airflow image creation process - 4GB memory required. I did adjusted my memory usage on the docker app ('settings' > 'Resources' > 'Advanced') but this is not recommended for low memory macs and contains risks for crashing your host machine.)
