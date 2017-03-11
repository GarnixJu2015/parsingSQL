# db that stores everything
from parseSQL import *
class Database:
    def __init__(self):
        self.tables = []
  
    def exec_sql(self, sql):
        #Call string parsing
        input_text(sql)
      
    def can_create(name, col_name, col_datatypes, col_constraints):
        """The fucntion to check whether the type or constraint is valid for table creation
        Args:
            name (String): The table name.
            col_name ([String]): The column names.
            col_datatypes ([String]): The column data types.
            col_constraints ([int]): The constraint value for each column.
        Returns:
            bool: The return value. True for valid, False otherwise.
        """
        # Check that all three list have the same length
        if not len(col_name) == len(col_datatype) == len(col_constraints):
            return False
          
        # Check that the DB doesn't contain more then 10 tables already
        if len(self.tables) >= 10:
            return False
        
        # Check that the column data types are either varchar or int
        for dtype in col_datatypes:
            if dtype not in Datatype.str2dt:
                return False
            
        # Check that the column constraints are < 40 for varchar
        for dtype, cons in zip(datatype, constraints):
            if Datatype.str2dt[dtype] == Datatype.VARCHAR and len(cons) > 40:
                return False
        
        return True
    
    
    # Create up to 10 individual tables
    def create_table(self, table_name, col_names, col_datatypes, col_constraints, keys=None):
        """The fucntion to create a new table. It will check if the given parameter is valid. 
        Args:
            table_name (String): The table name.
            col_names ([String]): The column names.
            col_datatypes ([String]): The column data types.
            col_constraints ([int]): The constraint value for each column.
            keys ([Bool]): To indicate if the column is primary key.
        Returns:
            bool: The return value. True for successful creation, False otherwise.
            * maybe some error message?
        """
        if can_create(table_name, col_names, col_datatypes, col_constraints):
            columns = []
            for cname, dtype, cons, key in zip(col_names, col_datatypes, col_constraints, keys):
                columns.append(Column(cname, Datatype.str2dt[dtype], cons, key))
            table = Table(table_name, columns)
            self.tables.append(table)

    
    def get_all_table_names(self):
        return [t.name for t in self.tables]
  
    def get_table(self, name):
        for t in self.tables:
            if t.name == name:
                return t
        return None
  
class Datatype():
    INT = 1
    VARCHAR = 2
    # mapping string to datatype
    str2dt = {'int':INT, 'varchar':VARCHAR}
    
# each table
class Table:
    def __init__(self, name, columns):
        """The init fucntion of Table. It assumes that all columns are valid. 
        Args:
            name (String): The table name.
            columns ([Column]): The Column objects .
        
        Todo: May need to create hidden column for non-pk table.
        """
        self.name = name
        self.columns = columns
        # data structure for entity may need to change 
        self.entities = []
        # dictionary for fast look up from col_name to its order in the table
        self.col_name2id = {}
        for i, c in enumerate(columns):
            self.col_name2id[c.name] = i
       
    def insert(self, values, col_names=None):
        """The fucntion inserts a row into the table. It will check if the given parameter is valid. 
        Args:
            values ([int || String]): The value to insert.
            col_names ([String] || None): The column names. If this value is None, we will use default sequence.
        Returns:
            bool: The return value. True for successful insertion, False otherwise.
        
        Todo:
            maybe some error message?
            insert entity
        """
        # check if the col_name is in column
        # and convert the whole list to their order in the table
        col_ids = []
        for n in col_names:
            if n not in self.col_name2id:
                return False
            else:
                # convert col_name to its order in the table and append to list
                col_ids.append(self.col_name2id[n])
        
        # create Entitiy
        if col_names:
            entity = Entity(values, col_ids)
        else:
            entity = Entity(values)
      
        # validate entity
        if not entity_is_valid(entity):
            return False
        
        # insert entity
        pass
  
    def delete(self, entity):
        pass
  
    def entity_is_vaild(self, entity):
        """The fucntion checks if the entity is fine to insert into the table.
        Args:
            entity (Entity): The entity we want to test.
        Returns:
            bool: The return value. True for valid, False otherwise.
        
        Test:
            Check if column values are valid
            Check for null value
            Check that there are no keys with the same value
        
        Todo:
            Check for null value
            We know we can't have empty value for primary key
            But can we have empty value for non-primary-key column?
            If so, we only have to check for those pk columns.
            
        """
        # Check if column values are valid
        for v, c in zip(entity.values, self.columns):
            if not c.is_valid(v):
                return False
        
        ''' NOT SURE IF WE CAN HAVE MISSING VALUE '''
        # Check for null value
        
        
        # Check that there are no keys with the same value
        # Get all order id that the corresponding column is marked as primary key
        key_id = []
        for i, c in enumerate(self.column):
            key_id.append((i,c))
        
        # Get all value that the corresponding column is marked as primary key
        entity_key_values = [v for (v, c) in zip(entity.values, self.columns) if c.key]
        
        # Go through all entities, and check there are no same primary key
        # Can speed up by better Data Structure
        for e in self.entities:
            # Extract key column values of every entities, and compare with the one we want to test
            # If there's same combination, we say this entity is invalid
            if entity_key_values == [e[i] for i in key_id]:
                return False
            
        # Pass all validation 
        return True
  
    # Getting data for specific key
    def fetch(self, column_name):
        pass

class Column:
    def __init__(self, name, datatype, constraint_val, key):
        """The fucntion to create a column. It assumes that all parameter are valid. 
        Args:
            name (String): The column name.
            datatype (int): The column data types id, transformed by str2dt.
            constraint_val (int): The constraint value for each column.
            key (Bool): To indicate if the column is a primary key.
        """
        self.name = name
        # defines which type of data the column should accept
        self.datatype = datatype
        # Defines boundaries for the data
        # Create Constraint object
        if datatype == Datatype.INT:
            self.constraint = IntConstraint()
        elif datatype == Datatype.VARCHAR:
            self.constraint = VarcharConstraint(constraint_val)
        # Sets bool whether a column contains a key
        self.key = key
    
# each row
class Entity:
    def __init__(self, values):
        """The init fucntion to create an Entity. It assumes that all parameter are valid. 
        Args:
            values ([String|int]): The value for the corresponding column.
        """
        self.values = values
        
    def __init__(self, values, col_id):
        """The init fucntion to create an Entity. It assumes that all parameter are valid. 
        The order of the values in the Entity is sorted by col_id.
        Args:
            values ([String|int]): The value for the corresponding column.
            col_id ([int]): The order of the corresponding value.
        """
        for cid, v in zip(col_id, values):
            self.values[cid] = v

class IntConstraint:
    def __init__(self):
        pass
    
    @staticmethod
    def is_valid(value):
        # Check that value is an int within -2,147,483,648 to 2,147,483,647
        return isInstance(value, int) and value >= -2147483648 and value <= 2147483647

class VarcharConstraint:
    def __init__(self, max_len):
        """The init fucntion to create a VarcharConstraint. It assumes that max_len <= 40. 
        Args:
            max_len (int): The maximum length of a varchar.
        """
        self.max_len = max_len
        pass
    
    def is_valid(value):
        # Check that value is a string within char limit 40
        return isInstance(value, basestring) and len(value) <= max_len

"""
Temporary functions that insert fake data into views
Data visualization -- retrieve data only
"""
def get_all_table_names(database):
    table_names = ['Round Table','Square table','Triangle Table']
    return table_names

def get_table(table_name, database):
    title = ['title1','title2']
    content = [['row1 content1','row1 content2'],['row2 content1','row2 content2']]
    return title, content