from flask import Flask, request
from tracker_service import db_get_all, db_create_entry

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return {"index": True}

@app.route('/hours', methods=['GET'])
def get_all():
    try:  
        return db_get_all()
    except:
        return {"error": "no data"}



@app.route("/hours", methods=['POST'])
def create_person():
    try: 
        data = request.get_json()
        startTime = data['startTime']
        endTime = data['endTime']
        lunchBreakStart = data['lunchBreakStart']
        lunchBreakEnd = data['lunchBreakEnd']
        consultantName = data['consultantName']
        customerName = data ['customerName']
        db_create_entry(startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName, customerName)
        return {"success": "created a new entry:"}
    except:
        return {"error": "error creating entry"}
    
if __name__ == "__main__":
    app.run(debug = True)

'''
@app.route("/person/<int:id>", methods=['PUT'])
def update_person(id):
    try:
        data = request.get_json()
        username = data['name']
        age = data['age']
        student = data['student']
        db_update_person(id, username, age, student)
        return {"success": "updated person"}
    except:
        return {"error": "error updating person"}

@app.route('/person/<int:id>', methods=['DELETE'])
def delete_person(id):
    try:
        return db_delete_person(id)
    except:
        return {"error": "no such person"}
    
@app.route('/person/<int:id>', methods=['GET'])
def get_person_by_id(id):
    try:
        return db_get_person_by_id(id)
    except:
        return {"error": "no person with id %s" % id}
        '''