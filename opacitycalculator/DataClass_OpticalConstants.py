# Author: Ben de Vries
# Contact: bldevries.science@gmail.com
# Web: www.stjerke.com
# Github: https://github.com/bldevries

import sys
import os
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
This class inherits functions and variables
from the SQLData class. See that class for
additional information.
This class contains information about a set of
optical constants. It gets those from an sqlite
database.
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
        self.label = None
        self.type = None
        self.info = None
        self.composition = None
        self.reference = None
        self.doi = None
        self.mineral = None
        self.keywords = None
        self.lattice = None
        self.rho = None
        self.u_rho = None
        self.temperature = None
        self.u_temperature = None
        self.wavelength = None
        self.u_wavelength = None
        self.wavelength_grid = None
        self.N1 = None
        self.N2 = None
        self.N3 = None
        self.K1 = None
        self.K2 = None
        self.K3 = None

        # Set default values
        self.default_variable_values.update({"label": "",
                                             "type": "",
                                             "info": "",
                                             "composition": "",
                                             "mineral": "",
                                             "keywords": [],
                                             "reference": "",
                                             "doi": "",
                                             "lattice": "",
                                             "rho": -1,
                                             "u_rho": "",
                                             "temperature": -1,
                                             "u_temperature": "",
                                             "wavelength": np.array([]),
                                             "u_wavelength": "unknown",
                                             "wavelength_grid": "unknown",
                                             "N1": np.array([]),
                                             "N2": np.array([]),
                                             "N3": np.array([]),
                                             "K1": np.array([]),
                                             "K2": np.array([]),
                                             "K3": np.array([])}
                                            )

        # Exclude variables from being stored in the database
        self.exclude_variables_from_database.extend(["ocExists",
                                                     "SQLITE_NK_DB_FILE_PATH"])

        # Search in the kargs for variables to search content with
        # First get the names of all variables stored in the
        # database (function from the SQLite model)
        table_name, column_names, column_values_from_model, \
            column_datatypes = self.generateRowAndTableInfo()
        # Then assign the found variables
        search = False
        for col in column_names:
            if col in kargs:
                self.__dict__[col] = kargs[col]
                # If any of the variables
                # is given, initiate a search
                search = True

        # Search the database
        if search:
            nr_found = self.search()
            if nr_found > 0:
                self.ocExists = True

    def wavelengthResolution(self):
        # Size up the steps in the wavelength grid
        dw = []
        for i in range(len(self.wavelength)-1):
            dw.append(round(self.wavelength[i+1]-self.wavelength[i], 3))

        # Check if the resolution is constant
        if len(dw) != 0:
            variable = not dw.count(dw[0]) == len(dw)
        else:
            variable = False

        # Calculate average and stdev of the resolution
        av = np.average(dw)
        dev = np.std(dw)

        return av, variable, dev

    def print(self):
        # Depending on the step size in the wavelength grid get
        # some information on the wavelength steps for printing
        if self.wavelength_grid == "lin":
            res, var, dev = self.wavelengthResolution()
            grid_info = self.wavelength_grid + ", resolution: " + \
                str(round(res, 3))
        elif self.wavelength_grid == "log":
            start = round(self.wavelength[1]-self.wavelength[0], 5)
            end = round(self.wavelength[-1]-self.wavelength[-2], 5)
            grid_info = self.wavelength_grid+", start/end resolution: " + \
                str(start)+"/"+str(end)
        else:
            res, var, dev = self.wavelengthResolution()
            grid_info = "unknown"+", average resolution/stdev: " + \
                        str(round(res), 3)+"+/-"+str(round(dev), 3)

        # Get the start and end wavelengths
        start, end = self.wavelength[0], self.wavelength[-1]

        # Get some print friendly lattice information
        if self.lattice == "c":
            lat = "crystalline"
        elif self.lattice == "a":
            lat = "amorphous"
        else:
            lat = self.lattice

        # Items that will be printed
        items = [("Label: ", self.label),
                 ("Information: ", self.info),
                 ("Keywords: ", self.keywords),
                 ("Type: ", self.type),
                 ("Lattice structure: ", lat),
                 ("Mineral: ", self.mineral),
                 ("Composition: ", self.composition),
                 ("Density: ", self.rho),
                 ("Units: ", self.u_rho),
                 ("Temperature: ", self.temperature),
                 ("Units: ", self.u_temperature),
                 ("Units wavelength grid: ", self.u_wavelength),
                 ("Wavelength start/end: ", str(start)+", "+str(end)),
                 ("Wavelength grid: ", grid_info),
                 ("Reference: ", self.reference),
                 ("DOI: ", self.doi),
                 ]
                 
        print()
        for i in items:
            print("{:<25}{}".format(i[0], i[1]))
        print()

    # ^^^^^^^^^^^^^^^
    # Check if the optical constants exist
    #
    def exists(self):
        return self.ocExists

    def is_crystalline(self):
        if self.K2 is not None:
            if len(self.K2) > 0:
                return True
