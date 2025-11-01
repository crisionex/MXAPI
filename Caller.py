#importing libraries
from dotenv import dotenv_values
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

#Importing Secret Keys
dotenv_path = Path('Data.env')
SecretData = dotenv_values(dotenv_path=dotenv_path)

#Setting credentials and initial connection
def ConnectingDB():
    conn = psycopg2.connect(database=SecretData["DATABASE"],
                            host =SecretData["HOST"],
                            user=SecretData["USER"],
                            password=SecretData["PASSWORD"],
                            port=SecretData["PORT"])
    return conn

#Creating connection to Postgressql
def CreateConnection(conn):
    return conn.cursor(cursor_factory=RealDictCursor)