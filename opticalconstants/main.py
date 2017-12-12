
import sys
import os
import pkg_resources

from .DataClass_OpticalConstants import *
# from DataClass_Opacity import *

SQLITE_DB_FILE_PATH = pkg_resources.resource_filename(__name__,
                                                      'SQLITE_NK_DATABASE.db')

# def printDatabase():
#   rowsId = OpticalConstants.getColumnInTable("Id", SQLITE_DB_FILE_PATH)
#   rowsL = OpticalConstants.getColumnInTable("label", SQLITE_DB_FILE_PATH)
#   rowsI = OpticalConstants.getColumnInTable("info", SQLITE_DB_FILE_PATH)

#   print '{:*^150}'.format('')
#   print '{:*^150}'.format('  SQLite DATABASE CONTENT  ')
#   print '{:*^150}'.format('')
#   print '{:<5}'.format("Id"), '{:<60}'.format("label")+"Information"
#   print '{:*^150}'.format('')
#   for Id, r, i in zip(rowsId, rowsL, rowsI):
#       print '{:<5}'.format(Id), '{:<60}'.format(r)+i
#   print '{:*^150}'.format('')
#   print '{:*^150}'.format('')


# def getOpticalConstants(label, print_console_output = False):
#   if print_console_output: print ""
#   if print_console_output: print '{:*^50}'.format(' OPACITY CALCULATOR')
#   if print_console_output: print '{:^50}'.format(' - Retrieving Optical Constants - ')
#   if print_console_output: print "Label: ", label

#   oc = OpticalConstants(SQLITE_DB_FILE_PATH, label=label)

#   if print_console_output: print '{:*^50}'.format('')
#   if print_console_output: print ""

#   return oc

# def getOC(label):
#   return getOpticalConstants(label)


# def getOpacity(label, grain_size, grain_shape = "CDE", print_console_output = False):

#   if print_console_output: print ""
#   if print_console_output: print '{:*^50}'.format(' OPACITY CALCULATOR')
#   if print_console_output: print '{:^50}'.format(' - Calculating opacities - ')
#   if print_console_output: print "Label: ", label
#   if print_console_output: print "Grain size: ", grain_size
#   if print_console_output: print "Grain shape: ", grain_shape

#   opac = Opacity(SQLITE_DB_FILE_PATH, label= label, grain_shape=grain_shape, grain_size=grain_size)

#   if print_console_output: print '{:*^50}'.format('')
#   if print_console_output: print ""

#   return opac

# def test():
#   print ""
#   print ""
#   print "DATABASE: ", SQLITE_DB_FILE_PATH
#   printDatabase()

#   getOpticalConstants("fo050")#a_ol_Jager03_mg1.0_fe0.0")

#   for l in ["fo050", "a_ol_Jager03_mg1.0_fe0.0", "a_ol_Jager94_mg0.5_fe0.5"]:#, "py_mg0.95_fe0.05_SiO3"]:
#       Opac = getOpacity(label=l, grain_size = 1.0, print_console_output=True)
#       plt.plot(Opac.getW(), Opac.getAbs())
#   plt.show()


# def test2():
#   print ""
#   print ""
#   print "DATABASE: ", SQLITE_DB_FILE_PATH
#   printDatabase()

#   getOpticalConstants("fo050")

#   for l in ["fo050", "fo295"]:
#       Opac = getOpacity(label=l, grain_size = 1.0, print_console_output=False)
#       plt.plot(Opac.getW(), Opac.getAbs())
#   plt.show()






