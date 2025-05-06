"""
This module is used for setting up and initializing the database for ADIChain.
It creates all necessary tables including Credentials, Medics, Patients, Caregivers,
Reports, and Treatment Plans with appropriate relationships and constraints.
"""

import sqlite3

con = sqlite3.connect("SFSchain")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS Credentials")
cur.execute("DROP TABLE IF EXISTS Users")
cur.execute("DROP TABLE IF EXISTS Operations")
cur.execute("DROP TABLE IF EXISTS Reports")

cur.execute('''CREATE TABLE Credentials(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            hash_password TEXT NOT NULL,
            role TEXT CHECK(role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL
            );''')
cur.execute('''CREATE TABLE IF NOT EXISTS Users(
                    username TEXT NOT NULL,
                    name TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    birthday DATE NOT NULL,
                    user_role TEXT CHECK(role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL,
                    mail TEXT NOT NULL,
                    phone TEXT,
                    company_name TEXT,
                    carbon_credit INTEGER,
                    FOREIGN KEY(username) REFERENCES Credentials(username)
                    );''')
cur.execute('''CREATE TABLE Operations(
            id_operation INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_date DATE NOT NULL,
            username TEXT NOT NULL,
            role TEXT CHECK(role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL
            operation TEXT NOT NULL
            );''')
cur.execute('''CREATE TABLE Reports(
            id_report INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_date DATE NOT NULL
            operation_date DATE NOT NULL
            username TEXT NOT NULL,
            role TEXT CHECK(role IN ('FARMER', 'CARRIER', 'PRODUCER', 'SELLER')) NOT NULL
            operations TEXT
            );''')
con.commit()
con.close()