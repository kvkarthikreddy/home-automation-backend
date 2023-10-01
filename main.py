from flask import *
import psycopg2

app = Flask(__name__)
from flask_cors import CORS

conn = psycopg2.connect("postgres://kjtxgayq:urkFQwxMUks3YpOmCXlsBmHj0Y-eob-_@peanut.db.elephantsql.com/kjtxgayq")

CORS(app)

@app.route("/create-device", methods=["POST"])
def createDevice():
    # Retrieve the POST data
    data = request.get_json()

    if data is None:
        return make_response("Invalid JSON data", 400)

    try:
        # Extract data from the JSON
        deviceType = data.get("deviceType")
        deviceName = data.get("deviceName")
        pinNo = data.get("pinNo")
        isDeviceOn = data.get("isDeviceOn")



        # Create a cursor object
        cur = conn.cursor()

        # Insert data into the "manoj" table without specifying deviceId
        sql = "INSERT INTO IOT (deviceType, deviceName, pinNo, isDeviceOn) VALUES (%s, %s, %s, %s) RETURNING deviceId"
        cur.execute(sql, (deviceType, deviceName, pinNo, isDeviceOn))

        # Fetch the generated deviceId
        generated_device_id = cur.fetchone()[0]

        # Commit the transaction and close the database connection
        conn.commit()


        return make_response(f"Device with deviceId {generated_device_id} successfully created", 200)
    except Exception as e:
        return make_response(str(e), 500)
@app.route("/toggle-switch", methods=["POST"])
def toggleSwitch():
    try:
        # Retrieve the deviceId from the POST data
        data = request.get_json()
        device_id = data.get("deviceId")


        cur = conn.cursor()

        # Fetch the current state of the device from the database
        sql = "SELECT isDeviceOn::Boolean FROM IOT WHERE deviceId = %s"
        cur.execute(sql, (device_id,))
        current_state = cur.fetchone()

        if current_state is not None:
            print(current_state)
            current_state = current_state[0]
            if not current_state:
                new_state = "True"
            else:
                new_state = "False"



            # Update the device's state in the database
            sql = "UPDATE IOT SET isDeviceOn = %s WHERE deviceId = %s"
            cur.execute(sql, (new_state, device_id))

            # Commit the transaction and close the database connection
            conn.commit()


            # Return the updated state as a JSON response
            return jsonify({"message": "Switch toggled successfully", "deviceId": device_id, "isDeviceOn": new_state})
        else:
            return jsonify({"error": "Device not found"}), 404

    except Exception as e:
        # Handle errors here, such as logging or sending an error message
        return jsonify({"error": str(e)}), 500

@app.route("/devices", methods=["GET"])
def getDevices():
    try:
        # Create a cursor object
        cur = conn.cursor()

        # Execute a query to retrieve all devices and their data
        sql = "SELECT deviceType, deviceName, pinNo, deviceId::text, isDeviceOn::Boolean FROM IOT ORDER BY deviceId"
        cur.execute(sql)

        # Fetch all rows as a list of dictionaries
        devices_data = []
        columns = ["deviceType", "deviceName", "pinNo", "deviceId", "isDeviceOn"]
        # columns = [desc[0] for desc in cur.description]
        for row in cur.fetchall():
            device = dict(zip(columns, row))
            devices_data.append(device)



        # Return the list of devices as an HTTP response
        return jsonify(devices_data)
    except Exception as e:
        # Handle errors here, such as logging or sending an error message
        return jsonify({"error": str(e)}), 500
@app.route("/delete-device", methods=["DELETE"])
def delete_device():
    data = request.json
    device_id = data.get("deviceId")

    if not device_id:
        return jsonify({"message": "Invalid input data"}), 400


    with conn.cursor() as cur:
        cur.execute("DELETE FROM IOT WHERE deviceId = %s", (device_id,))
        conn.commit()
        return make_response("Device deleted successfully",200)




if __name__ == '__main__':
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS IOT (deviceId serial PRIMARY KEY, deviceType varchar,deviceName varchar, pinNo varchar, isDeviceOn varchar);")
    conn.commit()
    cur.close()
    app.run()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
