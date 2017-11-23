# Author: Ben de Vries
# Contact: bldevries.science@gmail.com
# Web: www.stjerke.com
# Github: https://github.com/bldevries

import 	sys
import 	os
import numpy as np
import warnings
import sqlite3 as lite
import io
from pprint import pprint


# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# CLASS OpticalConstants
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------

class SQLData(object):
	"""
	This class is used, by inheriting it, by objects that need to be saved to an SQLite database.
	This class implements two instance methods to store and retrieve data (save and search). 

	INSTRUCTIONS:
	1) Inherit this class
	2) Implement a constructor:
		def __init__(self, SQLITE_DB_FILE_PATH, ...):

			#self.SQLITE_DB_FILE_PATH = "name.db"

			# Call the constructor of the SQLData class
			super(<yourclassname>, self).__init__(SQLITE_DB_FILE_PATH)

			# Declare the variables you want saved in the DB
			self.variable_1_to_store_in_db = None # or some value
			self.variable_2_to_store_in_db = None 
			...

			# Give default values for the variables that are stored. These will determine how the types
			# are saved in the SQLite DB
			self.default_variable_values.update({	"variable_1_to_store_in_db": "", \
													"variable_2_to_store_in_db": "", \
													...
									})

			# If you use global variables that you do not want to save in the DB, add them here
			self.exclude_variables_from_database.extend(["<list the vars you do not want to have saved in the DB>"])


	3) Note that all global variables will be stored in the sqlite database
	4) The SQLITE_DB_FILE_PATH must be pased to the super.__init__
	5) default_variable_values contains defaults that will be given to the variables if they are set to None.
	6) Data types supported: numbers, chars, lists (saved as strings), numpy arrays
	7) Data types NOT supported: complex numbers
	8) If you want to use instance variables and not save them in the database, add them to this variable: exclude_variables_from_database


	"""

	# These functions are needed to save nparaays in the sqlite db
	def adapt_array(arr):
		try:
		    buffer
		except NameError:
		    buffer = bytes

		out = io.BytesIO()
		np.save(out, arr)
		out.seek(0)
		return lite.Binary(out.read())

	def convert_array(text):
	    out = io.BytesIO(text)
	    out.seek(0)
	    return np.load(out)
			    
	# Converts np.array to TEXT when inserting
	lite.register_adapter(np.ndarray, adapt_array)

	# Converts TEXT to np.array when selecting
	lite.register_converter("array", convert_array)	


	# ^^^^^^^^^^^^^^^ 
	# 
	# This initialises the ID column in the table
	#KEY_ID				= "Id"
	#NK_TABLE_KEY_COL 	= (KEY_ID, "INTEGER PRIMARY KEY")


	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def __init__(self, SQLITE_DB_FILE_PATH, exclude_variables_from_database=[]):
		self.Id = None
		self.exclude_variables_from_database = ["SQLITE_DB_FILE_PATH", "default_variable_values"]
		self.default_variable_values = {"Id": "INTEGER PRIMARY KEY"}
		self.SQLITE_DB_FILE_PATH = SQLITE_DB_FILE_PATH


	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def save(self, force_as_new_entry = False, resetTable = False):
		"""
		This function saves the current state of the model data. It does this as a new entry if the entry does
		not exist. Forcing an entry as a new entry eventhough it already exists can be done with force_as_new_entry. 
		If you want to drop the table before saving (CAREFUL!) then you can use resetTable.
		"""

		con = None
		try:
			# Make connection (dont forget the detect_types for using np arrays that you defined yourself)
			con = lite.connect(self.SQLITE_DB_FILE_PATH, detect_types=lite.PARSE_DECLTYPES)
			con.row_factory = lite.Row
			cur = con.cursor()    

			# Fetch tje column information
			table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo()

			# CREATE TABLE if it does not exist or when user request to drop the table
			if not self.tableExists(table_name) or resetTable:
				cur.execute("DROP TABLE IF EXISTS "+table_name)
				sql_q = "create table "+table_name+" ("#+self.NK_TABLE_KEY_COL[0]+" "+self.NK_TABLE_KEY_COL[1]+", "
				for i in range(len(column_names)):
					sql_q += column_names[i]+" "+column_datatypes[i]
					if i != len(column_names)-1:
						sql_q += ", "
				sql_q += ")"

				cur.execute(sql_q)
				con.commit()

			# If the ID is set, 
			if self.Id != None:
				# you search if there is an entry with that ID (if not, later on that will be treated as a new entry and the non existing id is discarded)
				nr_entries_found = self.search(set_values = False, only_by_id=True)# DIT WERKT NIET WAT WAARDES ZIJN AL VERANDERD HIERVOOR
			# If the ID is not set, see how many entries there are that are similar
			else:
				nr_entries_found = self.search(set_values = False)# DIT WERKT NIET WAT WAARDES ZIJN AL VERANDERD HIERVOOR

			# If no entries are found or user want to force a new entry, make a new entry into the DB
			if nr_entries_found == 0 or force_as_new_entry:
				table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo(with_id=False)
				sql_q = "insert into "+table_name+" ("+", ".join(column_names)+") values ("+", ".join(["?" for i in range(len(column_names))])+")"

				cur.execute(sql_q, column_values_from_model)
				con.commit()

				#print("SQLData note: made new entry: label={}".format(self.label))
			# If there is exactly one match with a row in the DB, update that row with the variables in this SQLData instance
			elif nr_entries_found == 1:
				table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo(with_id=False)

				# We do not want to update the variables that are set to the default values
				var_names_to_save, var_values_to_save = [], []
				for i in range(len(column_names)):
					if column_values_from_model[i] != self.default_variable_values[column_names[i]]:
						var_names_to_save.append(column_names[i])
						var_values_to_save.append(column_values_from_model[i])

				sql_q = "UPDATE "+table_name+\
						" SET "+", ".join( [var_names_to_save[i]+" = ?" for i in range(len(var_names_to_save))] )+\
						" WHERE Id="+str(self.Id)

				cur.execute(sql_q, var_values_to_save)
				con.commit()
				#print("SQLData note: updated the entry: label={}, Id={}".format(self.label, self.Id) )

			# If more than one entries in the DB are equal to this one, nothing is done
			else: # Multiple entries found
				print("SQLData.save: multiple entries exist already in the DB, NOT saving or updating. Please specify more variables to make a unique match")

		except lite.Error as e:
		    print("Error (save): %s" % e.args[0])
		    sys.exit(1)
		    
		finally:
		    if con:
		        con.close()

		self.search()


	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def search(self, set_values = True, only_by_id=False):
		"""
			Takes the variables that are set in the model and searches for a matching entry in the DB
			If it is found it completes the variables in the model with those found in the DB.
			It returns the amount of rows found for the given variable. You can use the parameter
			set_values=False to use this function as a checker for if the entry exists.
		"""

		nr_found = 0 # Keeps track of how many rows are found
		con = None # connection to the sqlite3
		try:
			# Fetch tje column information
			table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo(with_id=True)
			if self.tableExists(table_name):

				# Set up connection and cursor
				con = lite.connect(self.SQLITE_DB_FILE_PATH, detect_types=lite.PARSE_DECLTYPES)
				con.row_factory = lite.Row # This way you get dictionairies returned
				cur = con.cursor()    

				# Now run over the variables (=column_names) and make a search string that can be 
				# used in the sql query
				search_str = []
				if only_by_id:
					search_str.append( "Id="+str(self.Id) )
				else:
					for i in range(len(column_names)):
						variable, value, def_value = column_names[i], column_values_from_model[i], self.default_variable_values[column_names[i]]
						if not (value == None or value == def_value):
							if isinstance(value, (str, unicode)):
								if not "List:" in value:
									search_str.append( variable+"=\'"+value+"\'" )
								else:
									listOfValues = self.listToString(value, inverse=True)
									for v in listOfValues:
										search_str.append( variable+" LIKE \'%"+v+"%\'" )
							elif isinstance(value, (int, long, float, complex)):
								search_str.append( variable+"="+str(value) )

				# Format the search string and create an sql query
				search_str = " AND ".join(search_str)
				if search_str.strip() == "":
					sql_q = "SELECT * FROM "+table_name
				else:
					sql_q = "SELECT * FROM "+table_name+" WHERE "+search_str

				# Execute and fetch results
				cur.execute(sql_q)
				rows = cur.fetchall()

				nr_found = len(rows)

				# If more then 1 elements in the database correspond to the variables with which you searched
				# then a warning is given and the first row returned is used
				if nr_found > 1:
					warnings.warn("DataClass_SQLData, search(): search did not give unique results, will just use the first item in the result list")
				# If one or more rows are found, start reading in the database content to the model
				if nr_found > 0:

					if set_values:
						for column_name in rows[0].keys():
							if isinstance(rows[0][column_name], (str,unicode)): 
								content = str(rows[0][column_name])
								if "List: " in rows[0][column_name]:
									content = self.listToString(content, inverse=True)
									for c in range(len(content)):
										if content[c].strip().isdigit():
											content[c] = float(content[c])
									self.__dict__[column_name] = content
								else:
									self.__dict__[column_name] = content
							else:
								self.__dict__[column_name] = rows[0][column_name]
					else:
						self.Id = rows[0]["Id"]
			else:
				warnings.warn("Table does not exist, printed from SQLData.search()")

		except lite.Error as e:
			print("Error (SQLData.search): %s" % e.args[0], e, e.args)
			print(self.SQLITE_DB_FILE_PATH)
			print("\n".join([column_names[i]+", "+str(column_values_from_model[i])+", "+str(column_datatypes[i]) for i in range(len(column_names)) ]))
			print(table_name)
			print(self.exclude_variables_from_database)
			sys.exit(1)

		finally:
			if con:
				con.close()

		return nr_found


	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def getColumnInTable(self, select, where = {}, use_like=False):#, SQLITE_DB_FILE_PATH):
		""" 
		Returns all rows of column column_name in the table. The where can be used as an SQL search in the form
		of a dictionary. For example select=label, where = \{ "lattice":"a" \}.
		"""

		db_name = self.SQLITE_DB_FILE_PATH
		table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo()

		con = None
		#table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo()
		try:
			# Make connection (dont forget the detect_types for using np arrays that you defined yourself)
			con = lite.connect(db_name, detect_types=lite.PARSE_DECLTYPES)
			# Make a connection
			con.row_factory = lite.Row
			# Set the cursor
			cur = con.cursor()    

			search_str = []
			for key in where:
				if use_like:
					search_str.append(key+" LIKE \'%"+where[key]+"%\'")
				else:
					search_str.append(key+"=\'"+where[key]+"\'")
			search_str = " AND ".join(search_str)

			# Execute and fetch
			sql_q = "select "+select+" from "+table_name
			if search_str.strip() != "":
				sql_q += " WHERE "+search_str
			#print sql_q
			cur.execute(sql_q)
			rows = cur.fetchall()

			return [ r[select] for r in rows]

		except lite.Error as e:
		    print("Error (getColumnInTable): %s" % e.args[0])
		    sys.exit(1)
		    
		finally:
		    if con:
		        con.close()



	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def tableExists(self, table_name):#, SQLITE_DB_FILE_PATH):
		"""Checks if the table exists in the SQLite database"""
		con = None
		try:
			con = lite.connect(self.SQLITE_DB_FILE_PATH, detect_types=lite.PARSE_DECLTYPES)
			cur = con.cursor()    
			cur.execute("SELECT * FROM "+table_name+";")
			return True

		except lite.Error as e:
			return False
		    
		finally:
		    if con:
		        con.close()

	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def getTableName(self):
		""" Gives name of the table where the data of this model is saved """
		return self.__class__.__name__+"s"


	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def generateRowAndTableInfo(self, with_id = True):
		"""
			Generates the table name, a list of column names (based on the object variables, the values of these 
			variables as currently in the model (not necessarily as in the database) and generates 
			a list of SQLite datatypes corresponding to the datatypes of the object variables
		"""


		table_name = self.getTableName()

		if with_id:
			column_names = ["Id"]
			column_datatypes = [self.default_variable_values["Id"]]
			column_values_from_model = [self.Id]
		else:
			column_names = []
			column_datatypes = []
			column_values_from_model = []

		var_dict = self.__dict__

		# Now pop the variables that are not user made (done this way as to not mess up the original dict):
		var_dict = {i:var_dict[i] for i in var_dict if (i!="SQLITE_DB_FILE_PATH" and i!="Id" and i!= "exclude_variables_from_database" and i not in self.exclude_variables_from_database)}

		for name in var_dict:

			column_names.append(name)

			if isinstance(var_dict[name], type(None)) and name in self.default_variable_values:
				var = self.default_variable_values[name]
			elif isinstance(var_dict[name], type(None)):
				warnings.warn("SQLData.generateRowAndTableInfo: no type known for (its set to None and no default given): "+name )
				sys.exit()
			else:
				var = var_dict[name]

			if isinstance(var, (str, unicode)):
				column_datatypes.append("VARCHAR(200)")
			elif isinstance(var, (int, long, float)):
				column_datatypes.append("FLOAT")
			elif isinstance(var, np.ndarray):
				column_datatypes.append("array")
			elif isinstance(var, list):
				column_datatypes.append("VARCHAR(200)")
			elif isinstance(var, complex):
				warnings.warn("SQLData, generateRowAndTableInfo: complex datatypes not supported in current version of SQLData.")
				sys.exit()
			else:
				warnings.warn("SQLData.generateRowAndTableInfo: Unknown datatype: "+name+", "+ str(type(var)))
				sys.exit()

			# Lists will be saved as comma separated. 
			if isinstance(var, list):
				column_values_from_model.append(\
					self.listToString(var)
					)
			else:
				column_values_from_model.append(var)

		return table_name, column_names, column_values_from_model, column_datatypes

							
	# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	def listToString(self, var, inverse=False):
		""" Conversts a list into a string to save in the sqlite database. Inverse also avaliable """
		if inverse and isinstance(var, str):
			return [v.strip() for v in var.split("List: ")[1].split("<,>") ]
		elif isinstance(var, list):
			return "List: "+"<,> ".join([str(item) for item in var])

