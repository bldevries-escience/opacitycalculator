# Author: Ben de Vries
# Contact: bldevries.science@gmail.com
# Web: www.stjerke.com
# Github: https://github.com/bldevries

import 	sys
import 	os
import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt
from operator import itemgetter
import warnings
import sqlite3 as lite
import io
import pkg_resources

from .SQLData import SQLData


# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# CLASS OpticalConstants
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
""" 
This class inherits functions and variables from the SQLData class. See that class for 
additional information.
"""
class OpticalConstants(SQLData):	

	# ^^^^^^^^^^^^^^^
	# Constructor
	#
	def __init__(self,  SQLITE_NK_DB_FILE_PATH=None, **kargs):

		if SQLITE_NK_DB_FILE_PATH is None:
			self.SQLITE_NK_DB_FILE_PATH = pkg_resources.resource_filename(
											__name__, 
											'SQLITE_NK_DATABASE.db')
		else:
			self.SQLITE_NK_DB_FILE_PATH = SQLITE_NK_DB_FILE_PATH

		self.ocExists = False

		# Call the constructor of the SQLData class with the DB file path
		super(OpticalConstants, self).__init__(self.SQLITE_NK_DB_FILE_PATH)

		# Declare all variables to be saved into the database
		self.label 			= None
		self.type 			= None
		self.info 			= None
		self.composition	= None
		self.reference 		= None
		self.doi			= None
		self.mineral		= None
		self.keywords		= None
		self.lattice 		= None
		self.rho 			= None
		self.u_rho			= None
		self.temperature	= None
		self.u_temperature	= None
		self.wavelength 	= None
		self.N1 			= None
		self.N2 			= None
		self.N3 			= None
		self.K1 			= None
		self.K2 			= None
		self.K3 			= None

		# Set default values
		self.default_variable_values.update({"label": "", \
											"type": "", \
											"info": "", \
											"composition": "",\
											"mineral":"",\
											"keywords":[],\
											"reference": "", \
											"doi": "",\
											"lattice": "", \
											"rho": -1,\
											"u_rho":"",\
											"temperature": 300,\
											"u_temperature": "",\
											"wavelength": np.array([]),\
											"N1":np.array([]),\
											"N2":np.array([]),\
											"N3":np.array([]),\
											"K1":np.array([]),\
											"K2":np.array([]),\
											"K3":np.array([])\
											})


		# Exclude variables from being stored in the database
		self.exclude_variables_from_database.extend(["ocExists", "SQLITE_NK_DB_FILE_PATH"])

		# Search in the kargs for variables to search content with
		# First get the names of all variables stored in the database (function from the SQLite model)		
		table_name, column_names, column_values_from_model, column_datatypes = self.generateRowAndTableInfo()
		# Then assign the found variables
		search = False
		for col in column_names:
			if col in kargs:
				self.__dict__[col] = kargs[col]
				search = True # If any of the variables is given, initiate a search
		
		# Search the database
		if search:
			nr_found = self.search()
			if nr_found > 0:
				self.ocExists = True


	def wavelengthRange(self):
		print("")

	def wavelengthResolution(self):
		print("")

		
	# ^^^^^^^^^^^^^^^
	# Check if the optical constants exist
	#
	def exists(self):
		return self.ocExists

	def is_crystalline(self):
		if self.K2 != None:
			if len(self.K2) > 0:
				return True
