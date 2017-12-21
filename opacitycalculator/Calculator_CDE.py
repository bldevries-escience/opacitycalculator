# Author: Ben de Vries
# Contact: bldevries.science@gmail.com
# Web: www.stjerke.com
# Github: https://github.com/bldevries

import 	sys
import 	os
from 	math import *
from 	numpy import *
import warnings

SIZE_STEP = 0.01 # Microns

def calc_C_CDE_small(w,a,n,k):

	# Make complex values out of the n and k
	m = []
	for i in range(len(k)):
		m.append( complex(n[i], k[i]) )
	m = array(m)
	
	# Apply Equation 12.36 (page 356) in Bohren & Huffman for 
	# the absorption cross sections. Note this is an averaged 
	# cross section, see the book.
	epsilon = m**2
	alpha=(2*epsilon*log(epsilon)/(epsilon-1))-2
	V=(4/3)*pi*a**3
	k=2*pi/w
	cab=k*V*imag(alpha)

	# And calculate the scattering
	csc = 0.5 * (k*k*k*k * V*V * abs(epsilon -1)*abs(epsilon -1) * imag(alpha)) / (3 * pi * imag(epsilon))
	
	return {"abs":cab, "sca":csc, "m":m}


def calc_CDE(w, n, k, grain_size, rho):
	"""
	Calculates the absorption and scattering cross-sections.
	Units:
		w: micron
		grain_size: micron
		rho: gr/cm^3 
		Oabs, Osca: cm^2/gr
	"""

	# Set wavelength to centimeters
	w = w*1e-4
	# Set grain size to cm
	grain_size = grain_size*1e-4

	# Calculate cross-sections
	C = calc_C_CDE_small(w, grain_size, n, k)

	# Convert to specific cross-sections
	V = (4/3)*pi*(grain_size**3)
	m = V*float(rho)
	Oabs = C["abs"] / m
	Osca = C["sca"] / m

	return Oabs, Osca


# --------------------------------------------------------------------
# makeAmorph
# --------------------------------------------------------------------
# file_lnk: string
# rho: string(castable to float)/float
# size: catalog -> {"a_min", "a_max", "slope"}
#def makeAmorph(file_lnk, rho, size, grid):
def makeAmorph(w, n, k, rho, size):

	conv = 1e-4
	
	# c1 = Read.read(file_lnk, headerLength=3, comChar='#')
	# w = array( c1[0] ) 
	# n = array(c1[1])
	# k = array(c1[2])
	
	w = array([w[i] * conv for i in range(len(w))]) # cm
	
	A = makeSizeGrid(size)
	A = A * conv #cm

	o_abs = 0
	o_sca = 0
	sum_a = 0

	for a in A:
		C = calc_C_CDE_small(w, a, n, k)
		V = (4/3)*pi*(a**3)
		m = V*float(rho)
		Oabs = C["abs"] / m
		Osca = C["sca"] / m
		o_abs = o_abs + Oabs * 	a**(size["slope"]) * SIZE_STEP*conv #!!!! MICRONS
		o_sca = o_sca + Osca * 	a**(size["slope"]) * SIZE_STEP*conv
		sum_a = sum_a + 		a**(size["slope"]) * SIZE_STEP*conv
		
	o_abs = o_abs / sum_a
	o_sca = o_sca / sum_a
	o = o_abs+o_sca

	w = array([w[i]/conv for i in range(len(w))]) # micron
	
	size_param_min = array([2*pi*float(size["min"])/w[i] for i in range(len(w))])
	size_param_max = array([2*pi*float(size["max"])/w[i] for i in range(len(w))])
	absMx_min = array([abs(C["m"][i]*2*pi*float(size["min"])/w[i]) for i in range(len(w))])
	absMx_max = array([abs(C["m"][i]*2*pi*float(size["max"])/w[i]) for i in range(len(w))])

	# if len(grid) != 0:
	# 	o, o_abs, o_sca, n, k, w = setToGrid(o, o_sca, o_abs, n, k, w, grid)
	
	
	p = ""
	for i in range(len(w)):
		p+=str(w[i])+" "+str(o[i])+" "+str(o_abs[i])+" "+str(o_sca[i])+"\n"
		for j in range(6):
			for k in range(180):
				p+=str(k+1)+" "
			p+="\n"
	
	return w, o_abs, o_sca, {"w":w, "o":o, "o_abs": o_abs, "o_sca": o_sca, "n":n, "k":k, "p":p,\
			"size_p_min":size_param_min, "size_p_max":size_param_max,\
			"mx_min":absMx_min, "mx_max":absMx_max}

# --------------------------------------------------------------------
# makeCryst
# --------------------------------------------------------------------
# file_lnk: list of strings with len 3
# rho: string(castable to float)/float
# size: catalog -> {"a_min", "a_max", "slope"}
def makeCryst(w, list_n, list_k, rho, size):
	
	# c1 = Read.read(list_file_lnk[0], headerLength=9)
	# c2 = Read.read(list_file_lnk[1], headerLength=9)
	# c3 = Read.read(list_file_lnk[2], headerLength=9)
	
	conv = 1e-4
	
	w = array(w)*conv #array( c1[0] ) * conv # cm
	n = [array(i_n) for i_n in list_n]  #[ array(c1[1]), array(c2[1]), array(c3[1]) ]
	k = [array(i_k) for i_k in list_k] #[ array(c1[2]), array(c2[2]), array(c3[2]) ]

	#print "N", n

	A = makeSizeGrid(size)
	A = array([A[i] * conv for i in range(len(A))]) # cm
	#w = array([w[i] * conv for i in range(len(w))]) # cm
	
	o_abs = 0
	o_sca = 0
	sum_a = 0
	a_step = SIZE_STEP * conv
	for a in A:	
		C = [calc_C_CDE_small(w, a, n[i], k[i])  for i in range(len(n)) ]
		V = (4/3)*pi*(a**3)
		m = V*float(rho)

		
		temp1 = [(1/m) * C[i]["abs"] * a**(size["slope"]) * a_step for i in range(len(n)) ]
		temp1 = (temp1[0]+temp1[1]+temp1[2])/3
		o_abs = o_abs + temp1

		temp = [(1/m) * C[i]["sca"] * a**(size["slope"]) * a_step for i in range(len(n)) ]
		temp = (temp[0]+temp[1]+temp[2])/3
		o_sca = o_sca + temp
		
		sum_a = sum_a + a**(size["slope"]) * a_step

	o_abs = o_abs / sum_a
	o_sca = o_sca / sum_a
	o = o_abs+o_sca

	w = array([w[i]/conv for i in range(len(w))]) # micron

	size_param_min = array([2*pi*float(size["min"])/w[i] for i in range(len(w))])
	size_param_max = array([2*pi*float(size["max"])/w[i] for i in range(len(w))])
	absMx_min = array([abs(C[0]["m"][i]*2*pi*float(size["min"])/w[i]) for i in range(len(w))])
	absMx_max = array([abs(C[0]["m"][i]*2*pi*float(size["max"])/w[i]) for i in range(len(w))])

	# if len(grid) != 0:
	# 	o, o_abs, o_sca, n, k, w = setToGrid(o, o_sca, o_abs, n, k, w, grid)

	p = ""
	for i in range(len(w)):
		p+=str(w[i])+" "+str(o[i])+" "+str(o_abs[i])+" "+str(o_sca[i])+"\n"
		for j in range(6):
			for k in range(180):
				p+=str(k+1)+" "
			p+="\n"
			
	return w, o_abs, o_sca, {"w":w, "o": o, "o_abs":o_abs, "o_sca":o_sca, "n":n, "k":k, "p":p,\
			"size_p_min":size_param_min, "size_p_max":size_param_max,\
			"mx_min":absMx_min, "mx_max":absMx_max}			



# --------------------------------------------------------------------
# makeSizeGrid
# --------------------------------------------------------------------
# size: catalog -> {"a_min", "a_max", "slope"}
# *
# Makes an array with a size distribution in MICRONS
# The grid has a constant step size
def makeSizeGrid(size):
	a_step = float(SIZE_STEP)
	a_min = float(size["min"])
	a_max = float(size["max"])
	slope = float(size["slope"])
	a = []

	# If there is no distribution for the size,
	# but just a single size
	if a_min == a_max : return array([a_min])

	# Otherwise creat a distribution of sizes
	# with constant step size 
	go = 1
	i = 0
	while go:
		a.append(a_min+i*a_step)
		i+=1
		if (a_min+i*a_step > a_max):
			go = 0

	return array(a)




# --------------------------------------------------------------------
# setToGrid
# --------------------------------------------------------------------
# def setToGrid(o, o_sca, o_abs, n, k, w, grid):
# 	warnings.warn("CDE.py, setToGrid: this function is not supported anymore", DeprecationWarning)
# 	print "Running: CDE.setToGrid()"

# 	s, e, step = float(grid["start"]), float(grid["end"]) , float(grid["step"])
# 	grid = [s+i*step for i in range(int((e-s)/step))]

# 	o = array(lMan.makeSameResolution(y = o, x = w, y_set = grid, x_set = grid)["y"])
# 	o_abs = array(lMan.makeSameResolution(y = o_abs, x = w, y_set = grid, x_set = grid)["y"])
# 	o_sca = array(lMan.makeSameResolution(y = o_sca, x = w, y_set = grid, x_set = grid)["y"])

# 	if len(n) == 3:
# 		n_new, k_new = [], []
# 		for i in range(len(n)):
# 			n_new.append(array(lMan.makeSameResolution(y = n[i], x = w, y_set = grid, x_set = grid)["y"]))
# 			k_new.append(array(lMan.makeSameResolution(y = k[i], x = w, y_set = grid, x_set = grid)["y"]))
# 		n, k = n_new, k_new
# 	else:	
# 		n = array(lMan.makeSameResolution(y = n, x = w, y_set = grid, x_set = grid)["y"])
# 		k = array(lMan.makeSameResolution(y = k, x = w, y_set = grid, x_set = grid)["y"])
# 	w = array(grid)

# 	print len(grid), len(o)

# 	return o, o_abs, o_sca, n, k, w