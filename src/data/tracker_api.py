from flask import Flask, request
from tracker_service import db_get_all, db_create_entry, db_update_balances

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
        db_update_balances(startTime, endTime, lunchBreakStart, lunchBreakEnd, consultantName)
        return {"success": "created a new entry:"}
    except:
        return {"error": "error creating entry"}
    
if __name__ == "__main__":
    app.run(debug = True)

