from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/report", methods=["GET"])
def create_report():
    try:
        # Using subprocess to run the Python script
        subprocess.run(["python", "tracker_create_report.py"], check=True)
        subprocess.run(["python", "tracker_toazure.py"], check=True)
        return {"success": True, "message": "Scripts executed successfully."}
    except subprocess.CalledProcessError as e:
        return {"success": False, "message": str(e)}


if __name__ == "__main__":
    app.run(debug = True)