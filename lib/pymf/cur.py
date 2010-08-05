#!/usr/bin/python2.6
#
# Copyright (C) Christian Thurau, 2010. 
# Licensed under the GNU General Public License (GPL). 
# http://www.gnu.org/licenses/gpl.txt
#$Id: cur.py 21 2010-08-05 08:13:08Z cthurau $
#$Author$
"""
PyMF CUR Decomposition [1]

	CUR(SVD) : Class for CUR Decomposition

[1] Drineas, P., Kannan, R. and Mahoney, M. (2006), 'Fast Monte Carlo Algorithms III: Computing 
a Compressed Approixmate Matrix Decomposition', SIAM J. Computing 36(1), 184-206.
"""

__version__ = "$Revision$"

import numpy as np

from svd import pinv, SVD


__all__ = ["CUR"]

class CUR(SVD):
	"""  	
	CUR(data, num_bases=4, show_progress=True, compW=True)
		
	CUR Decomposition. Factorize a data matrix into three matrices s.t.
	F = | data - USV| is minimal. CUR randomly selects rows and columns from
	data for building U and V, respectively. 
	
	Parameters
	----------
	data : array_like
		the input data
	rrank: int, optional 
		Number of rows to sample from data.
		4 (default)
	crank: int, optional
		Number of columns to sample from data.
		4 (default)
	show_progress: bool, optional
		Print some extra information
		False (default)	
	
	Attributes
	----------
		U,S,V : submatrices s.t. data = USV		
	
	Example
	-------
	>>> import numpy as np
	>>> data = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 1.0]])
	>>> cur_mdl = CUR(data, show_progress=False, rrank=1, crank=2)	
	>>> cur_mdl.factorize()
	"""
	
	_VINFO = 'pymf-cur v0.1'
	
	def __init__(self, data, rrank=0, crank=0, show_progress=True):
		SVD.__init__(self, data, rrank=rrank, crank=rrank, show_progress=show_progress)
		
		# select all data samples for computing the error:
		# note that this might take very long, adjust self._rset and self._cset for 
		# faster computations.
		self._rset = range(self._rows)
		self._cset = range(self._cols) 
			
	def sample(self, s, probs):		
		prob_rows = np.cumsum(probs.flatten()) #.flatten()				
		temp_ind = np.zeros(s, np.int32)
	
		for i in range(s):		 
			tempI = np.where(prob_rows >= np.random.rand())[0]
			#if len(tempI) > 0:
			temp_ind[i] = tempI[0]    	
			#else:	
			#	temp_ind[i] = 0
			
		return np.sort(temp_ind)
		
	def sample_probability(self):
		
		dsquare = self.data[:,:]**2
			
		prow = np.array(dsquare.sum(axis=1))
		pcol = np.array(dsquare.sum(axis=0))
		
		prow /= prow.sum()
		pcol /= pcol.sum()	
		
		return (prow.reshape(-1,1), pcol.reshape(-1,1))
							
	def computeUCR(self):				
		# the next  lines do NOT work with h5py if CUR is used -> double indices in self.cid or self.rid
		# can occur and are not supported by h5py. When using h5py data, always use CMD which ignores
		# reoccuring row/column selections.
		self._C = np.dot(self.data[:, self._cid].reshape((self._rows, -1)), np.diag(self._ccnt**(1/2)))		
		self._R = np.dot(np.diag(self._rcnt**(1/2)), self.data[self._rid,:].reshape((-1, self._cols)))
		
		# Compute pseudo inverse of C and R				
		self._U = np.dot(np.dot(pinv(self._C), self.data[:,:]), pinv(self._R))
			
		# set some standard (with respect to SVD) variable names 
		self.U = self._C
		self.S = self._U
		self.V = self._R
			
	def factorize(self):			
		[prow, pcol] = self.sample_probability()
		self._rid = self.sample(self._rrank, prow)
		self._cid = self.sample(self._crank, pcol)
		
		self._rcnt = np.ones(len(self._rid))
		self._ccnt = np.ones(len(self._cid))	
									
		self.computeUCR()
	

if __name__ == "__main__":
	import doctest  
	doctest.testmod()				