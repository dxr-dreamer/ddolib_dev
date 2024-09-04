import uuid
import dill
import os,json,time
import logging
from sqlalchemy import create_engine, update,MetaData, Table, Column, String, LargeBinary, JSON, text
from sqlalchemy.sql import insert
import hashlib

class DigitalObject:
    """
    Base class representing a Digital Object (DO).

    Attributes:
    data (any): The main content of the digital object.
    metadata (dict): Metadata associated with the digital object.
    doid (str): System-internal unique identifier for the digital object.
    doid (str): External unique identifier for the digital object, assigned by a registration service.
    """
    def __init__(self, data, metadata, doid=None):
        """
        Initializes a DigitalObject.

        Parameters:
        data (any): The main content of the digital object.
        metadata (dict): Metadata associated with the digital object.
        doid (str, optional): External unique identifier for the digital object, assigned by a registration service.
        """
        self._data = data
        self._metadata = metadata
        self._doid = doid

    def __str__(self):
        """
        Returns a string representation of the digital object.

        Returns:
        str: String representation of the digital object.
        """
        data_str = self._safe_str(self.data)
        metadata_str = self._safe_str(self.metadata, json_format=True)
        return f"DigitalObject(data={data_str}, metadata={metadata_str}, doid={self.doid}, doid={self.doid})"

    def __repr__(self):
        """
        Returns a string representation of the digital object for debugging.

        Returns:
        str: Debugging string representation of the digital object.
        """
        data_str = self._safe_str(self.data)
        metadata_str = self._safe_str(self.metadata, json_format=True)
        return f"DigitalObject(data={data_str}, metadata={metadata_str},doid={self.doid})"

    def _safe_str(self, obj, max_length=50, json_format=False):
        """
        Returns a safe string representation of an object, truncating if necessary.

        Parameters:
        obj (any): The object to convert to a string.
        max_length (int, optional): The maximum length of the string representation.
        json_format (bool, optional): Whether to format the object as a JSON string.

        Returns:
        str: A safe string representation of the object.
        """
        try:
            if json_format:
                obj_str = json.dumps(obj)
            else:
                obj_str = str(obj)
            if len(obj_str) > max_length:
                return obj_str[:max_length] + "..."
            return obj_str
        except Exception as e:
            return f"<unprintable object: {e}>"

    def get_doid(self,IRS):
        if self.doid:
            logging.error(f"The do already has a doid {self.doid}.")
            return False
        gdoid = IRS.generate(self.data)
        if gdoid:
            self._doid = gdoid
        else:
            logging.error(f"IRS returns null.")
            return False
        return True
    
    @property
    def data(self):
        """
        Returns the data of the digital object.

        Returns:
        any: The data of the digital object.
        """
        return self._data

    @property
    def metadata(self):
        """
        Returns the metadata of the digital object.

        Returns:
        dict: The metadata of the digital object.
        """
        return self._metadata

    @property
    def doid(self):
        """
        Returns the external identifier of the digital object.

        Returns:
        str: The external identifier of the digital object.
        """
        return self._doid
    

class DigitalObjectRepository:
    def __init__(self, url=None):  
        self.repo_db_url = url 

    #retrieve
    def load(self, doid, url=None):
        db_url = url or self.repo_db_url
        logging.debug(f"Loading DigitalObject with doid={doid} from {db_url}")
        if db_url.startswith("sqlite://") or db_url.startswith("mysql://"):
            engine = create_engine(db_url)
            with engine.connect() as connection:
                try:
                    result = connection.execute(text("SELECT data, metadata FROM digital_objects WHERE doid = :doid"), {"doid": doid})  
                    row = result.fetchone()  
                    if row:  
                        loaded_object_data = dill.loads(row[0])  
                        metadata = json.loads(row[1]) if isinstance(row[1], str) else row[1]  
                        #   row[0] is data,row[1] is metadata.
                        return DigitalObject( 
                            data=loaded_object_data,  
                            metadata=metadata,  
                            doid=doid  
                        ) 
                    else:
                        logging.error(f"Can't find doid {doid} in repository.")
                        return False
                except Exception as e:  
                    logging.error(f"Failed to load DigitalObject from database: {e}")
                    return False
        else: #未调整
            filename = os.path.join(db_url, f"{doid}.dill")
            with open(filename, 'rb') as file:
                loaded_object = dill.load(file)
                return DigitalObject(
                    data=loaded_object.data,
                    metadata=loaded_object.metadata,
                    doid=loaded_object.doid
                )

    #create
    def save(self,do,url=None):
        db_url = url or self.repo_db_url
        if do.doid is None:
            logging.debug(f"Doid is needed for create new do in repository.")
            return False
        logging.debug(f"Saving DigitalObject with doid={do.doid} to {db_url}")
        if db_url.startswith("sqlite://") or db_url.startswith("mysql://"):
            try:
                engine = create_engine(db_url)
                with engine.connect() as connection:
                    serialized_data = dill.dumps(do.data)
                    logging.debug(f"Serialized data: {serialized_data[:50]}...")  # 输出序列化数据的前50个字符
                    
                    metadata = MetaData()
                    digital_objects_table = Table(
                                                    'digital_objects', metadata,
                                                    Column('doid', String, primary_key=True),
                                                    Column('data', LargeBinary),
                                                    Column('metadata', JSON))
                    
                    # 确保表结构已存在
                    metadata.create_all(engine)
                    
                    # 构建插入语句
                    stmt = insert(digital_objects_table).values(doid=do.doid, data=serialized_data, metadata=do.metadata)
                    result = connection.execute(stmt)
                    connection.commit()  # 提交事务
                    logging.debug(f"Rows affected: {result.rowcount}")
                    logging.debug(f"DigitalObject with doid={do.doid} saved to database.")
            except Exception as e:
                logging.error(f"Failed to save DigitalObject to database: {e}")
            return True
        else:
            return False
         
    def update(self, doid, newdo, url=None):  
        db_url = url or self.repo_db_url 
        logging.debug(f"Updating DigitalObject with doid={doid} in {db_url}")  
        if db_url.startswith("sqlite://") or db_url.startswith("mysql://"):  
            try:  
                engine = create_engine(db_url)  
                with engine.connect() as connection:  
                    # 序列化新数据  
                    serialized_data = dill.dumps(newdo.data)  
                    logging.debug(f"Serialized data: {serialized_data[:50]}...")  # 输出序列化数据的前50个字符
                    # 假设 new_metadata 已经是 JSON 格式，如果不是，则需要先转换为 JSON  
                       
                    metadata = MetaData()  
                    digital_objects_table = Table(  
                        'digital_objects', metadata,  
                        Column('doid', String, primary_key=True),  
                        Column('data', LargeBinary),  
                        Column('metadata', JSON)  
                    )  
                      
                    # 构建更新语句  
                    stmt = update(digital_objects_table).where(digital_objects_table.c.doid == doid).values(  
                        data=serialized_data,  
                        metadata=newdo.metadata  
                    )  
                    result = connection.execute(stmt)  
                    connection.commit()  # 提交事务  
                    logging.debug(f"Rows updated: {result.rowcount}")  
                    if result.rowcount == 0:  
                        logging.warning(f"No rows were updated for doid={doid}.")
                        return False  
                    else:  
                        logging.debug(f"DigitalObject with doid={doid} updated in database.")  
                        return True 
            except Exception as e:  
                logging.error(f"Failed to update DigitalObject in database: {e}")  
                return False   
        else:
            return False
      
    def retrieve(self, doid, url=None):  
        """  
        Retrieves a DigitalObject by its doid.  
  
        This is a wrapper around the load method for clarity.  
        """  
        return self.load(doid, url) 
     
    def create(self, do, url=None):  
        """  
        Create a DigitalObject by its doid and data.  
  
        This is a wrapper around the save method for clarity.  
        """  
        return self.save(do, url) 
     
    def delete(self, doid, url=None):  
        db_url = url or self.repo_db_url
        logging.debug(f"Deleting DigitalObject with doid={doid} from {db_url}")  
  
        if db_url.startswith("sqlite://") or db_url.startswith("mysql://"):  
            try:  
                engine = create_engine(db_url)  
                with engine.connect() as connection:  
                    # 构造SQL删除语句  
                    stmt = text("DELETE FROM digital_objects WHERE doid = :doid")  
                    result = connection.execute(stmt, {"doid": doid})  
  
                    # 提交事务  
                    connection.commit()  
  
                    logging.debug(f"Rows affected: {result.rowcount}")  
                    if result.rowcount == 0:  
                        logging.warning(f"No DigitalObject with doid={doid} found in the database.")  
                        return False
                    else:  
                        logging.debug(f"DigitalObject with doid={doid} deleted from database.")  
                        return True
  
            except Exception as e:  
                logging.error(f"Failed to delete DigitalObject from database: {e}") 
                return False
        else:
            return False 
  
# 待修改
class Relationship:
    """
    Class representing a Relationship between DOs.

    Attributes:
    from_ddo_doids (list of str): The originating data object identifiers.
    to_ddo_doids (list of str): The target data object identifiers.
    metadata (dict): Metadata associated with the relationship, including description.
    """
    def __init__(self, from_ddo_doids, to_ddo_doids, metadata, url=None):
        """
        Initializes a Relationship.

        Parameters:
        from_ddo_doids (list of str): The originating data object identifiers.
        to_ddo_doids (list of str): The target data object identifiers.
        metadata (dict): Metadata associated with the relationship.
        """
        self._from_ddo_doids = from_ddo_doids
        self._to_ddo_doids = to_ddo_doids
        self._metadata = metadata
        self._doid = self._generate_internal_id()
        self.save(url)

    @property
    def from_ddo_doids(self):
        return self._from_ddo_doids

    @property
    def to_ddo_doids(self):
        return self._to_ddo_doids

    @property
    def metadata(self):
        return self._metadata

    @property
    def doid(self):
        return self._doid

    def _generate_internal_id(self):
        return str(uuid.uuid4())
    
    def save(self, url=None):
        db_url = url 
        logging.debug(f"Saving Relationship with doid={self.doid} to {db_url}")
        if db_url.startswith("sqlite://") or db_url.startswith("mysql://"):
            engine = create_engine(db_url)
            with engine.connect() as connection:
                metadata = MetaData()
                relationships_table = Table(
                                                'relationships', metadata,
                                                Column('doid', String, primary_key=True),
                                                Column('from_ddo_doids', JSON),
                                                Column('to_ddo_doids', JSON),
                                                Column('metadata', JSON))
                metadata.create_all(engine)
                stmt = insert(relationships_table).values(doid=self.doid, from_ddo_doids=self.from_ddo_doids, to_ddo_doids=self.to_ddo_doids, metadata=self.metadata)
                connection.execute(stmt)
                connection.commit()
                logging.debug(f"Relationship with doid={self.doid} saved to database.")
        else:
            if not os.path.exists(db_url):
                os.makedirs(db_url)
            filename = os.path.join(db_url, f"{self.doid}.dill")
            with open(filename, 'wb') as file:
                dill.dump(self, file)
            logging.debug(f"Relationship with doid={self.doid} saved to file {filename}.")
        return True

    def __repr__(self):
        """
        Returns a string representation of the relationship for debugging.

        Returns:
        str: Debugging string representation of the relationship.
        """
        return f"Relationship(from_ddo_doids={self.from_ddo_doids}, to_ddo_doids={self.to_ddo_doids}, metadata={self.metadata})"


class IdentifierResolutionService:  
    def __init__(self, repository):  
        self.repository = repository

    def generate(self,data):  
        """  
        生成一个基于当前时间和数据的唯一标识符。  
  
        参数:  
            data (object): 需要生成标识符的数据对象。  
  
        返回:  
            str: 生成的唯一标识符。  
        """  
        timestamp = str(int(time.time() * 1000))   
        data_hash = hashlib.sha256(str(data).encode()).hexdigest()     
        unique_id = f"{timestamp}_{data_hash}"  
        return unique_id  
    
    def resolution(self, doid, url=None):  
        """  
        Resolves a digital object identifier (doid) to a DigitalObject instance.  
  
        Parameters:  
        doid (str): The unique identifier of the digital object.  
        url (str, optional): The URL or path to the storage location.  
  
        Returns:  
        DigitalObject: The digital object corresponding to the doid, or None if not found.  
        """  
        try:  
            return self.repository.retrieve(doid, url)  
        except Exception as e:  
            logging.error(f"Failed to resolve DigitalObject with doid={doid}: {e}")  
            return None

