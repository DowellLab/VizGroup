# -*- coding: utf-8 -*-

# 
#
#Copyright (2011) University of Colorado
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
	print '   Plot the results of model'

###################################################################################################

###################################################################################################
# ReadCSVFile(filename)
# 	Read header from first line
#	Read values
#
def ReadCSVFile(filename, verbose=False):
	headers = dict()
	values  = list()

	csvFile = open(filename, "r")
	line = csvFile.readline()
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

#	lines = csvFile.readlines()
#	n_lines = len(lines)
	n = 0
	line = csvFile.readline()
	while (line and (len(line) > 0)):
#	for line in lines:
		if (len(line) > 2) and (line[0] != '#'):

			if (n%100 == 0):
				#sys.stdout.write("\r%10d of %d lines parsed"%(n, n_lines))
				sys.stdout.write("\r%10d lines parsed"%(n))
				sys.stdout.flush()
			n += 1

			line = line.strip()
			fields = line.split(",")
			vals = []
			for f in fields:
				try:
					vals.append(float(f))
				except:
					print "Error (reported from %s) [%s]"%("ReadCSVFile",f)
					vals.append(0.0)
			values.append(vals)

		line = csvFile.readline()

	sys.stdout.write("\r%10d lines parsed"%(n))
	sys.stdout.flush()
	if verbose:
		print "read %d lines"%n

	return headers, values
#end ReadCSVFile

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
# ReadSimTimestep(file, n_lines_processed)
#	Read values from next line in file
#	Parse the line
#	Return values
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
			line = line.strip()
			fields = line.split(",")
			vals = []
			for f in fields:
				try:
					vals.append(float(f))
				except:
					print "Error (reported from %s, line:%d) [%s]"%("ReadSimTimestep",n, f)
					vals.append(0.0)
			return n,vals

		line = file.readline()

	# only get here if end of file
	if (verbose):
		sys.stdout.write("\r%10d lines parsed"%(n))
		sys.stdout.flush()
	return n,[]

#end of ReadSimTimestep

###################################################################################################
# ReadSimFile(filename)
# 	Read header from first line
#	Read values
#
def ReadSimFile(filename, verbose=False):
	values  = list()

	csvFile = open(filename, "r")

	headers = ReadSimHeader(csvFile, verbose)

	n = 0
	vals = ReadSimTimestep(csvFile, n)
	while (len(vals) > 0):
		values.append(vals)
		n,vals = ReadSimTimestep(csvFile, n)

	if verbose:
		print "read %d lines"%n

	return headers, values
#end ReadSimFile
###################################################################################################
def PrintBargraph(out_filename, data1, data2, title):

	fig = P.figure(figsize=(20,8))
 	ax  = fig.add_subplot(111)
	fig.subplots_adjust(bottom=.2, top=0.96, left=0.04, right=0.96)

	ind = np.arange(len(data1))    # the x locations for the groups
	width = 0.5       # the width of the bars: can also be len(x) sequence

	p1 = ax.bar(ind,       data1, width, color='r')
	p2 = ax.bar(ind+width, data2, width, color='y')

	N = min(81,len(data1))
 	xticks = P.arange((N+9)/10 + 3)
 	xticks *= 10;
 	xticks[-1] = 64+1
 	xticks[-2] = 54+1
 	xticks[-3] = 15+1
	ax.set_xticks(xticks)

	xlabels = [""] * len(xticks)
	for i in xrange(len(xlabels)):
		xlabels[i] = "%d"%xticks[i]
	xlabels[-1] = "Full IME4"
	xlabels[-2] = "Pause Site"
	xlabels[-3] = "Pause Site"
	ax.set_xticklabels(xlabels, size=12, rotation=-50)

#	ax.annotate('Pause Here', xy=(15, .1),  xycoords='data',
#                xytext=(0, 0), textcoords='offset points',
#                arrowprops=dict(arrowstyle="->")
#                )
#
	ax.set_xlabel("Position on DNA")
	ax.set_ylabel('# of transcripts')
	ax.set_title(title)
	ax.legend( (p1[0], p2[0]), ('Sense', 'Anti-sense') )

#	P.savefig(out_filename)

#	P.show()
#end end of PrintBargraph
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
	global saved_cols
	c = -2
	cstr = "%s%04d"%(prefix,col)
	if (saved_cols.has_key(cstr)):
		return saved_cols[cstr]

	if cstr in headers:
		c = headers[cstr]
#	print "GetPositionalCol(%s)==>%d"%(cstr,c)
#	if (c < 0):
#		print "GetPositionalCol(%s)==>%d"%(cstr,c)
	saved_cols[cstr] = c
	#print "added [%s] at col: %d"%(cstr,c)

	return c
#end GetCol
###################################################################################################

def	Print_RNAP_Results(valsStart, valsEnd, headers):
	col_rnap  = GetCol("rnap", headers)
	print "# of RNAP at start", valsStart[col_rnap], "# of RNAP at end", valsEnd[col_rnap]
	col_init  = GetCol("RNAP_INIT", headers)
	col_elong = GetCol("RNAP_ELONGATED", headers)
	if (col_init > 0):
		ratio = 0
		if (valsEnd[col_init] > 0):
			ratio = 100.*valsEnd[col_elong]/valsEnd[col_init]
		print "INIT = %d, Elongated = %d, Ratio=%8.4f%%"%(valsEnd[col_init],valsEnd[col_elong], ratio)
#end Print_RNAP_Results
###################################################################################################

def	Print_DEBUG_Results(vals, headers, names):
	line = "DEBUG"
	for name in names:
		if (name[0] == "#"):
			# this is a summation of cols
			cols = [0]*(len(vals)+1)
			GetMatchingCols(name[1:], headers, vals, cols)
			val = 0
			for c in cols:
				val += c
		else:
			col  = GetCol(name, headers)
			val = -1
			if (col > 0):
				val = vals[col]

		line += " : %s = %d"%(name,val)

	print "%s"%line
#end Print_DEBUG_Results
###################################################################################################
def	Print_DEBUG_Counts(vals, headers, name, N_DNA):
	divider = BuildDivider(N_DNA)

	line1 = "     :"
	line2 = "     :"
	line3 = "     :"
	print "Counts for [%s]:"%name
	for i in xrange(1,N_DNA):
		# find item for that position
		col = GetPositionalCol(name,i,headers)
		val = 0
		if (col > 0):
			val = vals[col]

		if (val > 0):
			line3 += "%d"%(val%10)			# 1's in line 3
		else:
			line3 += "_"

		if (val >= 10):
			line2 += "%d"%(val/10%10)		# 10's in line 2
		else:
			line2 += " "

		if (val >= 100):
			line1 += "%d"%(val/100%10)		# 100's in line 1
		else:
			line1 += " "

	print line1
	print line2
	print line3
	print divider
# end of Print_DEBUG_Counts

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
def	Print_Percent_Graph2(counts, title, mean=0):
	if (len(counts) == 0): return

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

def OLD_BuildDivider(N_DNA):
	line1 = "     :"
	line2 = "     :"
	for dna_pos in xrange(1,N_DNA):
		line2 += "%d"%(dna_pos%10)
		if ((dna_pos%10) == 0):
			line1 += "%10d"%((dna_pos*NT_PER_GROUP+START_POS)/100)
	divider =  line1
	divider += "\n"
	divider += line2
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

def LoadDNA(verbose=False):
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
		if verbose:
			print ("Loading fasta: [%s]\n"%fastafile)

		seqs = Fasta.load(fastafile)

		seqkeys = seqs.keys()
		seqkeys.sort()

		n = 0
		for chr in seqkeys:
			n += len(seqs[chr])
		if verbose:
			print("Genome length = %d, # chromosomes = %d\n"%(n, len(seqkeys)))

		if (seqs.has_key(chromo)):
			seq = seqs[chromo]
			if verbose:
				print("Chr[%s] = %d nt\n"%(chromo,len(seq)))
			dna = seq[chr_start:chr_end]
			if verbose:
				print("DNA[%d:%d] = %d nt\n"%(chr_start,chr_end,len(dna)))
		else:
			if verbose:
				print("Cannot find [%s] chromosome in %s\n"%(chromo, filename))
		if (verbose):
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
		col_TF = GetPositionalCol("TF_%s_bound_"%tf,  dna_pos, headers)
		if (col_TF > 0) and (vals[col_TF] > 0):
			return tf

	return "T"

###################################################################################################
def Build_TF_Sizes(headers, vals):
	# search the headers for TF_(.*)_SIZE
	# add the name to TF_Sizes with corresponding col value
	sizes = {}
	for h in headers.keys():
	#	if (h[0] == 'T'): print "checking:",h
		m = re.match('^TF_(.*)_SIZE$',h)
		if (m):
			i = headers[h]
			#print "Found TF [%s] at %d = %s"%(m.group(0),i, vals[i])
			sizes[m.group(0)] = vals[i]

	return sizes

###################################################################################################

def BuildWig(outfile, name, desc, chromo, counts, start_pos, group_size):

	outfile.write("track type=wiggle_0 name=\"%s\" description=\"%s\" visibility=full autoScale=on"%(name, desc))
	outfile.write(" color=0,100,0 altColor=0,100,0 priority=10 yLineMark=0 yLineOnOff=on\n")
	outfile.write("variableStep chrom=%s span=%d\n"%(chromo, group_size))
	pos = start_pos

#	for i in xrange(DISPLAY_START,DISPLAY_END):
	for i in xrange(N_DNA):
		c = counts[i]
		#outfile.write("%d\t%f\n"%(pos,c/100.))
		outfile.write("%d\t%f\t%d\n"%(pos,c/100.,c))
		pos += group_size

#end BuildWig

###################################################################################################

def	DisplayTimeStep(vals, printing, headers, tf_list, tf_positions, tf_counts, nuc_counts, nuc_core_counts, rnap_counts,
					   tf_named_counts, tf_sizes, f_objects):
	# Globals:
	#		NT_PER_GROUP

	# what is the state of each DNA position
	tf_range   = 0
	nuc_range  = 0
	nuc_core_range  = 0
	rnap_range = 0

	tf_str = ""
	nuc_str = ""
	rnap_str = ""
	rnap_size		    = params.GetInt("RNAP","RNAP_SIZE",25)
	pos_per_rnap	 	= (rnap_size + NT_PER_GROUP-1) / NT_PER_GROUP
	rnap_init_stages	= params.GetInt("RNAP","N_INIT_STAGES",2)

	nuc_size		    = params.GetInt("Nucleosome","SIZE",147)
	pos_per_nucleosome 	= (nuc_size + NT_PER_GROUP-1) / NT_PER_GROUP
	sideDotL = "." * ((pos_per_nucleosome-3)/2)
	sideDotR = "." * ((pos_per_nucleosome-3+1)/2)

	nuc_core_size	    = params.GetInt("Nucleosome","SIZE",80)
	pos_per_nucleosome_core 	= (nuc_core_size + NT_PER_GROUP-1) / NT_PER_GROUP
	sideDotCoreL = "." * ((pos_per_nucleosome_core-3)/2)
	sideDotCoreR = "." * ((pos_per_nucleosome_core-3+1)/2)

	pos_per_tf 			= (20 + NT_PER_GROUP-1) / NT_PER_GROUP		# should get data for each TF ???

	lineA = "%5d:"%vals[0]
	lineB = "     :"
	#TODO: CHANGE THIS BACK TO [lineA]
	lineC = [lineA]
	lineC = []

	unused_chr = "~#$%^&*_;:/?><,\\|ABCDEFGHIJKLMOPQSUVWXYZ"

	# List of all objects attached to the DNA at the current timestep
	# Each object is a tuple containing (type, subtype, pos, length)
	attached_objects = []

	#sys.stderr.write('N_DNA = %s\n' % str(N_DNA))

#	for dna_pos in xrange(DISPLAY_START,DISPLAY_END): #1,N_DNA):
	for dna_pos in xrange(1,N_DNA):
		ch = ' '
		# get the state of this DNA position
		col_rb  = GetPositionalCol("rnap_bound_", dna_pos, headers)
		col_nb  = GetPositionalCol("nuc_bound_",  dna_pos, headers)
		col_ncb = GetPositionalCol("nuc_core_bound_",  dna_pos, headers)
		col_tb  = GetPositionalCol("TF_bound_",   dna_pos, headers)
		col_dna = GetPositionalCol("dna_",        dna_pos, headers)
		col_ra  = GetPositionalCol("rnap_abort_", dna_pos, headers)

		# if col_rb * col_nb * col_ncb * col_tb * col_ra < 0:
		# 	sys.stderr.write('\n\n\nPOSITION %i:\n' %dna_pos)
		# 	sys.stderr.write('col_rb = %s\n' % col_rb)
		# 	sys.stderr.write('col_nb = %s\n' % col_nb)
		# 	sys.stderr.write('col_ncb = %s\n' % col_ncb)
		# 	sys.stderr.write('col_tb = %s\n' % col_tb)
		# 	sys.stderr.write('col_dna = %s\n' % col_dna)
		# 	sys.stderr.write('col_ra = %s\n' % col_ra)

		if (tf_range > 0):		# Still in TF region
			# because we dont know the real range of the TF, we must see if it is really still extended
			#print 'pos ' + str(dna_pos) + 'tf_range > 0'
			if (   ((col_dna > 0) and (vals[col_dna] > 0))
				or ((col_tb  > 0) and (vals[col_tb]  > 0))
				or ((col_nb  > 0) and (vals[col_nb]  > 0))
				or ((col_ncb  > 0) and (vals[col_ncb]  > 0))
				or ((col_rb  > 0) and (vals[col_rb]  > 0)) ):
				tf_range = 0
			else: # assume we are still in previous TF region
				ch = '-'
				if (len(tf_str) > 0):
					ch = tf_str[0]
					tf_str = tf_str[1:]
					tf_named_counts[dna_pos] += 1

				tf_range -= 1
				tf_counts[dna_pos] += 1

		if (nuc_range > 0):		# Still in NUC region
			#print 'pos ' + str(dna_pos) + 'nuc_range > 0'
			ch = '.'
			if (len(nuc_str) > 0):
				ch = nuc_str[0]
				nuc_str = nuc_str[1:]

			nuc_range -= 1
			nuc_counts[dna_pos] += 1

		if (nuc_core_range > 0):		# Still in NUC region
			#print 'pos ' + str(dna_pos) + 'nuc_core_range > 0'
			ch = '.'
			if (len(nuc_str) > 0):
				ch = nuc_str[0]
				nuc_str = nuc_str[1:]

			nuc_core_range -= 1
			nuc_core_counts[dna_pos] += 1

		if (rnap_range > 0):		# Still in RNAP region
			#print 'pos ' + str(dna_pos) + 'rnap_range > 0'
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
			attached_objects.append(('Transcription_Factor', tf_str, dna_pos, tf_range))

			ch = tf_str[0]
			tf_str = tf_str[1:]

			if (len(tf_str) > 0):
				tf_named_counts[dna_pos] += 1
			tf_counts[dna_pos] += 1

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

			if   (col_ns > 0) and (vals[col_ns] > 0):
				ch = 'n'
				attached_objects.append(('Nucleosome', 'Stable', dna_pos, nuc_range+1))
			elif (col_nb > 0) and (vals[col_nb] > 0):
				ch = 'b'
				attached_objects.append(('Nucleosome', 'Binding', dna_pos, nuc_range+1))
			elif (col_nu > 0) and (vals[col_nu] > 0):
				ch = 'u'
				attached_objects.append(('Nucleosome', 'Unbinding', dna_pos, nuc_range+1))

			nuc_str = "(%s%c%s)"%(sideDotL,ch,sideDotR)
			ch = nuc_str[0]
			nuc_str = nuc_str[1:]

			if (tf_range > 0) or (rnap_range > 0):
				ch = '$'

		elif ((col_ncb > 0) and (vals[col_ncb] > 0)) : 		# NUC bound
			nuc_core_range = pos_per_nucleosome_core - 1	# this position is start of NUCLEOSOME region
			nuc_core_counts[dna_pos] += 1
			ch = 'N'
			# which state of nucleosome occupation?
			col_ns = GetPositionalCol("nuc_core_stable_",  dna_pos, headers)
			col_nb = GetPositionalCol("nuc_core_binding_",  dna_pos, headers)
			col_nu = GetPositionalCol("nuc_core_unbinding_",  dna_pos, headers)

			if   (col_ns > 0) and (vals[col_ns] > 0):
				ch = 'n'
				attached_objects.append(('Nucleosome', 'Stable', dna_pos, nuc_core_range+1))
			elif (col_nb > 0) and (vals[col_nb] > 0):
				ch = 'b'
				attached_objects.append(('Nucleosome', 'Binding', dna_pos, nuc_core_range+1))
			elif (col_nu > 0) and (vals[col_nu] > 0):
				ch = 'u'
				attached_objects.append(('Nucleosome', 'Unbinding', dna_pos, nuc_core_range+1))

			nuc_str = "(%s%c%s)"%(sideDotCoreL,ch.upper(),sideDotCoreR)
			ch = nuc_str[0]
			nuc_str = nuc_str[1:]

			if (tf_range > 0) or (rnap_range > 0):
				ch = '$'

		elif ((col_rb > 0) and (vals[col_rb] > 0)) : 		# RNAP bound
			rnap_range = pos_per_rnap-1	# this position is start of RNAP region
			rnap_str = 'R'*(rnap_range+1)

			# which state of RNAP occupation?
		##	col_ra  = GetPositionalCol("rnap_abort_", dna_pos, headers)
			col_rwp = GetPositionalCol("rnap_w_paused_", dna_pos, headers)
			col_rcp = GetPositionalCol("rnap_c_paused_", dna_pos, headers)
			col_rw  = GetPositionalCol("rnap_w_", dna_pos, headers)
			col_rc  = GetPositionalCol("rnap_c_", dna_pos, headers)
			col_rws = GetPositionalCol("rnap_w_scribed_", dna_pos, headers)
			col_rcs = GetPositionalCol("rnap_c_scribed_", dna_pos, headers)

			# watson direction
			if   ((col_rw  > 0) and (vals[col_rw]  > 0)):
				rnap_str = "%s%s"%("="*rnap_range,">")
				attached_objects.append(('Transcriptional_Machinery', 'Watson', dna_pos, rnap_range+1))
			elif ((col_rws > 0) and (vals[col_rws] > 0)):
				rnap_str = "%s%s"%("="*rnap_range,"]")
				attached_objects.append(('Transcriptional_Machinery', 'Watson-Transcribed', dna_pos, rnap_range+1))
			elif ((col_rwp > 0) and (vals[col_rwp] > 0)):
				rnap_str = "%s%s"%("="*rnap_range,"}")
				attached_objects.append(('Transcriptional_Machinery', 'Watson-Paused', dna_pos, rnap_range+1))
			# crick direction
			elif ((col_rc  > 0) and (vals[col_rc]  > 0)):
				rnap_str = "%s%s"%("<", "="*rnap_range)
				attached_objects.append(('Transcriptional_Machinery', 'Crick', dna_pos, rnap_range+1))
			elif ((col_rcs > 0) and (vals[col_rcs] > 0)):
				rnap_str = "%s%s"%("[", "="*rnap_range)
				attached_objects.append(('Transcriptional_Machinery', 'Crick-Transcribed', dna_pos, rnap_range+1))
			elif ((col_rcp > 0) and (vals[col_rcp] > 0)):
				rnap_str = "%s%s"%("{", "="*rnap_range)
				attached_objects.append(('Transcriptional_Machinery', 'Crick-Paused', dna_pos, rnap_range+1))
		##	elif ((col_ra  > 0) and (vals[col_ra]  > 0)):	rnap_str = "@%s@"%("="*(rnap_range-1))

			else:		# check the stage of initiation
				# initation
				for n in xrange(rnap_init_stages):
					col_rwi = GetPositionalCol("rnap_w_init_%d_"%n, dna_pos, headers)
					if ((col_rwi > 0) and (vals[col_rwi] > 0)):
						rnap_str = ("%d%s"%(n,">"*rnap_range))
						attached_objects.append(('Transcriptional_Machinery', 'Watson-Init%d' % n, dna_pos, rnap_range+1))
						break #found init stage

					col_rci = GetPositionalCol("rnap_c_init_%d_"%n, dna_pos, headers)
					if ((col_rci > 0) and (vals[col_rci] > 0)):
						rnap_str = ("%s%d"%("<"*rnap_range,n))
						attached_objects.append(('Transcriptional_Machinery', 'Crick-Init%d' % n, dna_pos, rnap_range+1))
						break #found init stage


			print 'RNAP str: ' + rnap_str
			ch = rnap_str[0]
			rnap_str = rnap_str[1:]

			if (nuc_range > 0) or (tf_range > 0):
				ch = '$'

		elif ((col_ra  > 0) and (vals[col_ra]  > 0)):
			rnap_range = pos_per_rnap-1	# this position is start of RNAP region
			rnap_str = "@%s@"%("="*(rnap_range-1))
			attached_objects.append(('Transcriptional_Machinery', 'Abort', dna_pos, rnap_range+1))
			ch = rnap_str[0]
			rnap_str = rnap_str[1:]

		elif ((col_dna > 0) and (vals[col_dna] < 0)):	# should not get here, NO DNA and not in another state
			chr = '!'

		#TODO: REMOVE "TRUE OR"
		if True or (DISPLAY_START <= dna_pos <= DISPLAY_END):
			lineC.append(ch)
#			lineA += ch

	if (printing):
		print "".join(lineC)
		print attached_objects
#		print lineA

	if f_objects and attached_objects:
		if f_objects.tell() > 0:
			f_objects.write('\n')
		f_objects.write(str(attached_objects))

# end of DisplayTimeStep

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

	saved_cols = dict()

	out_filename		= None
	out_format			= "Model_Results.png"
	filename1 			= ""
	plot				= False
	visualize 			= False
	visualize2 			= True
	show_nucleosomes 	= False
	showtimes			= None
	random_select 		= 0
	display_range		= None
	writeWIG			= False
	roman				= False
	verbose				= False
	objects_file		= None

	paramfile   = "PARAM.INI"
	DNA_section = ""

	try:
		opts, args = getopt.getopt(sys.argv[1:], "d:nvpo:r:st:wR", ["help", "results=", "DNA=", "param=", "verbose=", "objs-file="])
	except getopt.GetoptError:
		print "GetOpt errors found"
		usage()
		sys.exit(1)

	if not args:
		print "ERROR: Missing files!"
		usage()
		sys.exit(1)

	filename1 = args[0]

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
		elif (opt == '-w'):		writeWIG = True
		elif (opt == '-R'):		roman = True
		elif opt == '--DNA':	DNA_section = value
		elif opt == '--param':	paramfile   = value
		elif opt == '--verbose':	verbose   = True
		elif opt == '--objs-file': objects_file = value
		else:
			print "Unhandled opt [%s][%s]"%(opt,value)

	# If set, start writing to objects output file
	f_objects = open(objects_file, 'w') if objects_file else None

	showtime_start = -1
	showtime_end   = sys.maxint
	if (showtimes):
		fields = showtimes.split(':')
		showtime_start = int(fields[0])
		if (len(fields) > 1):
			showtime_end   = int(fields[1])
		if verbose:
			print "Only showing timesteps [%d..%d]"%(showtime_start,showtime_end)

	showpos_range = None
	if (display_range):
		showpos_range = [-1, sys.maxint]
		fields = display_range.split(':')
		showpos_range[0] = int(fields[0])
		if (len(fields) > 1):
			showpos_range[1] = int(fields[1])
		if verbose:
			print "Only showing positions [%d..%d]"%(showpos_range[0],showpos_range[1])

	params = K.NOX_ParamFile(paramfile)
	if verbose:
		print "sections:",params.sections

	if (DNA_section == ""):
		DNA_section = params.GetString("SRB","DNA", "DNA_SAMPLE")
	if verbose:
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
	if verbose:
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

	# Show the nucleosome probabilities
	NUCLEOSOME_ON_RATE  = params.GetFloat("NUCLEOSOME","ON_RATE", 1.0)
	NUCLEOSOME_OFF_RATE = params.GetFloat("NUCLEOSOME","OFF_RATE",1.0)

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
	if verbose:
		print lineN

#	occupancy_file = "./DATA/updated_0308_yeast_basepair_occupancy.tab"
#	print "Reading nuc occupancy file {%s}"%occupancy_file
#	occupancy = SRB_Utils.Read_Nuc_Occupancy_File(occupancy_file, chromo, start_pos, end_pos)
#
# 	occ_vals = []
# 	pos = 1
# 	for i in xrange(N_DNA):
# 		val = 0
# 		for n in xrange(NT_PER_GROUP):
# 			if ((pos+n) < len(occupancy)):
# 				entry = occupancy[pos+n]
# 				if (val < entry[1]*100):
# 					val = int(entry[1]*100)
# 		occ_vals.append(val)
# 		pos += NT_PER_GROUP
# #
# #	mean = np.average(occ_vals)
# #	Print_Percent_Graph2(occ_vals, "Segal Predicted Occupancy %",mean)
#
# 	# Get the position dependent OFF rates based on DNA sequence
# 	prob_file = params.GetString("NUCLEOSOME","NUC_PROB_FILE")
# 	prob_file = params.GetString(DNA_section,"NUC_PROB_FILE",prob_file)		# override filename
# 	if (prob_file):
# 		positional_nuc_rates = SRB_Utils.Calc_WASSON_Nucleosome_Rates(prob_file, dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE)
# 	elif (prob_file):
# 		positional_nuc_rates = SRB_Utils.Calc_Nucleosome_Rates_From_File(prob_file, chromo, start_pos, end_pos, dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE, NT_PER_GROUP, START_POS)
# 	else:
# 		positional_nuc_rates = SRB_Utils.Calc_Nucleosome_Rates(dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE)
#
# 	on_vals = []
# #	for k in xrange(1, len(positional_nuc_rates)):
# 	for k in xrange(DISPLAY_START, DISPLAY_END):
# 		on_vals.append( positional_nuc_rates[k][0] )
# 	Print_Percent_Graph_LOG(on_vals, "Nucleosome Positional Probability:")
#
# 	print "Chromosome: %s, %d .. %d, %d nt (%d DNA positions with grouping at %d)"%(chromo, start_pos, end_pos, (end_pos-start_pos+1), N_DNA, NT_PER_GROUP)
# 	print "Nuclesomes cover %d positions"%pos_per_nucleosome

	trailer = "." * (pos_per_nucleosome-1)
	sideDot = "." * ((pos_per_nucleosome-3)/2)
	sideUnd = "_" * ((pos_per_nucleosome-3)/2)
	sideDsh = "-" * ((pos_per_nucleosome-3)/2)
	replacement = "(%s%c%s)" # replacement%(side,'c',side)
	replacementN = replacement%(sideDot,'n',sideDot)
	replacementB = replacement%(sideDsh,'b',sideDsh)
	replacementU = replacement%(sideUnd,'u',sideUnd)
	if verbose:
		print "Trailer:[%s]"%trailer
		print "Replacement Format: [%s]"%replacement

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
			if verbose:
				print "Highlight: [%s]"%h, fields
			highlite_start = int(fields[0])
			highlite_end   = int(fields[1])
			ch = "_"
			if (len(fields) > 2):
				ch = fields[2][0]
			highlights.append([highlite_start, highlite_end, ch])
		lineH = BuildHighlighter(highlights)

	debug_names = []
#	debug_names = [	"rnap","RNAP_ABORTED","RNAP_INIT","RNAP_ELONGATED","TATA", "#TF_bound_", "#TATA_bound_",
#					"TI_COLLISION", "TI_COLLISION_SD", "RNAP_COMPLETED_W", "RNAP_COMPLETED_C",
#					"#RNAP_STARTED_W_", "#RNAP_STARTED_C_"]

	tf_list		= []
	for tf in params.GetString(DNA_section,"TF_LIST", "").split(','):
		tf_list.append(tf.strip())
	for tf in params.GetString(DNA_section,"TF_DISPLAY_LIST", "").split(','):
		tf_list.append(tf.strip())

#	tf_list		= [ "GAL4"]
#	tf_list		= [ "MCM1","FKH2"]
#	tf_list		= [ "ACE2","ADR1","ARG80","ARG81","ARR1","BAS1","CHA4","CIN5","CRZ1","CST6"
#					 ,"HAP2","HAP3","HAP4","HAP5","MAC1","MBP1","MCM1","MET28","MET31","MOT3"
#					 ,"MSN2","MSN4","NDD1","NRG1","OPI1","PHD1","PHO2","PHO4","REB1","RIM101"
#					 ,"RLM1","RME1","RTG3","SPT2","SPT23","STB1","STB2","STB5","STE12","SUM1"
#					 ,"SUT1","SWI4","SWI5","SWI6","TEC1","UGA3","XBP1","YAP5","YAP6","YDR026C"
#					 ,"YER051W","YHP1","A1_ALPHA2","RSC3" 	]

	if (True):
		# Get the position dependent OFF rates based on DNA sequence
		prob_file = params.GetString("NUCLEOSOME","NUC_PROB_FILE")
		prob_file = params.GetString(DNA_section,"NUC_PROB_FILE",prob_file)		# override filename
		if (prob_file):
			positional_nuc_rates, pos_prob = K.Calc_WASSON_Nucleosome_Rates(prob_file, dna, NT_PER_GROUP, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE)
			# changes prob to %
			for n in xrange(len(pos_prob)):
				pos_prob[n] = int(pos_prob[n]*100.)
			# display nuc on rates:
			if verbose:
				print "Nucleosome Prob shown as Percent of maximum value:"
			Print_Percent_Graph2(pos_prob[DISPLAY_START:DISPLAY_END+1], "Nuc Binding Prob % of Max",0.)
			if (lineH): print lineH
			# Create a WIG file for this prob set
			if (True):
				wig_filename = "NUC_Probability.wig"
				if verbose:
					print "Creating WIG file with Nucleosome Proability:[%s]"%wig_filename
				outfile = open(wig_filename, "w")
				BuildWig(outfile, "Nucleosome Probability", "PlotModelResults:%s"%DNA_section, 'II', pos_prob, START_POS, NT_PER_GROUP)
				outfile.close()


	n_selected	  = 0
	nuc_full_counts = nuc_core_counts = tf_counts = rnap_counts = None
	for filename in args:

##		# read input file
##		print "Opening bindings file [%s]"%(filename)
##		headers,values = ReadSimFile(filename)
##		print "#columns=%d, #rows=%d"%(len(headers),len(values))

		# Read Headers from Sim
		csvFile = open(filename, "r")
		headers = ReadSimHeader(csvFile)
		values = []
		if verbose:
			print "File:[%s], #columns=%d"%(filename,len(headers))


		if (nuc_full_counts == None):
			# Count the number of times a nucleosome contains each DNA position
			nuc_full_counts = [0]*(N_DNA+1)

			# Count the number of times a nucleosome contains each DNA position
			nuc_core_counts = [0]*(N_DNA+1)

			# Count the number of times a TF contains each DNA position
			tf_counts = [0]*(N_DNA+1)
			tf_named_counts = [0]*(N_DNA+1)

			# Count the number of times a RNAP contains each DNA position
			rnap_counts = [0]*(N_DNA+1)

###		if (visualize):
		divider = BuildDivider(N_DNA)
		# CalcPositions for each of the TFs
		tf_pos_dict = {}
		for tf in tf_list:
			tf_pos = []
			for pos in xrange(1,N_DNA):
				col_TF = GetPositionalCol("TF_%s_bound_"%tf,  pos, headers)
				if (col_TF > 0):
					tf_pos.append(pos)
			tf_pos_dict[tf] = tf_pos
	#	print "TF position list:"
	#	for tf,poslist in tf_pos_dict:
	#		print "\t",tf, len(poslist), poslist

		# Create time vs DNA positional polt
		v = 0
		if (visualize and visualize2 and ((v%50) == 0)):
			print divider
			if (lineH): print lineH
		v,vals = ReadSimTimestep(csvFile, v)

		# Find the lenth of each named TF
		tf_sizes = Build_TF_Sizes(headers, vals)

		while (len(vals) > 0):
			values.append(vals)

			timestep = int(float(vals[0]))
			printing = False
			if (visualize):
				if (not showtimes or ((showtime_start <= timestep) and (showtime_end >= timestep)) ):
					printing = True
				if (random_select != 0):
					printing = False

			if ( (random_select == 0) or (random.random() < (random_select/100.)) ) and \
				 (not showtimes or ((showtime_start <= timestep) and (showtime_end >= timestep)) ):
					n_selected += 1
					DisplayTimeStep(vals, printing, headers, tf_list, tf_pos_dict, tf_counts, nuc_full_counts,
									nuc_core_counts, rnap_counts, tf_named_counts, tf_sizes, f_objects)

			if (visualize and visualize2 and ((v%50) == 0) and printing):
			#	Print_DEBUG_Results(vals, headers, debug_names)
				print divider
				if (lineH): print lineH

			v,vals = ReadSimTimestep(csvFile, v)
			# end of values enumeration loop
		if verbose:
			print "Processed %d timesteps"%v

	# Print the Final stats
	#
	if verbose:
		print "\nProcessed %d timesteps from %d files"%(n_selected,len(args))

	if verbose:
		Print_RNAP_Results(values[0],  values[-1], headers)
	# 	Print_DEBUG_Results(values[0],  headers, debug_names)
	# 	Print_DEBUG_Results(values[-1], headers, debug_names)
	#
		Print_DEBUG_Counts(values[-1], headers, "RNAP_STARTED_W_", N_DNA)
		Print_DEBUG_Counts(values[-1], headers, "RNAP_STARTED_C_", N_DNA)

	if (lineH): print lineH

	if (False):
		# changes counts to % of the time in a TF
		tf_named_percent = []
		for n in xrange(N_DNA+1):
			tf_named_percent.append(int(tf_named_counts[n]*100./n_selected))
	#	Print_Counts(tf_named_counts, "TF bound %")
		mean = np.average(tf_named_percent)
		sd   = np.std(tf_named_percent)
		if verbose:
			print "TF List Bound Mean=%f, SD=%f [%f,%f]"%(mean, sd, mean-sd, mean+sd)
		Print_Percent_Graph2(tf_named_percent[DISPLAY_START:DISPLAY_END+1], "TF Bound %",mean)
		if (lineH): print lineH

	if (True):
		# changes counts to % of the time in a TF
		tf_percents = []
		for n in xrange(N_DNA+1):
			tf_percents.append(int(tf_counts[n]*100./n_selected))
	#	Print_Counts(tf_counts, "TF bound %")
		mean = np.average(tf_percents)
		sd   = np.std(tf_percents)
		if verbose:
			print "TF Bound Mean=%f, SD=%f [%f,%f]"%(mean, sd, mean-sd, mean+sd)
		if (max(tf_counts) > 0):
			Print_Percent_Graph2(tf_percents[DISPLAY_START:DISPLAY_END+1], "TF Bound %",mean)
			if (lineH): print lineH

	# check to see if RNAP is active
	if (params.GetInt("RNAP","INITIAL_COUNT", 0) > 0):
		# changes counts to % of the time in a RNAP
		for n in xrange(N_DNA+1):
			rnap_counts[n] = int(rnap_counts[n]*100./n_selected)
	#	Print_Counts(rnap_counts, "RNAP bound %")
		mean = np.average(rnap_counts)
		sd   = np.std(rnap_counts)
		if verbose:
			print "RNAP Bound Mean=%f, SD=%f [%f,%f]"%(mean, sd, mean-sd, mean+sd)
		Print_Percent_Graph2(rnap_counts[DISPLAY_START:DISPLAY_END+1], "RNAP Bound %",mean)
		Print_Counts(rnap_counts[DISPLAY_START:DISPLAY_END+1], "RNAP Counts")
		if (lineH): print lineH

# 	Print_Counts(nuc_counts[DISPLAY_START:DISPLAY_END+1], "Nucleosome Counts")

	# changes counts to % of the time in a nucleosome
	nuc_percent = [0] * len(nuc_full_counts)
	for n in xrange(N_DNA+1):
		nuc_percent[n] = int(nuc_full_counts[n]*100./n_selected)

# 	Print_Counts(nuc_percent[DISPLAY_START:DISPLAY_END+1], "Nucleosome %")

	mean = np.average(nuc_full_counts)
	median = np.median(nuc_full_counts)
	sd   = np.std(nuc_full_counts)
	if verbose:
		print "Mean=%f, SD=%f [%f,%f] Median=%f"%(mean, sd, mean-sd, mean+sd, median)
	Print_Percent_Graph2(nuc_percent[DISPLAY_START:DISPLAY_END+1], "Nucleosome Occupancy %",mean)
	if (lineH): print lineH

	# Print Nucleosome Core occupancy
	# changes counts to % of the time in a nucleosome core
	nuc_core_percent = [0] * len(nuc_core_counts)
	for n in xrange(N_DNA+1):
		nuc_core_percent[n] = int(nuc_core_counts[n]*100./n_selected)

	mean = np.average(nuc_core_counts)
	median = np.median(nuc_core_counts)
	sd   = np.std(nuc_core_counts)
	if verbose:
		print "Mean=%f, SD=%f [%f,%f] Median=%f"%(mean, sd, mean-sd, mean+sd, median)
	Print_Percent_Graph2(nuc_core_percent[DISPLAY_START:DISPLAY_END+1], "Nucleosome Core Occupancy %",mean)
	if (lineH): print lineH

	# Combined total of FULL and CORE nucleosomes
	nuc_counts = [0]*(N_DNA+1)
	for n in xrange(N_DNA+1):
		nuc_counts[n] = nuc_full_counts[n] + nuc_core_counts[n]

	nuc_percent = [0] * len(nuc_counts)
	for n in xrange(N_DNA+1):
		nuc_percent[n] = int(nuc_counts[n]*100./n_selected)

	mean = np.average(nuc_counts)
	median = np.median(nuc_counts)
	sd   = np.std(nuc_counts)
	if verbose:
		print "Mean=%f, SD=%f [%f,%f] Median=%f"%(mean, sd, mean-sd, mean+sd, median)
	Print_Percent_Graph2(nuc_percent[DISPLAY_START:DISPLAY_END+1], "Nucleosome Full+Core Occupancy %",mean)
	if (lineH): print lineH

# 	# Calc Distribution of Occupancy
# 	dist = [0] * 101
# 	for n in nuc_percent:
# 		dist[n] += 1
# 	Print_Counts(dist, "Distribution of Nucleosome Occupancy")
# 	Print_Graph(dist, "Distribution of Nucleosome Occupancy",mean)
# 	#PrintBargraph("dist.png", [0], dist, "Distribution of Nucleosome Occupancy")
# 	#P.show()

# 		out = open("random_dist.tab","w")
# 		nuc_list = nuc_percent
# 	#	print nuc_list
# 		random.shuffle(nuc_list)
# 	#	print nuc_list
# 	#	while (len(nuc_list) > 0):
# 	#		# select random value, write to output
# 	#		i = random(0,len(nuc_list))
# 	#		value = nuc_list[i]
# 	#		del nuclist[i]
# 	#		out.write("%f\n")%value
# 		BuildWig(out, "Nucleosome Occupancy", "PlotModelResults:%s"%DNA_section, chromo, nuc_list, START_POS, NT_PER_GROUP)
# 	##	for value in nuc_list:
# 	##		out.write("%f\n")%(value/100.)
# 		out.close()
# 		if (lineH): print lineH

	print lineN

	if (False):
		# Show the KAPLAN/SEGAL predicted nucleosome occupancy graph
		mean = np.average(occ_vals)
		Print_Percent_Graph2(occ_vals[DISPLAY_START:DISPLAY_END+1], "Segal Predicted Occupancy %",mean)
		if (lineH): print lineH

		diff_vals = []
		for k in xrange(len(occ_vals)):
			diff_vals.append( (occ_vals[k] - nuc_percent[k]) )	# abs(occ_vals[k] - nuc_full_counts[k]) )
		mean = np.average(diff_vals)
		Print_Percent_Graph3(-100, 100, diff_vals[DISPLAY_START:DISPLAY_END+1], "Diff Occupancy %",mean)
	#	SRB_Utils.Print_Percent_Graph_LOG(diff_vals, "Diff Occupancy %", NT_PER_GROUP, START_POS)
		if (lineH): print lineH

		Print_Percent_Graph_LOG(on_vals, "Nucleosome Positional Probability:")

	chrom = chromo
	if (roman):
		chrom = chrom[:3] + K.NOX_ConvertStr2Roman(chrom[3:])

	if (True):
		# Output the Nuc positioning as a WIG file
		#wig_filename = "%s_NUC_Occupancy.wig"%DNA_section
		m = re.match('^(.*)\.',args[0])
		wig_filename = "%s_NUC_Occupancy.wig"%m.group(0)[:-1]
		if verbose:
			print "Creating WIG file with Occupancy - %% of Time in a Nucleosome:[%s]"%wig_filename
		outfile = open(wig_filename, "w")
		BuildWig(outfile, "Occupancy - % of Time in a Nucleosome", "PlotModelResults:%s"%DNA_section, chrom, nuc_percent, START_POS, NT_PER_GROUP)
		outfile.close()

	if (writeWIG):
		# Output the Nuc positioning as a WIG file

		m = re.match('^(.*)\.',args[0])
		wig_filename = "%s_NUC_Counts.wig"%m.group(0)[:-1]
		if verbose:
			print "Creating WIG file with Occupancy - # of timesteps in Nucleosome:[%s]"%wig_filename
		outfile = open(wig_filename, "w")
		BuildWig(outfile, "Occupancy - # of timesteps in Nucleosome", "PlotModelResults:%s"%DNA_section, chrom, nuc_counts, START_POS, NT_PER_GROUP)
		outfile.close()
#
if __name__ == '__main__':
	main()
