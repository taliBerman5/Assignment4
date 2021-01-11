import sqlite3
import DTO
from DAO import Dao
import atexit


class _Repository:
    def __init__(self):
        self._conn = sqlite3.connect('database.db')
        self.vaccines = Dao(DTO.Vaccine, self._conn)
        self.suppliers = Dao(DTO.Supplier, self._conn)
        self.clinics = Dao(DTO.Clinic, self._conn)
        self.logistics = Dao(DTO.Logistic, self._conn)

    def _close(self):
        self._conn.commit()
        self._conn.close()

    def createTables(self):
        self._conn.executesscript("""
        CREATE TABLE vaccines (
            id          INTEGER     PRIMARY KEY
            date        DATE        NOT NULL
            supplier    INTEGER     REFERENCES Supplier(id)
            quantity    INTEGER     NOT NULL
            ); 
            
        CREATE TABLE suppliers (
            id          INTEGER     PRIMARY KEY
            name        STRING      NOT NULL
            logistic    INTEGER     REFERENCES Logistic(id)
            );
            
        CREATE TABLE logistics (
            id          INTEGER     PRIMARY KEY
            location    STRING      NOT NULL
            demand      INTEGER     NOT NULL
            logistic    INTEGER     REFERENCES Logistic(id)
            );
            
        CREATE TABLE logistics (
            id              INTEGER     PRIMARY KEY
            name            STRING      NOT NULL
            count_sent      INTEGER     NOT NULL
            count_received  INTEGER     NOT NULL
            );
        """)
    def getSummary(self):
        c = self._conn.cursor()
        inv = c.execute("""
                SELECT sum(quantity) 
                FROM vaccines 
        """).fetchone()

        demand = c.execute(""" 
                SELECT sum(demand)
                FROM clinics
        """).fetchone()

        rec_sent = c.execute("""
                SELECT sum(count_received), sum(count_sent)
                FROM logistics
        """).fetchone()

        return inv[0] + ',' + demand[0] + ',' + rec_sent[0] + ',' + rec_sent[1]



repo = _Repository()
atexit.register(repo._close)
