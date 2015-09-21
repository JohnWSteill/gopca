# Copyright (c) 2015 Florian Wagner
#
# This file is part of GO-PCA.
#
# GO-PCA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import csv
import cPickle as pickle

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

from genometools import misc

class Logger(object):

	def __init__(self,verbosity=1,log_file=None):

		# verbosity levels
		# 0: output nothing
		# 1: output only errors
		# 2: output errors and warnings
		# 3: output errors, warnings and messages

		# When then specified verbosity level indicates that output should occur,
		# messages and warnings will be directed to 'outbuf',
		# while errors will be directed to 'errbuf'.

		# All events will be reported in a logfile (if specified).

		self.verbosity = verbosity
		self.log = []
		self.log_file = log_file

		self.ofh = None
		if log_file is not None:
			self.ofh = open(log_file,'w')

	def __del__(self):
		sys.stdout.flush()
		sys.stderr.flush()

		if self.ofh is not None:
			self.ofh.flush()
			self.ofh.close()

	def output(self,s,buf,endline,flush):
		# mimics print
		end = ' '
		if endline:
			end = '\n'
		s = s + end

		# store in variable
		self.log.append(s)

		# write to stdout/stderr
		if buf is not None:
			buf.write(s)
			if flush: buf.flush()

		# write to log file
		if self.ofh is not None:
			self.ofh.write(s)

	def message(self,s,endline=True,flush=False):

		s = 'Info: ' + s

		buf = sys.stdout
		if self.verbosity < 3:
			buf = None

		self.output(s,buf,endline,flush)

	def warning(self,s,endline=True,flush=False):

		s = 'Warning: ' + s
		buf = sys.stdout
		if self.verbosity < 2:
			buf = None

		self.output(s,buf,endline,flush)

	def error(self,s,endline=True,flush=False):

		s = 'Error: ' + s
		buf = self.stderr
		if self.verbosity == 0:
			buf = None

		self.output(s,buf,endline,flush)

def print_signatures(signatures):
	a = None
	maxlength = 40
	a = sorted(range(len(signatures)),key=lambda i: -signatures[i].msfe)

	for i in a:
		sig = signatures[i]
		print sig.get_label(max_name_length=maxlength,include_pval=True)

def read_meta(fn):
	meta = {}
	with open(fn) as fh:
		reader = csv.reader(fh,dialect='excel-tab')
		for l in reader:
			meta[l[0]] = l[1:]
	return meta

def read_gene_data(fn,case_insensitive=False):
	labels = None
	genes = []
	data = []
	with open(fn) as fh:
		reader = csv.reader(fh,dialect='excel-tab')
		labels = reader.next()[1:]
		for l in reader:
			g = l[0]
			if case_insensitive: g = g.upper()
			genes.append(g)
			data.append(l[1:])
	D = np.float64(data)
	return genes,labels,D

def read_expression(fn,case_insensitive=False):
	samples = None
	genes = []
	expr = []
	with open(fn) as fh:
		reader = csv.reader(fh,dialect='excel-tab')
		samples = reader.next()[1:]
		for l in reader:
			g = l[0]
			if case_insensitive: g = g.upper()
			genes.append(g)
			expr.append(l[1:])
	E = np.float64(expr)
	return genes,samples,E

def write_expression(output_file,genes,samples,E):
	write_gene_data(output_file,genes,samples,E)

def write_gene_data(output_file,genes,labels,D):
	p = len(genes)
	n = len(labels)
	assert D.shape == (p,n)
	with open(output_file,'w') as ofh:
		writer = csv.writer(ofh,dialect='excel-tab',lineterminator='\n',quoting=csv.QUOTE_NONE)
		writer.writerow(['.'] + labels)
		for i,g in enumerate(genes):
			writer.writerow([g] + ['%.5f' %(D[i,j]) for j in range(n)])

def get_standardized(e):
	e = e.copy()
	e -= np.mean(e)
	e /= np.std(e,ddof=1)
	return e

def get_signature_expression(genes,E,sig_genes):
	p_sig = len(sig_genes)
	p,n = E.shape
	S = np.zeros((p_sig,n),dtype=np.float64)
	for i,g in enumerate(sig_genes):
		idx = genes.index(g)
		S[i,:] = E[idx,:]
		S[i,:] -= np.mean(S[i,:])
		S[i,:] /= np.std(S[i,:],ddof=1)
	sig = np.mean(S,axis=0)
	return sig

def get_signature_expression_robust(genes,E,sig_genes):
	p_sig = len(sig_genes)
	p,n = E.shape
	S = np.zeros((p_sig,n),dtype=np.float64)
	for i,g in enumerate(sig_genes):
		idx = misc.bisect_index(genes,g)
		S[i,:] = E[idx,:]
		med = np.median(S[i,:])
		mad = np.median(np.absolute(S[i,:]-med))
		std = 1.4826*mad
		S[i,:] -= med
		S[i,:] /= std
	sig = np.mean(S,axis=0)
	return sig

def get_signature_label(GO,sig,max_length=40):
	count = ' (%d:%d/%d)' %(sig.pc,len(sig.genes),sig.K)
	enr = sig.enrichment
	return GO.terms[enr.term[0]].get_pretty_format(omit_acc=True,max_name_length=max_length) + count

def variance_filter(genes,E,top):
	# filter genes by variance
	a = np.argsort(np.var(E,axis=1,ddof=1))[::-1]
	n = E.shape[0]
	sel = np.zeros(n,dtype=np.bool_)
	sel[a[:top]] = True
	sel = np.nonzero(sel)[0]
	genes = [genes[i] for i in sel]
	E = E[sel,:]
	return genes,E

def read_gopca_result(fn):
	result = None
	with open(fn) as fh:
		result = pickle.load(fh)
	return result

def read_annotations(fn):
	ann = {}
	with open(fn) as fh:
		reader = csv.reader(fh,dialect='excel-tab')
		for l in reader:
			ann[tuple(l[:4])] = l[4].split(',')
	return ann

def get_signature_labels(signatures,omit_acc=False):
	labels = []
	for sig in signatures:
		return sig.enrichment
		
def cluster_rows(S,metric='correlation',method='average',invert=False):
	distxy = squareform(pdist(S, metric=metric))
	R = dendrogram(linkage(distxy, method=method),no_plot=True)
	order_rows = np.int64([int(l) for l in R['ivl']])
	if invert:
		order_rows = order_rows[::-1]
	return order_rows

def cluster_signatures(S,metric='correlation',method='average',invert=False):
	# hierarchical clustering of signatures
	order_rows = cluster_rows(S,metric,method,invert)
	return order_rows

def get_qvalues(pvals,pi_zero=1.0):
	# implements storey-tibshirani procedure for calculating q-values
	n = pvals.size
	qvals = np.empty(n,dtype=np.float64)

	# start with largest p-value
	a = np.argsort(pvals,kind='mergesort') # stable sort
	a = a[::-1]

	s = 1
	q = 1.0
	for i in a:
		q = min(((pi_zero * pvals[i])*n)/s , q)
		qvals[i] = q
		s += 1

	return qvals
