
import psycopg2
from psycopg2.extras import RealDictCursor
from config import config
import json
from datetime import datetime
import pandas as pd

# from ..data.tracker_service import db_get_all

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    return x

'''Create a software that reads the daily/weekly consultant time tracking from PostgreSQL database table 
and writes a report to a text file. 
This report is then uploaded to storage account as a blob for your team leader to read.
 The Scenario 1 reporting software will be run manually from commandline.This 
 report contains daily/weekly total working hours by consultant and by customer.'''

def get_all():
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()
        SQL = 'SELECT * FROM hours;'
        cursor.execute(SQL)

        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        #data = {item['id']: item for item in data}
        cursor.close()
        json_data = json.dumps(data, default=datetime_handler)

        return json_data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
#startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName, customerName) 
def create_report(json_string):
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
    
    print(df)
    grouped = df.groupby(['consultantname', 'customername','week'])['work_h'].sum().reset_index()
    print(grouped)
    return(grouped)


#create a file named 'report.txt' to the tracker folder
def write_file(text):
    as_string = text.to_string(index=False)
    with open('report.txt', 'w') as file:
        file.write(as_string)

data = get_all()
report = create_report(data)
write_file(report)