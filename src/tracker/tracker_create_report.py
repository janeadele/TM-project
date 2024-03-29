
import psycopg2
from psycopg2.extras import RealDictCursor
from config import config
import json
from datetime import datetime
import pandas as pd

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    return x

# Azure Key Vault details
key_vault_url = "https://timetrackerproject.vault.azure.net/"
secret_name = "timedatabase"
# Connect to Azure Key Vault and retrieve the secret
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)
conn_str = client.get_secret(secret_name).value


# Parse the connection string
conn_params = dict(item.split('=') for item in conn_str.split(';') if item)

# The `Username` field from the connection string contains the user and the server name in some cases
# We need to extract only the username part for the DSN
username = conn_params.get('Username').split('@')[0] if '@' in conn_params.get('Username', '') else conn_params.get('Username')

# Construct the DSN string for psycopg2
dsn = f"dbname={conn_params.get('Database')} user={username} password={conn_params.get('Password')} host={conn_params.get('Host')} port={conn_params.get('Port')} sslmode=require"




'''Create a software that reads the daily/weekly consultant time tracking from PostgreSQL database table 
and writes a report to a text file. 
This report is then uploaded to storage account as a blob for your team leader to read.
 The Scenario 1 reporting software will be run manually from commandline.This 
 report contains daily/weekly total working hours by consultant and by customer.'''

def get_all():
    con = None
    try:
        con = psycopg2.connect(dsn)
        cursor = con.cursor()
        SQL = 'SELECT * FROM hours;'
        cursor.execute(SQL)

        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        json_data = json.dumps(data, default=datetime_handler)

        return json_data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def get_balances():
    con = None
    try:
        con = psycopg2.connect(dsn)
        cursor = con.cursor()
        SQL = 'SELECT * FROM balance;'
        cursor.execute(SQL)

        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        json_data = json.dumps(data, default=datetime_handler)

        return json_data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def create_tracking_report(json_string):
    data = json.loads(json_string)
    df = pd.DataFrame(data)
    
# Select columns representing date and time
    date_time_columns = ['starttime', 'endtime', 'lunchbreakstart', 'lunchbreakend']

# Convert selected columns to datetime objects
    df[date_time_columns] = df[date_time_columns].apply(pd.to_datetime)


    df['lunchbreak'] = df['lunchbreakend']-df['lunchbreakstart']
    df['workhours'] = df['endtime'] - df['starttime']-df['lunchbreak']
    df['work_h'] = df['workhours'].dt.total_seconds() / 3600


    df['week'] = df['starttime'].dt.isocalendar().week
    
    grouped = df.groupby(['consultantname', 'customername','week'])['work_h'].sum().reset_index()

    print(grouped)
    return(grouped)


def create_cumulative_report(json_string):
    data = json.loads(json_string)
    df = pd.DataFrame(data)
    
#Select columns representing date and time
    date_time_columns = ['starttime', 'endtime', 'lunchbreakstart', 'lunchbreakend']

#Convert selected columns to datetime objects
    df[date_time_columns] = df[date_time_columns].apply(pd.to_datetime)


    df['lunchbreak'] = df['lunchbreakend']-df['lunchbreakstart']
    df['workhours'] = df['endtime'] - df['starttime']-df['lunchbreak']
    df['work_h'] = df['workhours'].dt.total_seconds() / 3600
    
  
    grouped = df.groupby(['consultantname', 'customername'])['work_h'].sum().reset_index()

    #Group by 'customername' and 'consultantname', calculate cumulative working hours
    grouped['cumulative_working_hours'] = df.groupby(['customername', 'consultantname'])['work_h'].cumsum()


    #Pivot the DataFrame to show each consultant's cumulative working hours for each customer
    pivot_df = grouped.pivot_table(index='customername', columns='consultantname', values='cumulative_working_hours', aggfunc='max')
    #Replace NaN values with zero
    pivot_df = pivot_df.fillna(0)

    #Calculate total hours for each customer
    pivot_df['total_hours'] = pivot_df.sum(axis=1)

    print(pivot_df)
    return(pivot_df)   

def create_balance_report(json_string):
    data = json.loads(json_string)
    df = pd.DataFrame(data)
    return df

def create_avghours_report(json_string):
    data = json.loads(json_string)
    df = pd.DataFrame(data)
    
#Select columns representing date and time
    date_time_columns = ['starttime', 'endtime', 'lunchbreakstart', 'lunchbreakend']

#Convert selected columns to datetime objects
    df[date_time_columns] = df[date_time_columns].apply(pd.to_datetime)


    df['lunchbreak'] = df['lunchbreakend']-df['lunchbreakstart']
    df['workhours'] = df['endtime'] - df['starttime']-df['lunchbreak']
    df['work_h'] = df['workhours'].dt.total_seconds() / 3600

    #Extract the day from the start_time
    df['day'] = df['starttime'].dt.date

    #Group by consultant and day, calculate the total hours worked each day
    total_hours_per_day = df.groupby(['consultantname', 'day'])['work_h'].sum().reset_index()

    #Group by consultant, calculate the average hours worked across all days
    avg_hours_per_person = total_hours_per_day.groupby('consultantname')['work_h'].mean().round(1).to_frame(name='daily_avg_hours').reset_index()

    print(avg_hours_per_person)
    return(avg_hours_per_person)


data = get_all()
data2 = get_balances()
report4 = create_balance_report(data2)
report1 = create_tracking_report(data)
report2 = create_cumulative_report(data)
report3 = create_avghours_report(data)


def write_to_txt_file(*args):
    #Open the file in write mode ('w')
    with open('report.txt', 'w') as file:
        #Write each text variable to the file
        file.write("CONSULTANT HOURS REPORT"+ '\n')
        for report in args:
            file.write(report + 2*'\n')
            file.write("-----------------------------------------------------------------------------------------------"+ '\n')


#Create variables for tables and their titles and write them to a txt file
report1_title = "Consultant hours per week and per project:"
report2_title = "Total consultant hours per project:"
report3_title = "Consultant average daily hours:"
report4_title = "Consultant hour balances:"
report1_string = report1.to_string(index=False)
report2_string = report2.to_string(index=True)
report3_string = report3.to_string(index=False)
report4_string = report4.to_string(index = False)

write_to_txt_file(report1_title, report1_string, report2_title, report2_string, report3_title, report3_string, report4_title, report4_string)