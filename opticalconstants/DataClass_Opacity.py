
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
import itertools
import warnings


#from sqlite_model import *
#from DataClass_OpticalConstants import *
#
#import Calculator_MIE

from .DataClass_OpticalConstants import OpticalConstants
from .Calculator_CDE import calc_CDE
from .SQLData import SQLData


# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# CLASS DATA
# -------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------
# To Do:
#		* Implement mixed optical constants
#			This might be done using self.label as a list of labels? Or maybe a catalogue 
#			also containing the abundance ratios
#		* Implement grain size distribution
#			This can be recognized when self.grain_size_max and self.grain_size_slope are non-default
#		* 
class Opacity(SQLData):
	
	
	POSSIBLE_GRAIN_SHAPES = ["CDE", "MIE"]

	# ^^^^^^^^^^^^^^^
	# Constructor
	#
	def __init__(self, SQLITE_DB_FILE_PATH, **kargs):
		
		self.oc_exists = False
		#self.mixing = False
		#self.use_slope = False

		super(Opacity, self).__init__(SQLITE_DB_FILE_PATH)
		#self.SQLITE_DB_FILE_PATH = SQLITE_DB_FILE_PATH
		
		# COMPOSITION PARAMETERS
		self.labels						= []
		self.grain_porosity				= 0

		# PARTICLE SHAPE PARAMETERS
		self.grain_shape 				= ""
		self.grain_filling_factor_DHS	= -1.0

		# PARTICLE SIZE PARAMETERS
		self.grain_size_start 			= -1.0
		self.grain_size_end 			= -1.0
		self.grain_size_slope			= -9999999.0
		self.grain_size_steps_per_micron= -1.0
		
		
		#self.grain_temperature 			= None

		# WAVELENGTH GRID PARAMETERS
		self.w_start					= -1.0
		self.w_end						= -1.0
		self.w_steps_per_micron			= -1.0
		self.w_extrapolate				= -1.0 # !! Need to make these boolean, need to implement this at SQLData level
		self.w_interpolate				= -1.0

		# RESULTS
		self.optical_constants			= [] #!
		self.wavelength 				= np.array([])
		self.grain_size_distribution_s	= np.array([]) # Size grid
		self.grain_size_distribution_p	= np.array([]) # Size probability
		self.o_sca 						= np.array([])
		self.o_abs 						= np.array([])


		# Set default values
		self.default_variable_values.update({"labels": 						[], \
											"grain_porosity":				0,\
											"grain_shape": 					"", \
											"grain_filling_factor_DHS": 	-1.0,\
											"grain_size_start": 			-1.0, \
											"grain_size_end": 				-1.0, \
											"grain_size_slope": 			-9999999.0, \
											"grain_size_steps_per_micron": 	-1.0,\
											"w_start":						-1.0,\
											"w_end":						-1.0,\
											"w_steps_per_micron":			-1.0,\
											"w_extrapolate":				"none",\
											"w_interpolate":				"none",\
											"wavelength":					np.array([]),\
											"grain_size_distribution_s":	np.array([]),\
											"grain_size_distribution_p":	np.array([]),\
											"o_sca":						np.array([]),\
											"o_abs":						np.array([]),\
											})
		
		self.exclude_variables_from_database.extend([	"optical_constants",\
														"oc_exists", \
														"POSSIBLE_GRAIN_SHAPES", \
													])

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
				self.oc_exists = True

		for label in self.labels:
			oc = OpticalConstants(label = label)
			if oc.ocExists:
				self.optical_constants.append(oc)
			else:
				warnings.warn("For this label no optical constants were found: {}".format(label))

	def process(self):
		
		print ("Processing...")

		# Combine the different optical constants
		if len(self.labels)>1:
			warnings.warn("Opacity, Not yet supported message: combining different materials/opticalconstants is not yet implemented")
		OC = self.optical_constants[0]
		if not OC.is_crystalline():
			list_N, list_K = [OC.N1], [OC.K1]
		else:
			#print "! Crystalline"
			list_N, list_K = [OC.N1,OC.N2, OC.N3], [OC.K1, OC.K2, OC.K3]
		rho = OC.rho

		# Set up wavelength grid
		if self.w_start != -1.0 or self.w_end != -1.0 or self.w_steps_per_micron != -1.0:
			warnings.warn("Opacity, Not yet supported message: setting the wavelength resolution is not yet implemented")
		self.wavelength = OC.wavelength
		W = self.wavelength

		# Set up grain size distribution
		if self.w_extrapolate != -1.0 or self.w_interpolate != -1.0:
			warnings.warn("Opacity, Not yet supported message: interpolation and extrapolation of the wavelength grid are not yet implemented")
		self.grain_size_distribution_s	= np.array([self.grain_size_start])
		self.grain_size_distribution_p	= np.array([1.0]) # Size probability

		# Iterate over size distribution
		absorption, scattering = [], []
		for size, prob in itertools.izip(self.grain_size_distribution_s, self.grain_size_distribution_p):

			# Iterate over different crystal axes
			absorption_at_size, scattering_at_size = [], []
			for N, K in itertools.izip(list_N, list_K):
				if self.grain_shape == "CDE" or self.grain_shape == "":
					if self.grain_shape == "":
						warnings.warn("Opacity, grain shape not set")
					abs_at_NK, sca_at_NK = Calculator_CDE.calc(W, N, K, size, rho)
				else:
					warnings.warn("Opacity, unknown grain shape: "+self.grain_shape)
					sys.exit()

				absorption_at_size.append( abs_at_NK )
				scattering_at_size.append( sca_at_NK )

			#print "! absorption_at_size length", len(absorption_at_size)
			absorption_at_size = sum(absorption_at_size)/len(absorption_at_size)
			scattering_at_size = sum(scattering_at_size)/len(scattering_at_size)

			absorption.append(absorption_at_size*prob)
			scattering.append(scattering_at_size*prob)


		# We must make sure that the size distribution is normalized
		#integr = integrate()
		absorption = sum(absorption)
		scattering = sum(scattering)

		self.o_abs, self.o_sca = absorption, scattering





		
		



	# ^^^^^^^^^^^^^^^
	# get functions for the columns
	#
	def getWavelength(self,):
		return self.wavelength

	def getW(self):
		return self.wavelength

	def getAbs(self):
		return self.o_abs

	def getSca(self):
		return self.o_sca




