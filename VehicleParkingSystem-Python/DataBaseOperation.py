import sqlite3
import json
from datetime import datetime

class DBOperation():

    def __init__(self):
        file = open("./config.json", "r")
        datadic = json.loads(file.read())
        file.close()
        # Use SQLite connection, specifying the database file
        self.mydb = sqlite3.connect(datadic['database'])  # Use the database file (e.g., "parking_system.db")

    def CreateTables(self):
        cursor = self.mydb.cursor()
        cursor.execute("DROP TABLE IF EXISTS admin")
        cursor.execute("DROP TABLE IF EXISTS slots")
        cursor.execute("DROP TABLE IF EXISTS vehicles")
        cursor.execute("CREATE TABLE admin (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, created_at TEXT)")
        cursor.execute("CREATE TABLE slots (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT, space_for INTEGER, is_empty INTEGER)")
        cursor.execute("CREATE TABLE vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, mobile TEXT, entry_time TEXT, exit_time TEXT, is_exit TEXT, vehicle_no TEXT, vehicle_type TEXT, created_at TEXT, updated_at TEXT)")
        cursor.close()

    def InsertOneTimeData(self, space_for_two, space_for_four):
        cursor = self.mydb.cursor()
        for x in range(space_for_two):
            cursor.execute("INSERT INTO slots (space_for, is_empty) VALUES ('2', '1')")
            self.mydb.commit()

        for x in range(space_for_four):
            cursor.execute("INSERT INTO slots (space_for, is_empty) VALUES ('4', '1')")
            self.mydb.commit()
        cursor.close()

    def InsertAdmin(self, username, password):
        cursor = self.mydb.cursor()
        val = (username, password)
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", val)
        self.mydb.commit()
        cursor.close()

    def doAdminLogin(self, username, password):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        data = cursor.fetchall()
        cursor.close()
        return len(data) > 0

    def getSlotSpace(self):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM slots")
        data = cursor.fetchall()
        cursor.close()
        return data

    def getCurrentVehicle(self):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE is_exit='0'")
        data = cursor.fetchall()
        cursor.close()
        return data

    def getAllVehicle(self):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE is_exit='1'")
        data = cursor.fetchall()
        cursor.close()
        return data

    def AddVehicles(self, name, vehicleno, mobile, vehicle_type):
        spacid = self.spaceAvailable(vehicle_type)
        if spacid:
            currentdata = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = (name, mobile, str(currentdata), '', '0', vehicleno, str(currentdata), str(currentdata), vehicle_type)
            cursor = self.mydb.cursor()
            cursor.execute("INSERT INTO vehicles (name, mobile, entry_time, exit_time, is_exit, vehicle_no, created_at, updated_at, vehicle_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            self.mydb.commit()
            lastid = cursor.lastrowid
            cursor.execute("UPDATE slots SET vehicle_id=?, is_empty='0' WHERE id=?", (lastid, spacid))
            self.mydb.commit()
            cursor.close()
            return True
        else:
            return "No Space Available for Parking"

    def spaceAvailable(self, v_type):
        cursor = self.mydb.cursor()
        cursor.execute("SELECT * FROM slots WHERE is_empty='1' AND space_for=?", (v_type,))
        data = cursor.fetchall()
        cursor.close()
        return data[0][0] if data else False

    def exitVehicle(self, id):
        cursor = self.mydb.cursor()
        currentdata = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE slots SET is_empty='1', vehicle_id='' WHERE vehicle_id=?", (id,))
        self.mydb.commit()
        cursor.execute("UPDATE vehicles SET is_exit='1', exit_time=? WHERE id=?", (currentdata, id))
        self.mydb.commit()
