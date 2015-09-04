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

import re
import cPickle as pickle

import numpy as np

class GOPCAConfig(object):

	valid_attrs = set(['mHG_X_frac','mHG_X_min','mHG_L','pval_thresh','mfe_pval_thresh','mfe_thresh','disable_local_filter','disable_global_filter'])

	def __init__(self,**kwargs):
		supplied_attrs = set(kwargs.keys())
		unknown_attrs = supplied_attrs - self.valid_attrs
		for k in sorted(unknown_attrs):
			print 'Warning: Config attribute "%s" unknown (will be ignored).' %(k)

		for k in list(self.valid_attrs):
			assert k in supplied_attrs

		kwargs = dict([k,kwargs[k]] for k in list(self.valid_attrs))
		self.__dict__.update(kwargs)


	def __repr__(self):
		return '<GOPCAConfig object (%s)>' %('; '.join(['%s=%s' %(k,getattr(self,str(k))) for k in sorted(self.valid_attrs)]))

	def __str__(self):
		return '<GOPCAConfig object with attributes: %s>' %(', '.join(['%s=%s' %(k,getattr(self,str(k))) for k in sorted(self.valid_attrs)]))

	def __hash__(self):
		return hash(repr(self))

	def __eq__(self):
		if type(self) is not type(other):
			return False
		if repr(self) == repr(other):
			return True
		else:
			return False


class GOPCASignature(object):

	abbrev = [('positive ','pos. '),('negative ','neg. '),('interferon-','IFN-'),('proliferation','prolif.'),('signaling','signal.')]

	def __init__(self,genes,pc,mfe,enrichment,label=None):
		self.genes = set(genes) # genes in the signature
		self.pc = pc # principal component (sign indicates whether ordering was ascending or descending)
		self.mfe = mfe # maximum fold enrichment
		self.enrichment = enrichment # GO enrichment this signature is based on
		if label is None:
			enr = enrichment
			label = '%s: %s (%d:%d/%d)' %(enr.term[2],enr.term[3],pc,enr.k,enr.K)
		self.label = label # signature label

	def __repr__(self):
		return '<GOPCASignature: label="%s", pc=%d, mfe=%.1f; %s>' \
				%(self.label,self.pc,self.mfe,repr(self.enrichment))

	def __str__(self):
		return '<GO-PCA Signature "%s" (PC %d / MFE %.1fx / %s)>' \
				%(self.label,self.pc,self.mfe, str(self.enrichment))

	def __hash__(self):
		return hash(repr(self))

	def __eq__(self,other):
		if type(self) is not type(other):
			return False
		elif repr(self) == repr(other):
			return True
		else:
			return False

	@property
	def pval(self):
		""" The enrichment p-value of the GO term that the signature is based on. """
		return self.enrichment.pval
	
	@property
	def k(self):
		""" The number of genes in the signature. """
		return len(self.genes)

	@property
	def K(self):
		""" The number of genes annotated with the GO term whose enrichment led to the generation of the signature. """
		return self.enrichment.K

	@property
	def n(self):
		""" The threshold used to generate the signature. """
		return self.enrichment.ranks[self.k-1]

	@property
	def N(self):
		""" The total number of genes in the data. """
		return self.enrichment.N

	def get_pretty_format(self,omit_acc=False,nitty_gritty=True,max_name_length=0):
		enr = self.enrichment

		term = enr.term
		term_name = term[3]
		for abb in self.abbrev:
			term_name = re.sub(abb[0],abb[1],term_name)
		if max_name_length > 0 and len(term_name) > max_name_length:
			term_name = term_name[:(max_name_length-3)] + '...'

		term_str = '%s: %s' %(term[2],term_name)
		if not omit_acc:
			term_str = term_str + ' (%s)' %(term[0])

		details = ''
		if nitty_gritty:
			details = ' [%d/%d genes,pc=%d,pval=%.1e,mfe=%.1fx]' \
					%(self.k,self.K,self.pc,self.pval,self.mfe)

		return '%s%s' %(term_str,details)

	def get_pretty_format_GO(self,GO,omit_acc=False,nitty_gritty=True,max_name_length=0):
		enr = self.enrichment
		term = GO.terms[enr.term[0]]
		goterm_genes = GO.get_goterm_genes(term.id)
		details = ''
		if nitty_gritty:
			details = ' [%d/%d genes,n=%d,pc=%d,mfe=%.1fx,pval=%.1e]' \
					%(self.k,self.K,self.n,self.pc,self.mfe,self.pval)
		return '%s%s' %(term.get_pretty_format(omit_acc=omit_acc,max_name_length=max_name_length),details)


class GOPCAResult(object):
	#def __init__(self,genes,W,mHG_X_frac,mHG_X_min,mHG_L,pval_thresh,mfe_pval_thresh,mfe_thresh,signatures):
	#def __init__(self,config,expression_hash,GO_hash,genes,samples,W,signatures,S):
	def __init__(self,config,genes,samples,W,signatures,S):

		# W = loading matrix
		# S = signature matrix

		# checks
		assert isinstance(config,GOPCAConfig)
		assert isinstance(genes,list) or isinstance(genes,tuple)
		assert isinstance(samples,list) or isinstance(samples,tuple)
		assert isinstance(W,np.ndarray)
		assert isinstance(signatures,list) or isinstance(signatures,tuple)
		for s in signatures:
			assert isinstance(s,GOPCASignature)
		assert isinstance(S,np.ndarray)

		assert W.shape[0] == len(genes)
		assert S.shape[0] == len(signatures)
		assert S.shape[1] == len(samples)

		# initialization
		self.config = config
		self.genes = tuple(genes)
		self.samples = tuple(samples)
		self.W = W
		self.signatures = tuple(signatures)
		self.S = S

		@property
		def p(self):
			return len(self.genes)

		@property
		def n(self):
			return len(self.samples)

		@property
		def d(self):
			return self.W.shape[1]

		@property
		def q(sefl):
			return len(self.signatures)
			
	def __repr__(self):
		conf_hash = hash(self.config)
		gene_hash = hash(self.genes)
		sample_hash = hash(self.samples)
		sig_hash = hash((hash(sig) for sig in self.signatures))
		return "<GOPCAResult object (config hash: %d; gene hash: %d; sample hash: %d; # PCs: %d; signature hash: %d)>" \
				%(conf_hash,gene_hash,sample_hash,self.d,self.q,sig_hash)

	def __str__(self):
		conf = self.config
		return "<GOPCAResult object (%d signatures); mHG parameters: X_frac=%.2f, X_min=%d, L=%d; \
				# genes (p) = %d, # principal components (d) = %d>" \
				%(self.q,conf.mHG_X_frac,conf.mHG_X_min,cof.mHG_L,self.p,self.d)

	def __eq__(self,other):
		if type(self) is not type(other):
			return False
		elif repr(self) == repr(other):
			return True
		else:
			return False
