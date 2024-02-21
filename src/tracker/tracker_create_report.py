
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
    
    #print(df[['endtime', 'week']])
    grouped = df.groupby(['consultantname', 'customername','week'])['work_h'].sum().reset_index()

    print(grouped)
    return(grouped)


def create_cumulative_report(json_string):
    data = json.loads(json_string)
    df = pd.DataFrame(data)
    
# Select columns representing date and time
    date_time_columns = ['starttime', 'endtime', 'lunchbreakstart', 'lunchbreakend']

# Convert selected columns to datetime objects
    df[date_time_columns] = df[date_time_columns].apply(pd.to_datetime)


    df['lunchbreak'] = df['lunchbreakend']-df['lunchbreakstart']
    df['workhours'] = df['endtime'] - df['starttime']-df['lunchbreak']
    df['work_h'] = df['workhours'].dt.total_seconds() / 3600
    
    #print(df[['endtime', 'week']])
    grouped = df.groupby(['consultantname', 'customername'])['work_h'].sum().reset_index()

    # Group by 'customer' and 'consultant', calculate cumulative working hours
    grouped['cumulative_working_hours'] = df.groupby(['customername', 'consultantname'])['work_h'].cumsum()


    # Pivot the DataFrame to show each consultant's cumulative working hours for each customer
    pivot_df = grouped.pivot_table(index='customername', columns='consultantname', values='cumulative_working_hours', aggfunc='max')
    # Replace NaN values with zero
    pivot_df = pivot_df.fillna(0)

    #Calculate total hours for each customer
    pivot_df['total_hours'] = pivot_df.sum(axis=1)

    print(pivot_df)
    return(pivot_df)   


def create_avghours_report(json_string):
    data = json.loads(json_string)
    df = pd.DataFrame(data)
    
# Select columns representing date and time
    date_time_columns = ['starttime', 'endtime', 'lunchbreakstart', 'lunchbreakend']

# Convert selected columns to datetime objects
    df[date_time_columns] = df[date_time_columns].apply(pd.to_datetime)


    df['lunchbreak'] = df['lunchbreakend']-df['lunchbreakstart']
    df['workhours'] = df['endtime'] - df['starttime']-df['lunchbreak']
    df['work_h'] = df['workhours'].dt.total_seconds() / 3600

    # Extract the day from the start_time
    df['day'] = df['starttime'].dt.date

    # Group by consultant and day, calculate the total hours worked each day
    total_hours_per_day = df.groupby(['consultantname', 'day'])['work_h'].sum().reset_index()

    # Group by consultant, calculate the average hours worked across all days
    avg_hours_per_person = total_hours_per_day.groupby('consultantname')['work_h'].mean().round(1)

    print(avg_hours_per_person)
    return(avg_hours_per_person)

'''#create a file named 'report.txt' to the tracker folder
def write_file(text):
    as_string = text.to_string(index=False)
    with open('report.txt', 'w') as file:
        file.write(as_string)'''

data = get_all()
report = create_tracking_report(data)
report2 = create_cumulative_report(data)
report3 = create_avghours_report(data)
#print(report)
#write_file(report)

def write_to_txt_file(*args):
    # Open the file in write mode ('w')
    with open('report1.txt', 'w') as file:
        # Write each text variable to the file
        for report in args:
            file.write(report + 2*'\n')  # You may want to add a newline character

# Example usage:
report1_string = report.to_string(index=False)
report2_string = report2.to_string(index=True)
report3_string = report3.to_string(index=True)

write_to_txt_file(report1_string, report2_string, report3_string)