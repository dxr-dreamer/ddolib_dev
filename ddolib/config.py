# config.py
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._storage_url = "sqlite:///test101_database.db"  # 默认使用内存数据库
        return cls._instance

    @property
    def storage_url(self):
        return self._storage_url

    @storage_url.setter
    def storage_url(self, value):
        self._storage_url = value
