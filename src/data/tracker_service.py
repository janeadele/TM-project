import psycopg2
from psycopg2.extras import RealDictCursor
from config import config
import json
from datetime import datetime


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
    raise TypeError("Unknown type")



#now_str = now.isoformat()
def db_get_all():
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor()
        SQL = 'SELECT * FROM hours;'
        cursor.execute(SQL)

        rows = cursor.fetchall()
        #print(data)

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

            '''
def db_get_persons():
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'SELECT * FROM person;'
        cursor.execute(SQL)

        data = cursor.fetchall()
        cursor.close()
        return json.dumps({"person_list": data})
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def db_get_person_by_id(id):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'SELECT * FROM person where id = %s;'
        cursor.execute(SQL, (id,))
        row = cursor.fetchone()
        cursor.close()
        return json.dumps(row)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
            


def db_update_person(id, username):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'UPDATE person SET username = %s WHERE id = %s;'
        cursor.execute(SQL, (username, id))
        con.commit()
        cursor.close()
        result = {"success": "updated person id: %s " % id}
        return json.dumps(result)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

def db_delete_person(id):
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'DELETE FROM person WHERE id = %s;'
        cursor.execute(SQL, (id,))
        con.commit()
        cursor.close()
        result = {"success": "deleted person id: %s " % id}
        return json.dumps(result)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()
'''


if __name__ == '__main__':
    #db_create_entry('2024-02-16 08:25:00', '2024-02-16 15:55:00', '2024-02-16 12:25:00', '2024-02-16 12:55:00', 'Matti', 'Valio')
    print(db_get_all())

