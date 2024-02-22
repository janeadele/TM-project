import psycopg2
from psycopg2.extras import RealDictCursor
from config import config
import json
from datetime import datetime
import pandas as pd


def db_create_entry(startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName, customerName):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()
        SQL = '''INSERT INTO hours (startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName, customerName) 
                 VALUES (%s,%s,%s,%s,%s,%s);'''
        add_data = (startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName, customerName)
        cursor.execute(SQL, add_data)
        con.commit()
        result = {"success": "created a new entry"}
        cursor.close()
        return json.dumps(result)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    return x


def db_update_balances(startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName):
    con = None

    #calculate hours
    hours = 0

    start = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
    lstart = datetime.strptime(lunchBreakStart, "%Y-%m-%d %H:%M:%S")
    lend = datetime.strptime(lunchBreakEnd, "%Y-%m-%d %H:%M:%S")
    lunch = lend-lstart
    hours = end-start-lunch

    hours = hours.total_seconds() / 3600

    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()
        #check if employee in the database
        employee = False
        SQL = "SELECT * FROM balance WHERE consultantname =%s;"
        add_data = (consultantName,)
        cursor.execute(SQL, add_data)
        rows = cursor.fetchall()
        print(rows)
        if rows:
            employee = True


        if employee:
            SQL = "UPDATE balance SET hour_balance = hour_balance + %s WHERE consultantname = %s;"

            add_data = (hours, consultantName)
            cursor.execute(SQL, add_data)
            con.commit()
            result = {"success": "updated balances"}
            cursor.close()
            return json.dumps(result)
        
        else:
            SQL = "INSERT INTO balance (consultantName, hour_balance) VALUES (%s,%s);"
            add_data = (consultantName, hours)
            cursor.execute(SQL, add_data)
            con.commit()
            result = {"success": "updated balances"}
            cursor.close()
            return json.dumps(result)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


def db_get_all():
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()
        SQL = 'SELECT * FROM hours;'
        cursor.execute(SQL)

        rows = cursor.fetchall()

        columns = [col[0] for col in cursor.description]

        data = [dict(zip(columns, row)) for row in rows]
        data = {item['id']: item for item in data}

        cursor.close()
        json_data = json.dumps({"entry_list": data}, default=datetime_handler)        
        return json_data
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()


if __name__ == '__main__':
    pass