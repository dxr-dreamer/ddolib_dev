import json
import matplotlib.pyplot as plt
import networkx as nx
from sqlalchemy import create_engine, MetaData, Table, Column, String, LargeBinary, JSON, text
from sqlalchemy.orm import sessionmaker
from .config import Config
from .core import DigitalObjectRepository,IdentifierResolutionService
import sqlite3
from matplotlib.lines import Line2D
from adjustText import adjust_text
import dill

class StorageManager:
    def __init__(self):
        self.config = Config()
        self.engine = create_engine(self.config.storage_url)
        self.metadata = MetaData()
        self.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.do_repo = DigitalObjectRepository(self.config.storage_url)
        self.irs = IdentifierResolutionService(self.do_repo)

    # 不可用，待修改
    def update_storage_url(self, new_url=None):
        self.config.db_url = new_url or self.config.storage_url
        self.engine = create_engine(self.config.db_url)
        self.metadata.bind = self.engine
        self.Session.configure(bind=self.engine)
        self.session = self.Session()
        self.do_repo = DigitalObjectRepository(self.config.storage_url)
        self.irs = IdentifierResolutionService(self.do_repo)

    def view_database(self):
        conn = sqlite3.connect(self.config.db_url.replace('sqlite:///', ''))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])
        
        cursor.execute("SELECT * FROM digital_objects;")
        rows = cursor.fetchall()
        print("\nContents of the digital_objects table:")
        for row in rows:
            print(row)

        cursor.execute("SELECT * FROM relationships;")
        rows = cursor.fetchall()
        print("\nContents of the relationships table:")
        for row in rows:
            print(row)
        
        conn.close()
    
storage_manager = StorageManager()