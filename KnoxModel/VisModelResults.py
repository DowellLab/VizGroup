# -*- coding: utf-8 -*-

# 
#
#Copyright (2011-2012) University of Colorado
#All Rights Reserved
#Author: David Knox
#
#
import sys, os, math, errno, getopt, re
import random
import numpy as np
import pylab as P
import KnoxUtils as K
import SRB as SRB_Utils
import TAMO
from   TAMO.seq import Fasta

###################################################################################################

def usage():
	print 'Usage: %s  csv_file'%(re.sub('^.*/','',sys.argv[0]))
	print '\n'
	print '   Visualize the results of model'
	
###################################################################################################
#
#
def ReadSimHeader(file, verbose=False):
	headers = dict()
	line = file.readline()
	line = line.strip()
	fields = line.split(",")
	#print "Columns:"
	str = ""
	for i,f in enumerate(fields):
		f = f.strip()
		headers[f] = i
		if (i%10 == 0):
			if (verbose): print str
			str = "%3d:"%i
		str += " %-24.24s"%("[%s]"%f)
	if (verbose): print str
	return headers
# end ReadSimHeader

###################################################################################################
# ReadSimTimestep(file, n_lines_processed, verbose)
#	Read values from next line in file
#	Parse the line into fields
#	Return (# total lines processed, fields)
#
def ReadSimTimestep(file, n, verbose=False):
	
	line = file.readline()
	while (line and (len(line) > 0)):
		if ((n%100 == 0) and verbose):
			#sys.stdout.write("\r%10d of %d lines parsed"%(n, n_lines))
			sys.stdout.write("\r%10d lines parsed"%(n))
			sys.stdout.flush()
		n += 1
		
		if (len(line) > 2) and (line[0] != '#'):
			print 'LINE:'
			print line
			line = line.strip()
			fields = line.split(",")
			for f in range(len(fields)):
				fields[f] = fields[f].strip()
			return n, fields
		
		line = file.readline()
	
	# only get here if end of file	
	if (verbose):
		sys.stdout.write("\r%10d lines parsed"%(n))
		sys.stdout.flush()
	return n,[]
	
#end of ReadSimTimestep

###################################################################################################

def GetBoolStates(vals, cols):
	states = []
	for c in cols:
		# find state of the given col
		if (c > 0) and (vals[c] != "0"):
		#	print "Boolean: [%s]"%vals[c], "==>", True
			states.append(True)
		else:
		#	print "Boolean: [%s]"%vals[c], "==>", False
			states.append(False)
	return states
	
###################################################################################################

# collect the data from rows matching 'match'
def GetMatchingCols(match, headers, vals, row):
	for h in headers:
		if (h[:len(match)] == match):
		#	print "\t%s"%(h)
			data_col = int(h[len(match):])
			v = headers[h]
		#	print "[%s]  data[%d] = vals[%d] = %f"%(h, data_col, v, vals[v])
			row[data_col] = vals[v]
#end GetMatchingCols

def GetCol(colstr, headers):
	c = -2
	if colstr in headers:
		c = headers[colstr]
	return c
#end GetCol


def GetPositionalCol(prefix, col, headers):
	c = -2

	cstr = "%s%04d"%(prefix,col)
	
	if cstr in headers:
		c = headers[cstr]

#	print "GetPositionalCol(%s)==>%d"%(cstr,c)

	return c
#end GetCol

###################################################################################################
def	Print_Counts(counts, title):
	
	divider = BuildDivider(len(counts))
	
	max_count = max(counts)
	if (max_count > 0): 
		n_lines = int(math.ceil(math.log(max_count,10)))
		
		limit = math.pow(10,n_lines) #10**n_lines 
		print "[%s] max=%d, n_lines=%d, limit=%d"%(title, max_count, n_lines, limit)
		print divider
		
		for n in xrange(n_lines):
			limit /= 10
			line = "%5d:"%limit
			
			for val in counts:
				if (val > limit):
					line += "%d"%(val/limit%10)
				elif (limit > 1):
					line += " "
				else:
					line += "_"
					
			print line
		
	print divider
# end of Print_Counts

###################################################################################################
def	Print_Graph(counts, title, mean=0):
	
	divider = BuildDivider(len(counts))
	
	max_count = max(counts)
	n_lines = 50
	
	print "[%s] max=%d"%(title, max_count)
	print divider
	
	for n in xrange(n_lines):
		limit = (n_lines-n) * (100/n_lines)
		line = "%5d:"%limit

		filler = ' '
		if (mean > 0) and (mean >= limit):
			filler = '-'
			mean = 0

		for val in counts:
			if (val >= limit):
				line += "*"
			else:
				line += filler
				
		print line
		
	print divider
# end of Print_Graph

###################################################################################################
def	Print_Percent_Graph2(counts, title, mean=0, n_lines=50):
	
	if (len(counts) == 0): return
	
	divider = BuildDivider(len(counts))
	
	max_count = max(counts)
	
	print "[%s] max=%d"%(title, max_count)
	print divider
	
	for n in xrange(n_lines):
		limit = (n_lines-n) * (100/n_lines)
		line = "%5d:"%limit

		filler = ' '
		if (mean > 0) and (mean >= limit):
			filler = '-'
			mean = 0

		for val in counts:
			if (val >= limit):
				line += "*"
			else:
				line += filler
				
		print line
		
	print divider
# end of Print_Percent_Graph2

###################################################################################################
def	Print_Percent_Graph3(lower, upper, counts, title, mean=0, delta=0):
	print counts[:100]
	
	if (len(counts) == 0): return
	
	divider = BuildDivider(len(counts))
	
	max_count = max(counts)
	n_lines = 50
	
	if (delta <= 0):
		delta   = (upper-lower)/n_lines
	else:
		n_lines = (upper-lower)/delta
		
	print "[%s] max=%d"%(title, max_count)
	print divider
	
	limit = upper
	for n in xrange(n_lines):
		limit = limit - delta
		line = "%5d:"%limit

		filler = ' '
		if (mean > 0) and (mean >= limit):
			filler = '-'
			mean = 0

		for val in counts:
			if (val > 0) and (limit >= 0) and (val >= limit):
				line += "*"
			elif (val < 0) and (limit <= 0) and (val <= limit):
				line += "*"
			else:
				line += filler
				
		print line
		
	print divider
# end of Print_Percent_Graph3
###################################################################################################
def	Print_Percent_Graph_LOG(counts, title):
	
	if (not counts) or (len(counts) == 0): return
	
	max_count = max(counts)
	n_lines = 10
	
	print "Log Scale [%s] max=%d in %d entries"%(title, max_count, len(counts))
	
	for n in xrange(n_lines):
		limit = (n_lines-n) * n_lines
		line = "%5d:"%limit
		
		for val in counts:
			v = val
			v = 100 - int(math.ceil(-10 * math.log(v,10)))
			if (v >= limit):
				line += "*"
			else:
				line += " "
				
		print line
		
# end of Print_Percent_Graph_LOG

###################################################################################################
def BuildDivider(N_DNA):	# build by group number
	line1 = "     :"
	line2 = "     :"
	line3 = "     :"

#	for dna_pos in xrange(1,N_DNA):
	for dna_pos in xrange(DISPLAY_START,DISPLAY_END+1):
		line3 += "%d"%(dna_pos%10)
		line2 += "%d"%(dna_pos/10%10)
		if ((dna_pos%10) == 0):
			line1 += "%10d"%(dna_pos/100)

	divider =  line1
	divider += "\n"
	divider += line2
	divider += "\n"
	divider += line3
	return divider

def POS_BuildDivider(N_DNA):	
	line1 = "     :"
	line2 = "     :"
	line3 = "     :"
	pos   = START_POS + DISPLAY_START * NT_PER_GROUP 

#	for dna_pos in xrange(1,N_DNA):
	for dna_pos in xrange(DISPLAY_START,DISPLAY_END+1):
		line3 += "%d"%(pos%10)
		line2 += "%d"%(pos/10%10)
		if ((dna_pos%10) == 0):
			line1 += "%10d"%(pos/100)
		pos += NT_PER_GROUP

	divider =  line1
	divider += "\n"
	divider += line2
	divider += "\n"
	divider += line3
	return divider

###################################################################################################

def BuildHighlighter(highlites):
	
	lineH = "     :"
	
	for dna_pos in xrange(DISPLAY_START,DISPLAY_END+1):
		nt = (dna_pos * NT_PER_GROUP) + START_POS
		
		ch = ' '
		for h in highlites:
			if (nt >= h[0]) and (nt < (h[1]+NT_PER_GROUP-1)):
				ch = h[2]

		lineH += ch
		
	return lineH

###################################################################################################

def LoadDNA():
	###############################################################################
	#
	#	Read DNA seqeuence
	#	Extract sub-sequence to model
	#	Define rules for DNA
	# 
	###############################################################################
	START_POS = 0
	dna = ""
	fastafile = params.GetString(DNA_section,"FILE")
	if (fastafile):	
		chromo = params.GetString(DNA_section,"CHR")
		chr_start  = params.GetInt(DNA_section,"START")
		chr_end    = params.GetInt(DNA_section,"END")
		if (not chr_end):
			chr_end = params.GetInt(DNA_section,"LENGTH")
			chr_end += chr_start
		
		print ("Loading fasta: [%s]\n"%fastafile)

		seqs = Fasta.load(fastafile)

		seqkeys = seqs.keys()
		seqkeys.sort()

		n = 0
		for chr in seqkeys:
			n += len(seqs[chr])
			
		print("Genome length = %d, # chromosomes = %d\n"%(n, len(seqkeys)))
		
		if (seqs.has_key(chromo)):
			seq = seqs[chromo]
			print("Chr[%s] = %d nt\n"%(chromo,len(seq)))
			dna = seq[chr_start:chr_end]
			print("DNA[%d:%d] = %d nt\n"%(chr_start,chr_end,len(dna)))
		else:
			print("Cannot find [%s] chromosome in %s\n"%(chromo, filename))
		print("DNA:[%s]\n"%dna)

	return dna	

###################################################################################################

def NameThatTF(name, timestep):
	n = len(name)
	c = timestep % (n+2)
	if (c >= n):
		return '.'	# u"" + chr(0xB7)
	return name[c]
	
################################################################################################### 

def Check_TF_Binding(tf_names, tf_positions, dna_pos, headers, vals, timestep, tf_counts):
	ch = None
	for tf in tf_names:
		if (not tf_positions.has_key(tf)): continue
		pos_list = tf_positions[tf]
		if (not dna_pos in pos_list): continue
		
		col_TF = GetPositionalCol("%s_bound_"%tf,  dna_pos, headers)
		if (col_TF > 0) and (vals[col_TF] > 0):	
			ch = NameThatTF(tf, timestep)
			tf_counts[dna_pos] += 1

	return ch

################################################################################################### 
def Get_TF_Name(tf_names, tf_positions, dna_pos, headers, vals):
	for tf in tf_names:
		if (not tf_positions.has_key(tf)): continue
		pos_list = tf_positions[tf]
		if (not dna_pos in pos_list): continue
		
		# found TF that can be at this position
		col_TF = GetPositionalCol("%s_bound_"%tf,  dna_pos, headers)
		if (col_TF > 0) and (vals[col_TF] > 0):	
			return tf

	return "T"

################################################################################################### 

def BuildWig(outfile, name, desc, chromo, counts, start_pos, group_size):

	outfile.write("track type=wiggle_0 name=\"%s\" description=\"%s\" visibility=full autoScale=on"%(name, desc))
	outfile.write(" color=0,100,0 altColor=0,100,0 priority=10 yLineMark=0 yLineOnOff=on\n")
	outfile.write("variableStep chrom=%s span=1\n"%(chromo))
	pos = start_pos

#	for i in xrange(DISPLAY_START,DISPLAY_END):
	for i in xrange(N_DNA):
		c = counts[i]
	#	outfile.write("%d\t%f\n"%(pos,c/100.))
		outfile.write("%d\t%f\t%d\n"%(pos,c/100.,c))
		pos += group_size
		
#end BuildWig

################################################################################################### 

def	DisplayTimeStep(vals, printing, headers, tf_list, tf_positions, tf_counts, nuc_counts, rnap_counts):
	# Globals:
	#		NT_PER_GROUP 
	
	# what is the state of each DNA position							
	tf_range   = 0
	nuc_range  = 0
	rnap_range = 0

	tf_str = ""
	nuc_str = ""
	rnap_str = ""
	rnap_size		    = params.GetInt("RNAP","RNAP_SIZE",25)
	pos_per_rnap	 	= (rnap_size + NT_PER_GROUP-1) / NT_PER_GROUP
	rnap_init_stages	= params.GetInt("RNAP","N_INIT_STAGES",2)

	pos_per_nucleosome 	= (147 + NT_PER_GROUP-1) / NT_PER_GROUP
	sideDot = "." * ((pos_per_nucleosome-3)/2)

	pos_per_tf 			= (20 + NT_PER_GROUP-1) / NT_PER_GROUP		# should get data for each TF ???
	
	lineA = "%5d:"%vals[0]
	lineB = "     :"
	lineC = [lineA]
	
	unused_chr = "~#$%^&*_;:/?><,\\|ABCDEFGHIJKLMOPQSUVWXYZ"
	
#	for dna_pos in xrange(DISPLAY_START,DISPLAY_END): #1,N_DNA):
	for dna_pos in xrange(1,N_DNA):
		ch = ' '
		# get the state of this DNA position
		col_rb  = GetPositionalCol("rnap_bound_", dna_pos, headers)
		col_nb  = GetPositionalCol("nuc_bound_",  dna_pos, headers)
		col_tb  = GetPositionalCol("TF_bound_",   dna_pos, headers)					
		col_dna = GetPositionalCol("dna_",        dna_pos, headers)
		col_ra  = GetPositionalCol("rnap_abort_", dna_pos, headers)

		if (tf_range > 0):		# Still in TF region
			# because we dont know the real range of the TF, we must see if it is really still extended
			if (   ((col_dna > 0) and (vals[col_dna] > 0))
				or ((col_tb  > 0) and (vals[col_tb]  > 0))
				or ((col_nb  > 0) and (vals[col_nb]  > 0))
				or ((col_rb  > 0) and (vals[col_rb]  > 0)) ):
				tf_range = 0
			else: # assume we are still in previous TF region				
				ch = '-'
				if (len(tf_str) > 0):
					ch = tf_str[0]
					tf_str = tf_str[1:]
				
				tf_range -= 1
				tf_counts[dna_pos] += 1
			
		if (nuc_range > 0):		# Still in NUC region
			ch = '.'
			if (len(nuc_str) > 0):
				ch = nuc_str[0]
				nuc_str = nuc_str[1:]
				
			nuc_range -= 1
			nuc_counts[dna_pos] += 1
			
		if (rnap_range > 0):		# Still in RNAP region
			ch = "'"
			if (len(rnap_str) > 0):
				ch = rnap_str[0]
				rnap_str = rnap_str[1:]
				
			rnap_range -= 1
			rnap_counts[dna_pos] += 1
			
		if   ((col_tb > 0) and (vals[col_tb] > 0)) : 		# TF bound
			tf_range = pos_per_tf	# this position is start of TF region 
			# which TF is bound? 
			# ???
			tf_str = Get_TF_Name(tf_list, tf_positions, dna_pos, headers, vals)
			ch = tf_str[0]
			tf_str = tf_str[1:]
			
			if (nuc_range > 0) or (rnap_range > 0):
				ch = '$'
				
		elif ((col_nb > 0) and (vals[col_nb] > 0)) : 		# NUC bound
			nuc_range = pos_per_nucleosome - 1	# this position is start of NUCLEOSOME region 
			nuc_counts[dna_pos] += 1
			ch = 'N'
			# which state of nucleosome occupation? 
			col_ns = GetPositionalCol("nuc_stable_",  dna_pos, headers)
			col_nb = GetPositionalCol("nuc_binding_",  dna_pos, headers)
			col_nu = GetPositionalCol("nuc_unbinding_",  dna_pos, headers)					

			if   (col_ns > 0) and (vals[col_ns] > 0):	ch = 'n'
			elif (col_nb > 0) and (vals[col_nb] > 0):	ch = 'b'
			elif (col_nu > 0) and (vals[col_nu] > 0):	ch = 'u'

			nuc_str = "(%s%c%s)"%(sideDot,ch,sideDot)
			ch = nuc_str[0]
			nuc_str = nuc_str[1:]

			if (tf_range > 0) or (rnap_range > 0):
				ch = '$'
			
		elif ((col_rb > 0) and (vals[col_rb] > 0)) : 		# RNAP bound
			rnap_range = pos_per_rnap-1	# this position is start of RNAP region 
			rnap_str = 'R'*rnap_range
			
			# which state of RNAP occupation? 
		##	col_ra  = GetPositionalCol("rnap_abort_", dna_pos, headers)
			col_rwp = GetPositionalCol("rnap_w_paused_", dna_pos, headers)
			col_rcp = GetPositionalCol("rnap_c_paused_", dna_pos, headers)
			col_rw  = GetPositionalCol("rnap_w_", dna_pos, headers)
			col_rc  = GetPositionalCol("rnap_c_", dna_pos, headers)
			col_rws = GetPositionalCol("rnap_w_scribed_", dna_pos, headers)
			col_rcs = GetPositionalCol("rnap_c_scribed_", dna_pos, headers)
		
			# watson direction
			if   ((col_rw  > 0) and (vals[col_rw]  > 0)):	rnap_str = "%s%s"%("="*rnap_range,">")
			elif ((col_rws > 0) and (vals[col_rws] > 0)):	rnap_str = "%s%s"%("="*rnap_range,"]")
			elif ((col_rwp > 0) and (vals[col_rwp] > 0)):	rnap_str = "%s%s"%("="*rnap_range,"}")
			# crick direction
			elif ((col_rc  > 0) and (vals[col_rc]  > 0)):	rnap_str = "%s%s"%("<", "="*rnap_range)
			elif ((col_rcs > 0) and (vals[col_rcs] > 0)):	rnap_str = "%s%s"%("[", "="*rnap_range)
			elif ((col_rcp > 0) and (vals[col_rcp] > 0)):	rnap_str = "%s%s"%("{", "="*rnap_range)

		##	elif ((col_ra  > 0) and (vals[col_ra]  > 0)):	rnap_str = "@%s@"%("="*(rnap_range-1))

			else:		# check the stage of initiation
				# initation
				for n in xrange(rnap_init_stages):
					col_rwi = GetPositionalCol("rnap_w_init_%d_"%n, dna_pos, headers)
					if ((col_rwi > 0) and (vals[col_rwi] > 0)): 
						rnap_str = ("%d%s"%(n,">"*rnap_range))
						break #found init stage
						
					col_rci = GetPositionalCol("rnap_c_init_%d_"%n, dna_pos, headers)
					if ((col_rci > 0) and (vals[col_rci] > 0)): 
						rnap_str = ("%s%d"%("<"*rnap_range,n))
						break #found init stage
							
			ch = rnap_str[0]
			rnap_str = rnap_str[1:]

			if (nuc_range > 0) or (tf_range > 0):
				ch = '$'

		elif ((col_ra  > 0) and (vals[col_ra]  > 0)):	
			rnap_range = pos_per_rnap-1	# this position is start of RNAP region 
			rnap_str = "@%s@"%("="*(rnap_range-1))
			ch = rnap_str[0]
			rnap_str = rnap_str[1:]

		elif ((col_dna > 0) and (vals[col_dna] < 0)):	# should not get here, NO DNA and not in another state
			chr = '!'		
			
		if (DISPLAY_START <= dna_pos <= DISPLAY_END):
			lineC.append(ch)
#			lineA += ch

	print "".join(lineC)
#	print lineA	
# end of DisplayTimeStep

################################################################################################### 

def Get_TF_Key(tf_name):
	key = 'TF_%s_SIZE'%tf_name
	return key
#end Get_TF_Key

################################################################################################### 

def Get_TF_Size(tf_name, headers, vals): 

	key = Get_TF_Key(tf_name)
	col = headers[key]
	if (col > 0): 
		size = float(vals[col])
		return int(size)
		
	return -1

#end Get_TF_Size

################################################################################################### 

def Find_TF_Bound(pos, headers, vals):  
	global tf_bound
	global N_DNA
	
	if (not tf_bound):
		tf_bound = [None]*(N_DNA+1)
		#print N_DNA, "TF_BOUND:",len(tf_bound),tf_bound
		
		for key in headers.keys():
			if (key[:3] == "TF_"):
				fields = key.split('_')		# assuming that TF definition is TF_%s_bound_%i
				if ('bound' == fields[2]):
					#print "found TF bound position:",fields
					p = int(fields[-1])  	# last field is the position
					#print "adding:", p, fields[1]
					if (not tf_bound[p]):
						tf_bound[p] = []
					tf_bound[p].append(fields[1])
					
		print N_DNA, "TF_BOUND:",len(tf_bound)
		for p in range(1000):
			if ((p < len(tf_bound)) and tf_bound[p]):
				print "\t%5d:"%p, tf_bound[p]
					
	# search through the possible TFs at the given location
	match_tf = None
	if (tf_bound[pos]):
		for tf in tf_bound[pos]:
			key = Get_TF_Key(tf)
			col = headers[key]
			
			if (float(vals[col]) > 0):
				# found a match
				if (match_tf):	
					print "Multiple TF bound at position %d, [%s][%s]"%(pos, match_tf, tf)
					# use the larger TF
					size_match = Get_TF_Size(match_tf, headers, vals)
					size_tf    = Get_TF_Size(tf, headers, vals)
					if (size_tf > size_match):
						match_tf = tf
				else:
					match_tf = tf
				
	return match_tf
	
#end Find_TF_Bound


################################################################################################### 
 
def main():

	global	N_DNA
	global 	START_POS
	global	NT_PER_GROUP
	global	DNA_section
	global	params
	global	saved_cols
	global	DISPLAY_START
	global	DISPLAY_END
	global	tf_bound
	
	tf_bound = None
		
	saved_cols = dict()

	out_filename		= None
	out_format			= "Model_Results.png"
	plot				= False
	visualize 			= False
	visualize2 			= True
	show_nucleosomes 	= False
	showtimes			= None
	random_select 		= 0
	display_range		= None
		
	paramfile   = "PARAM.INI"
	DNA_section = ""
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "d:nvpo:r:st:", ["help", "results=", "DNA=", "param="])
	except getopt.GetoptError:
		print "GetOpt errors found"
		usage()
		sys.exit(1)

	if not args:
		print "ERROR: Missing files!"
		usage()
		sys.exit(1)

	for opt, value in opts:
		#print opt, value
		if (opt == '-o'):		out_filename = value
		elif (opt == '-d'):		display_range = value
		elif (opt == '-n'):		show_nucleosomes = True
		elif (opt == '-p'):		plot = True
		elif (opt == '-v'):		visualize = True
		elif (opt == '-r'):		random_select = float(value)
		elif (opt == '-s'):		visualize2 = False
		elif (opt == '-t'):		showtimes = value
		elif opt == '--DNA':	DNA_section = value
		elif opt == '--param':	paramfile   = value
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	showtime_start = -1
	showtime_end   = sys.maxint
	if (showtimes):
		fields = showtimes.split(':')
		showtime_start = int(fields[0])
		if (len(fields) > 1):
			showtime_end   = int(fields[1])
		print "Only showing timesteps [%d..%d]"%(showtime_start,showtime_end)

	showpos_range = None
	if (display_range):
		showpos_range = [-1, sys.maxint]
		fields = display_range.split(':')
		showpos_range[0] = int(fields[0])
		if (len(fields) > 1):
			showpos_range[1] = int(fields[1])
		print "Only showing positions [%d..%d]"%(showpos_range[0],showpos_range[1])

	params = K.NOX_ParamFile(paramfile)
	print "sections:",params.sections
	
	if (DNA_section == ""):
		DNA_section = params.GetString("SRB","DNA", "DNA")
	print "processing DNA section [%s]"%DNA_section

	NT_PER_GROUP = params.GetInt(DNA_section,"GROUPING")
	
	chromo     = params.GetString(DNA_section,"CHR")
	start_pos  = params.GetInt(DNA_section,"START",0)
	end_pos    = params.GetInt(DNA_section,"END")
	if (not end_pos):
		end_pos = params.GetInt(DNA_section,"LENGTH",0)
		end_pos += start_pos
	START_POS  = start_pos
	dna        = LoadDNA()
	
	rnap_size		    = params.GetInt("RNAP","RNAP_SIZE",25)
	pos_per_rnap	 	= (rnap_size + NT_PER_GROUP-1) / NT_PER_GROUP

	pos_per_nucleosome 	= (147 + NT_PER_GROUP-1) / NT_PER_GROUP
	N_DNA				= ((end_pos-start_pos+1) + NT_PER_GROUP-1) / NT_PER_GROUP
	print "N_DNA =", N_DNA
		
	# calculate location of Start and Stop of Display line
	DISPLAY_START 	= 0
	DISPLAY_END 	= N_DNA

	start_display = params.GetInt(DNA_section,"DISPLAY_START", -1)
	if (start_display >= 0):
		DISPLAY_START 	= ((start_display-start_pos+1) + NT_PER_GROUP-1) / NT_PER_GROUP
	end_display = params.GetInt(DNA_section,"DISPLAY_END", -1)
	if (end_display >= 0):
		DISPLAY_END 	= ((end_display-start_pos+1) + NT_PER_GROUP-1) / NT_PER_GROUP
	
	if (showpos_range):
		DISPLAY_START 	= ((showpos_range[0]-start_pos+1) + NT_PER_GROUP-1) / NT_PER_GROUP
		DISPLAY_END 	= ((showpos_range[1]-start_pos+1) + NT_PER_GROUP-1) / NT_PER_GROUP
	
	# build a line with the nominal nucleosome and nominal linker sizes
	nuc_string =  "(" * (pos_per_nucleosome/2)
	if ( (pos_per_nucleosome%2) != 0):
		nuc_string += " "
	nuc_string += ")" * (pos_per_nucleosome/2)
	linker_size = params.GetInt("NUCLEOSOME","MIN_LINKER_SIZE", 20)
	linker_string = "-" * ((linker_size+NT_PER_GROUP-1) / NT_PER_GROUP)
	lineN = "-NUC-:"
	lineN += nuc_string
	while (len(lineN) < ((DISPLAY_END-DISPLAY_START+1)-len(nuc_string)-len(linker_string))):
		lineN += linker_string
		lineN += nuc_string
	print lineN
	
	print "Chromosome: %s, %d .. %d, %d nt (%d DNA positions with grouping at %d)"%(chromo, start_pos, end_pos, (end_pos-start_pos+1), N_DNA, NT_PER_GROUP)
	print "Nuclesomes cover %d positions"%pos_per_nucleosome
		
	# Get highlight region
	lineH = None
	highlite = params.GetString("SRB","HIGHLIGHT", "")
	highlite = params.GetString(DNA_section,"HIGHLIGHT", highlite)
	highlights = []
	if (len(highlite) > 0):
		hilite_list = highlite.split(";")
		for h in hilite_list:
			if (len(h) < 3): continue
			fields = h.split(",")
			print "Highlight: [%s]"%h, fields
			highlite_start = int(fields[0])
			highlite_end   = int(fields[1])
			ch = "_"
			if (len(fields) > 2):
				ch = fields[2][0]
			highlights.append([highlite_start, highlite_end, ch])
		lineH = BuildHighlighter(highlights)

	tf_list		= []
	for tf in params.GetString(DNA_section,"TF_LIST", "").split(','):
		tf_list.append(tf.strip())

	# Allocate the summary stats
	#			
	# Count the number of times a nucleosome contains each DNA position
	nuc_counts = [0]*(N_DNA+1)

	# Count the number of times a TF contains each DNA position
	tf_counts = [0]*(N_DNA+1)

	# Count the number of times a RNAP contains each DNA position
	rnap_counts = [0]*(N_DNA+1)
			
	n_selected	  = 0
	for filename in args:
	
##		# read input file
##		print "Opening bindings file [%s]"%(filename)
##		headers,values = ReadSimFile(filename)
##		print "#columns=%d, #rows=%d"%(len(headers),len(values))
			
		# Read Headers from Sim
		csvFile = open(filename, "r")
		headers = ReadSimHeader(csvFile, False)
		print "File:[%s], #columns=%d"%(filename,len(headers))

		dna_cols  = [-1]
		rnap_cols = [-1]
		nuc_cols  = [-1]
		tf_cols   = [-1]
		
		# find all the columns for DNA, RNAP, NUC, and TF bound
		for pos in range(1,N_DNA+1):
			col = GetPositionalCol("dna_", pos, headers)
			dna_cols.append(col)
			
			col_TF = GetPositionalCol("TF_bound_", pos, headers)
			tf_cols.append(col_TF)
					
			col_N = GetPositionalCol("nuc_bound_",  pos, headers)
			nuc_cols.append(col_N)
					
			col_P = GetPositionalCol("rnap_bound_", pos, headers)
			rnap_cols.append(col_P)

#		print "Found %d dna cols"% len(dna_cols),  dna_cols[1:20]
#		print "Found %d nuc cols"% len(nuc_cols),  nuc_cols[1:20]
#		print "Found %d TF cols"%  len(tf_cols),   tf_cols[1:20]
#		print "Found %d rnap cols"%len(rnap_cols), rnap_cols[1:20]

		divider = BuildDivider(N_DNA)	
				
		# Find positions for each of the TFs
		tf_pos_dict = {}
		for tf in tf_list:
			tf_pos = []
			for pos in xrange(1,N_DNA):
				col_TF = GetPositionalCol("%s_bound_"%tf,  pos, headers)
				if (col_TF > 0):
					tf_pos.append(pos)
			tf_pos_dict[tf] = tf_pos

		# for each line in the input file
		#	create display line and update summary counts
		#		read the states of DNA,NUC, TF, RNAP for each dna position
		#		for each position in dna:
		#			if (DNA[pos]):
		#				mark as unbound
		#			else if (NUC[pos]):
		#				determine the NUC state (binding, stable, unbinding)
		#				mark as nucleosome bound
		#				set range
		#			else if (TF[pos]):
		#				find which TF is bound
		#				mark as TF bound by name
		#				set range
		#			else if (RNAP[pos]):
		#				determine the RNAP state (abort,init..., paused...,scribing..,scribed.., ...)
		#				mark as RNAP state bound
		#				set range
		#			else:
		#				continue to mark active state
		#
		#	if (timestep is in range) and visualizing
		#		trim display line to area being displayed
		#		if (needed) display header
		#		display the line
		#
		
		state_char = ''
		state_range = 0
		
		v,vals = ReadSimTimestep(csvFile, 0)
		while (len(vals) > 0):
			# get current states 
			dna_state  = GetBoolStates(vals, dna_cols)
			nuc_state  = GetBoolStates(vals, nuc_cols)
			tf_state   = GetBoolStates(vals, tf_cols)
			rnap_state = GetBoolStates(vals, rnap_cols)

			line = ""


			for pos in range(1,N_DNA+1):
				if (dna_state[pos]):
					state_range = 0 
					line += ' ' # unbound DNA
					
				elif (len(nuc_state) > pos) and (nuc_state[pos]):
					#find the nuc state ...
					state_char = 'n'
					state_range = pos_per_nucleosome - 1
					line += state_char
					
					for i in range(pos_per_nucleosome):
						if (pos+i <= N_DNA):
							nuc_counts[pos+i] += 1
				#	print "NUC at ",pos
					
				elif (len(tf_state) > pos) and (tf_state[pos]):
					#find the TF bound ...

					tf = Find_TF_Bound(pos, headers, vals)
					new_range = Get_TF_Size(tf, headers, vals)		# Find TF size !!!
					
					# only update range if this is longer than prev range
					if (new_range > state_range):
						state_char = 't'
						state_range = new_range
						
					line += state_char

					for i in range(state_range):
						if (pos+i <= N_DNA):
							tf_counts[pos+i] += 1
					state_range -= 1
				#	print "TF at ",pos
					
				elif (len(rnap_state) > pos) and (rnap_state[pos]):
					#find the RNAP state ...
					state_char = 'p'
					state_range = pos_per_rnap - 1
					line += state_char
					
					for i in range(pos_per_rnap):
						if (pos+i <= N_DNA):
							rnap_counts[pos+i] += 1
				#	print "RNAP at ",pos
					
				else:
					if (state_range > 0):
						state_range -= 1
						line += state_char
						
			timestep = int(float(vals[0]))
			printing = False
			if (not showtimes or ((showtime_start <= timestep) and (showtime_end >= timestep)) ):
				printing = True

			if (printing):
				print "%5d:%s"%(timestep,line[DISPLAY_START:DISPLAY_END+1])
				n_selected += 1
				
			if (((v%50) == 0) and printing):
				print divider
				if (lineH): print lineH			

			DisplayTimeStep(vals, printing, headers, tf_list, tf_positions, tf_counts, nuc_counts, rnap_counts)

			v,vals = ReadSimTimestep(csvFile, v)
			# 
				
		print "Processed %d timesteps"%v

	#
	# Print summary information
	#

	#
	# TF Summary
	#
	
	# changes counts to % of the time in a TF
	print "Selected:", n_selected
	for n in xrange(N_DNA+1):
		tf_counts[n] = int(tf_counts[n]*100./n_selected)
#	Print_Counts(tf_counts, "TF bound %")
	mean = np.average(tf_counts)
	sd   = np.std(tf_counts)
	print "TF Bound Mean=%f, SD=%f [%f,%f]"%(mean, sd, mean-sd, mean+sd)
	Print_Percent_Graph2(tf_counts[DISPLAY_START:DISPLAY_END+1], "TF Bound %",mean)
	if (lineH): print lineH			

	#
	# Nucleosome Summary
	#
	
	# changes counts to % of the time in a nucleosome
	nuc_percent = [0] * len(nuc_counts)
	for n in xrange(N_DNA+1):
		nuc_percent[n] = int(nuc_counts[n]*100./n_selected)

# 	Print_Counts(nuc_percent[DISPLAY_START:DISPLAY_END+1], "Nucleosome %")

#	# Output the Nuc positioning as a WIG file
#	wig_filename = "%s_NUC_Occupancy.wig"%DNA_section
#	outfile = open(wig_filename, "w")
#	BuildWig(outfile, "Nucleosome Occupancy", "PlotModelResults:%s"%DNA_section, chromo, nuc_percent, START_POS, NT_PER_GROUP)
#	outfile.close()
	
	mean = np.average(nuc_counts)
	median = np.median(nuc_counts)
	sd   = np.std(nuc_counts)
	print "Mean=%f, SD=%f [%f,%f] Median=%f"%(mean, sd, mean-sd, mean+sd, median)
	Print_Percent_Graph2(nuc_percent[DISPLAY_START:DISPLAY_END+1], "Nucleosome Occupancy %",mean)
	if (lineH): print lineH			
	
#	print lineN				
# 
# 	# Output the Nuc positioning as a WIG file
# 	for n in xrange(N_DNA+1):
# 		nuc_counts[n] -= mean #adjust by the mean to get -values to +values
# 	wig_filename = "%s_NUC_COUNTS.wig"%DNA_section
# 	outfile = open(wig_filename, "w")
# 	BuildWig(outfile, "Nucleosome Occupancy", "PlotModelResults:%s"%DNA_section, chromo, nuc_counts, START_POS, NT_PER_GROUP)
# 	outfile.close()
# 	

	if (False):
		#
		# Show the nucleosome binding probabilities			
		#
		NUCLEOSOME_ON_RATE  = params.GetFloat("NUCLEOSOME","ON_RATE", 1.0)
		NUCLEOSOME_OFF_RATE = params.GetFloat("NUCLEOSOME","OFF_RATE",1.0)
		
		prob_file = params.GetString("NUCLEOSOME","NUC_PROB_FILE")
		prob_file = params.GetString(DNA_section,"NUC_PROB_FILE",prob_file)		# override filename
		if (prob_file):
			positional_nuc_rates = SRB_Utils.Calc_WASSON_Nucleosome_Rates(prob_file, dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE)
	
			on_vals = []
			for k in xrange(DISPLAY_START, DISPLAY_END):
				on_vals.append( positional_nuc_rates[k][0] * 100 )
	
			mean = np.average(on_vals)
			Print_Percent_Graph2(on_vals, "Nucleosome Positional Probability:",mean, 100)

#
if __name__ == '__main__':
	main()
