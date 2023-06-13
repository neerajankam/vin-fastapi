import os


HERE = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "vins_database.db"
DATABASE_PATH = os.path.join(HERE, "..", "data")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}/{DATABASE_NAME}"
