#
#Copyright (2011) University of Colorado
#All Rights Reserved
#Author: David Knox
#
###############################################################################
#
#
#
###############################################################################

import sys, os, re, string
import math

###############################################################################
# 
#
def NOX_Make_Results_Dir(path):
	if not os.path.exists(path):
		os.makedirs(path)
#end NOX_make_results_dir


def NOX_GetField(line, pos):
	f = None
	fields = line.split("\t")
	if (pos > 0) and (pos <len(fields)):
		f = fields[pos]
	return f
#end NOX_GetField

###############################################################################
# Read a wig file and return structure
#	[[header,data],[header,data],...]
# 
#
# WIG Format
#
# track type=wiggle_0 name=TF_REB1_70 description="REB1: Knox custom TF track"  visibility=2 autoScale=off viewLimits=-100:100.0 yLineMark=0. yLineOnOff=on color=0,255,0
# variableStep chrom=chr1 span=8
# # all following lines are in form: start_pos   score
# 22878       79.4
###############################################################################
# 
#
def NOX_Read_WIG(wig_filename, keep_other_fields=True):
	# Open binding site positions file
	wigFile = open(wig_filename, "r")

	results = []
	
	# collect data upto and including "track"
	# read and parse data until next track or comment line
	header = []
	data = []
		
	for line in wigFile.readlines():

		if (line[0] not in string.digits):
			# this is a header line
			# if we already have some data, write it out
			if (len(data) > 0):
				# add entry to results
				results.append([header,data])
				header = []	
				data = []
				
			header.append(line)
		else:
			# this is a data line
			# parse the data
			line.strip()
			fields = line.split()
			pos = int(fields[0])
			score = float(fields[1])

			if (keep_other_fields):	
				data.append((pos,score,fields[2:]))
			else:
				data.append((pos,score))
	
	if (len(header)	> 0):
		results.append([header,data])
							
	wigFile.close()
	
	return results
	
# end of NOX_Read_WIG

###############################################################################
# Read a wig file and return dictionary
#	results[chr] = [[pos,data],[pos,data],...]
# 
#
# WIG Format
#
# track type=wiggle_0 name=TF_REB1_70 description="REB1: Knox custom TF track"  visibility=2 autoScale=off viewLimits=-100:100.0 yLineMark=0. yLineOnOff=on color=0,255,0
# variableStep chrom=chr1 span=8
# # all following lines are in form: start_pos   score
# 22878       79.4
###############################################################################
# 
#
def NOX_Read_Parse_WIG(wig_filename, keep_other_fields=True, results=None, label="data",verbose=False):
	# Open binding site positions file
	wigFile = open(wig_filename, "r")

	if (not results):
		results = {}
	
	chr = ""
	prev_chr = ""
	lineno = 0
	
	for line in wigFile.readlines():
		lineno += 1
		
		if (len(line) < 3): continue
		if (line[0] == "#"): continue
		if (line[:5] == "track"): continue
		if (line[:5] == "varia"): 
			# parse the chromo
			line.strip()
			fields = line.split()
			chr = ""
			for f in fields:
				if (f[:5] == "chrom"):
					chromo,sep,chr = f.partition("=")					
			if (not results.has_key(chr)):
				results[chr] = []
	
			if (prev_chr != chr):
				if (verbose):
					sys.stderr.write("\t%s from: [%s]\n"%(label,chr))	
				prev_chr = chr
								
	
		else:
			# this is a data line
			# parse the data
			line.strip()
			fields = line.split()
			try:
				pos = int(fields[0])
				score = float(fields[1])

				if (keep_other_fields):	
					data = [pos,score,fields[2:]]
				else:
					data = [pos,score]
	
				results[chr].append(data)
			except:
				print "Error processing line [%d]: [%s]"%(lineno, line)
			
	wigFile.close()
	
	return results
	
# end of NOX_Read_WIG


###############################################################################

# GFF format
#
#    0. seqname - The name of the sequence. Must be a chromosome or scaffold.
#    1. source - The program that generated this feature.
#    2. feature - The name of this type of feature. Some examples of standard feature types are "CDS", "start_codon", "stop_codon", and "exon".
#    3. start - The starting position of the feature in the sequence. The first base is numbered 1.
#    4. end - The ending position of the feature (inclusive).
#    5. score - A score between 0 and 1000. If the track line useScore attribute is set to 1 for this annotation data set, the score value will determine the level of gray in which this feature is displayed (higher numbers = darker gray). If there is no score value, enter ".".
#    6. strand - Valid entries include '+', '-', or '.' (for don't know/don't care).
#    7. frame - If the feature is a coding exon, frame should be a number between 0-2 that represents the reading frame of the first base. If the feature is not a coding exon, the value should be '.'.
#    8. group - All lines with the same group are linked together into a single item. 
#
# chr1	sgdgene	gene	10769	11783	.	-	.	ID=geneYAL063C;Name=YAL063C;gene=FLO9;
#
def NOX_Read_GFF3(filename, thresh=-1, verbose=False):
	# Open binding positions file
	bindingFile = open(filename, "r")
	sites = {} 		# for each chromosome, create list of entrys, <start, score, strand, orig line>

	# read file records
	if (verbose):
		sys.stderr.write("Reading positions:\n")
	lines = bindingFile.readlines()
	if (verbose):
		sys.stderr.write("\tread %d lines\n"%len(lines))
	
	for line in lines:
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		chr    = fields[0]
		if (chr[:3] != 'chr'):
			chr = 'chr' + chr
		try:
			start  = int(fields[3]) 
		except:
			start = -1
			
		try:
			score  = float(fields[5]) 
			if (score < 0) : score = -score
		except:
			score = -1.
			
		if (thresh >= 0) and (score < thresh): continue
		
		# create entry = <start, score, strand, orig line>
		try:
			end = int(fields[4])
		except:
			end = -1
			
		entry = (min(start,end), score, fields[6], line)
		
		if (sites.has_key(chr)):
			sites[chr].append(entry)
		else:
			sites[chr] = [entry]
						
	bindingFile.close()
	return sites
# end of NOX_Read_GFF3

#########################################################################################
# Create list of entries for each chromosome
# Entry format: (chr, source, type, start, end, score, strand, frame, attributes)

def NOX_Parse_GFF3(filename, thresh=-1, verbose=False):
	# Open binding positions file
	bindingFile = open(filename, "r")
	sites = {} 		# for each chromosome, create list of entries

	# read file records
	if (verbose):
		sys.stderr.write("Reading positions:\n")
	lines = bindingFile.readlines()
	if (verbose):
		sys.stderr.write("\tread %d lines\n"%len(lines))
	
	for line in lines:
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		chr    = fields[0]
		if (chr[:3] != 'chr'):
			chr = 'chr' + chr
		try:
			start  = int(fields[3]) 
		except:
			start = -1
			
		try:
			score  = float(fields[5]) 
			if (score < 0) : score = -score
		except:
			score = -1.
			
		if (thresh >= 0) and (score < thresh): continue
		
		# create entry = <start, score, strand, orig line>
		try:
			end = int(fields[4])
		except:
			end = -1
			
		entry = (chr, fields[1], fields[2], start, end, score, fields[6], fields[7], fields[8])
		
		if (sites.has_key(chr)):
			sites[chr].append(entry)
		else:
			sites[chr] = [entry]
						
	bindingFile.close()
	return sites
# end of NOX_Parse_GFF3

#########################################################################################

# BEDGRAPH format
#    0. chrom - The name of the chromosome (e.g. chr3, chrY, chr2_random)
#    1. chromStart - The starting position of the feature in the chromosome. The first base in a chromosome is numbered 0.
#    2. chromEnd - The ending position of the feature in the chromosome
#    3. score - A score between 0 and 1000. 	  	 
#   
def NOX_Read_BEDGRAPH(bed_filename, thresh=-1):
	bedFile = open(bed_filename, "r")
	sites = {} 		# for each chromosome, create list of entrys, GFF style

	# read file records
	sys.stderr.write("Reading positions in [%s]:\n"%bed_filename)
	
	for line in bedFile.readlines():
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		if (line[0:5] == "track"): continue
			
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		if (len(fields) < 4): continue

		chr    = fields[0]
		if (chr[:3] != 'chr'):
			print ("[%s] ==> [chr%s]")%(chr,chr)
			chr = 'chr' + chr

		try:
			start = int(fields[1]) 
			end   = int(fields[2])
			score = float(fields[3]) 

		#	entry = (chr, "BED",".", min(start,end), max(start,end), score, ".", ".", "") 	# 3 match GFF3 format
			entry = [start,score, end, fields[4:]] # NOX_Read_Parse_WIG format

			if (sites.has_key(chr)):
				sites[chr].append(entry)
			else:
				sites[chr] = [entry]
		except:
			start = -1
						
	bedFile.close()
	return sites
#end of Read_BEDGRAPH
#
###############################################################################

#########################################################################################

# BED format
#    0. chrom - The name of the chromosome (e.g. chr3, chrY, chr2_random)
#    1. chromStart - The starting position of the feature in the chromosome. The first base in a chromosome is numbered 0.
#    2. chromEnd - The ending position of the feature in the chromosome
#    3. name - Defines the name of the annotation
#    4. score - A score between 0 and 1000. 	  	 
#    5. strand - Defines the strand - either '+' or '-'. 
#   
def NOX_Read_BED(bed_filename, thresh=-1):
	# Open binding positions file
	bindingFile = open(bed_filename, "r")
	sites = {} 		# for each chromosome, create list of entrys, <start, end, name, score, strand, orig line>

	# read file records
	sys.stderr.write("Reading positions:\n")
	lines = bindingFile.readlines()
	sys.stderr.write("\tread %d lines\n"%len(lines))
	
	for line in lines:
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		chr    = fields[0]
		if (chr[:3] != 'chr'):
			print ("[%s] ==> [chr%s]")%(chr,chr)
			chr = 'chr' + chr
		start  = int(fields[1]) 
		
		if (len(fields) > 4):
			score  = float(fields[4]) 
		else:
			score = 0
		if (score < 0) : score = -score
		if (thresh >= 0) and (score < thresh): continue

		if (len(fields) > 2):
			name  = fields[2]
		else:
			name = "BED"

		if (len(fields) > 3):
			strand = fields[3]
		else:
			strand = "+"
		
		# create entry = <start, end, name, score, strand, orig line>
		end = int(fields[2])
		entry = (min(start,end), max(start,end), name, score, strand, line)
		if (sites.has_key(chr)):
			sites[chr].append(entry)
		else:
			sites[chr] = [entry]
						
	bindingFile.close()
	return sites
#end of Read_BED
#
###############################################################################


###############################################################################
#
# Routines to handle parameter files
#
###############################################################################
class NOX_ParamFile:
	def __init__(self, filename=None):
		self.filename = ""
		self.data = {}		# for each named section, store a dictionary 
		self.sections = []
		if (filename):
			self.Load(filename)
		return
		
	def Load(self, filename):
		# read the file given
		sys.stderr.write("Reading Param File [%s]\n"%(filename))
		self.filename = filename
		lines = []
		try:
			paramFile = open(filename, "r")
		except IOError, err: 
			print "I/O error:", err
			return False
		except:
			print "Error opening file", sys.exc_info()[0]
			return False
		else:
			lines = paramFile.readlines()
		#	print "\tread %d lines"%len(lines)
			paramFile.close()
			
		attrs = re.compile('^\b*\s*(.*)=(.*)$')
		names = re.compile('^\b*\s*\[(.*)\]')
		section = None
		for line in lines:
		#	print "Line:",line[:-2]
			if (len(line) < 2): continue
			if (line[0] == '#'): continue
			
			if (line[0] == '['):
				# found a new section
				m = names.match(line)
				section = m.group(1).strip()
			#	print "Section:[%s]"%section
				self.data[section] = {}
				self.sections.append(section)
			else:
				# found new attribute
				try:
					m = attrs.match(line)
					attr  = m.group(1).strip()
					value = m.group(2).strip()
				#	print "\t[%s] <==> [%s]"%(attr,value)
					self.data[section][attr] = value
				except:
					pass
		return True
		
	def Write(self, file):
		file.write("# Generated by INI Range Generator from: %s\n"%self.filename)
		keys = self.data.keys()
		keys.sort()
		for k in keys:
			file.write("\n[%s]\n"%k)
			attrs = self.data[k].keys()
			attrs.sort()
			for a in attrs:
				file.write("%s = %s\n"%(a,self.data[k][a]))
		return
		
	def Dump(self):
		print "v==================v"
		keys = self.data.keys()
		keys.sort()
		for k in keys:
			print "|[%s]"%k
			attrs = self.data[k].keys()
			attrs.sort()
			for a in attrs:
				print "|\t[%s] = [%s]"%(a,self.data[k][a])
		print "^==================^"
		return
		
	def Sections(self):
		sections = self.data.keys()
		sections.sort()
		return sections

	def GetString(self, section, key, default=None):
		if (self.data.has_key(section)):
			if (self.data[section].has_key(key)):
				return self.data[section][key]
		return default

	def GetInt(self, section, key, default=None):
		str = self.GetString(section,key,default)
		if (str):
			try:
				str = self.StripComment(str)
				return int(str)
			except:
				try:
					return int(float(str))
				except:
					return default
		return default
		
	def GetFloat(self, section, key, default=None):
		str = self.GetString(section,key,default)
		if (str):
			try:
				str = self.StripComment(str)
				return float(str)
			except:
				return default
		return default

	def GetOverridedInt(self, sections, key, default=None):
		value = default
		for section in sections:
			value = self.GetString(section,key,value)
		return value
		
	def StripComment(self, str):
		i = str.find('#')
		if (i >= 0):
			str = str[:i]
		return str
		
# end of NOX_ParamFile class

def NOX_Load_Parameter_File(filename):
	params = NOX_ParamFile()
	params.Load(filename)
	return params
# end NOX_Load_Parameter_File()

###############################################################################

def Get_WASSON_Nucleosome_Prob_Position(alphabet_map, nt1, nt2):
	di_nt = alphabet_map[nt1] * 4 + alphabet_map[nt2]	# calc position in the prob array
	return di_nt
	
def Get_WASSON_Nucleosome_Prob(positional_di_probs, alphabet_map, nt1, nt2):
	di_nt = Get_WASSON_Nucleosome_Prob_Position(alphabet_map, nt1, nt2)
	return  positional_di_probs[di_nt]
###############################################################################
import copy

def Calc_WASSON_Nucleosome_Prob_Range(positional_di_probs, background_probs, alphabet_map):
	prob_range = [0,0]

	use_background = False
	
	# calc the max and min possible probabiity over the 127 positions	

	# Initialize all 16 possible states (AA,AC,AG,AT,CA,CG,...)
#L	state_ranges = [[1,1]]*16		# [max, min]
	state_ranges = [[0,0]]*16		# [log(1), log(1)]
	
	# add in the background probability for 20 nt
	back_probs = [math.log(max(background_probs)) * 20, math.log(min(background_probs)) * 20]
#	print "Back probs:", back_probs
	if (use_background):
		state_ranges = [back_probs] * 16 # use the background?
#		print "state_ranges:", state_ranges

	# for each position in the nucleosome prob list
	#	next_state_ranges = state_ranges
	# 	for each nt1 in "ACGT"
	#		Calc the Max(min)_prob to [nt1][nt2].  Max(min) of all paths ending with nt1 
	#				(e.g [A][nt1], C[nt1], G[nt1], T[nt1])
	#		for each nt2 in "ACGT"
	#			Next_state_ranges = Max(min)_prob * probability of nt2 in this position 
	#				of a nucleosome (positional_di_probs[i][nt1][nt2])
	#		
	#	state_ranges = next_state_ranges
	
	for i in xrange(127):
		next_state_ranges = copy.deepcopy(state_ranges)
		
		for nt1 in "ACGT":
			# calc max of all paths leading to nt1
			max_vals = []
			min_vals = []
			for nt0 in "ACGT":
				di_nt = Get_WASSON_Nucleosome_Prob_Position(alphabet_map, nt0, nt1)
				max_vals.append(state_ranges[di_nt][0])
				min_vals.append(state_ranges[di_nt][1])
			max_prob = max(max_vals)
			min_prob = min(min_vals)
			
			# calc new state ranges for states starting with nt1
			for nt2 in "ACGT":
				di_nt = Get_WASSON_Nucleosome_Prob_Position(alphabet_map, nt1, nt2)
				prob = Get_WASSON_Nucleosome_Prob(positional_di_probs[i], alphabet_map, nt1, nt2)
			#L	next_state_ranges[di_nt] = [max_prob * prob, min_prob * prob]
				next_state_ranges[di_nt] = [max_prob + prob, min_prob + prob]	# using log prob
		state_ranges = next_state_ranges
		
	print "Calc_WASSON_Nucleosome_Prob_Range:" 
	for x in "ACGT":
		line = "\t"
		for y in "ACGT":
			r = state_ranges[Get_WASSON_Nucleosome_Prob_Position(alphabet_map, x, y)]
		#	line += "[%e, %e]"%(r[0],r[1])
		#L	line += "[%5d, %5d]"%(math.log(r[0]),math.log(r[1]))
			line += "[%5d, %5d]"%(r[0], r[1])
		print line
			
	max_vals = []
	min_vals = []
	for nt1 in "ACGT":
		for nt2 in "ACGT":
			di_nt = Get_WASSON_Nucleosome_Prob_Position(alphabet_map, nt1, nt2)
			max_vals.append(state_ranges[di_nt][0])
			min_vals.append(state_ranges[di_nt][1])
	prob_range = [max(max_vals), min(min_vals)]
	print "Calc_WASSON_Nucleosome_Prob_Range ==>", prob_range
	diff = abs(prob_range[1] - prob_range[0])
	prob_range[0] = prob_range[1]+(diff/1.3)
	print "RE Calc_WASSON_Nucleosome_Prob_Range ==>", prob_range
	return prob_range
#end

###############################################################################

def Calc_WASSON_Nucleosome_Rates(filename, dna, NT_PER_GROUP, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE, log=None):
	positional_nuc_rates = [[NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE]]
	positional_prob = [0.]

	if (log == None):
		log = NOX_LogFile()
		
	log.Display("Using Calc_WASSON_Nucleosome_Rates([%s],...,%d,%f,%f):"%(filename, NT_PER_GROUP, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE))
	
	# read the positional di-nucleotide probabilities
	lines = open(filename).readlines()
	print "Read %d lines from [%s]"%(len(lines), filename)
	if (len(lines) != 127):
		log.Display("[%s] is not a di-nucleotide probability file"%filename)
		return positional_nuc_rates, positional_prob
		
	positional_di_probs = []
	for line in lines:
	#	print line
		fields = line.strip().split('\t')
		di_probs = []
		for f in fields:
	#		val = float(f)
			try:
				val = math.log(float(f))
			except:
				val = 0
				
			di_probs.append(val)
		positional_di_probs.append(di_probs)

	background_probs = [0.308512, 0.191488, 0.191488, 0.308512]		
	log_back_probs = []
	for p in background_probs:
		log_back_probs.append(math.log(p))
	alphabet_map = {"A":0, "C":1, "G":2, "T":3}

	print 
	log_prob_ranges = Calc_WASSON_Nucleosome_Prob_Range(positional_di_probs, background_probs, alphabet_map)
	log_prob_diff = log_prob_ranges[0] - log_prob_ranges[1]
	log.Display(("Wasson Nuc log(prob) range: %.8f"%log_prob_diff))
	
	# for each position in the DNA sequence
	#	calculate the probability of a nucleosome binding starting at this position
	#		using WASSON data: 10 background + 127 positional + 10 background
	#			prob = 1.0
	#			for i in range(10):
	#				prob *= background_probs[seq[pos+i]]		
	#			
	#			for i in range(127):
	#				di_nt = alphabet_map[seq[pos+i+10]] * 4 + alphabet_map[seq[pos+i+10+1]]
	#				prob *= positional_di_probs[i][di_nt]		
	#
	#			for i in range(10):
	#				prob *= background_probs[seq[pos+i+137]]		
	#
	#	if (grouping nucleotides)
	#		combine the probabilities at each nucleotide of the group
	use_background = False
	pos_prob = []
	nuc_prob = []	
	for pos in xrange(len(dna)):

		prob = 1.0
		
		# calculate the probability of nucleosome starting at this position
		for i in range(148):
			nt1 = nt2 = 0
			if (pos+i < len(dna)):
				nt1 = alphabet_map[dna[pos+i]]
			if (pos+i+1 < len(dna)):
				nt2 = alphabet_map[dna[pos+i+1]]
			
			if (i < 10) or (i >= 137):
				# use background prob of nt at this position
		#L		prob *= background_probs[nt1]
				if (use_background):
					prob += log_back_probs[nt1]
			else:
				di_nt = nt1 * 4 + nt2
				# print alphabet_map[dna[pos+i]],alphabet_map[dna[pos+i+1]], i-10, di_nt
		#L		prob *= positional_di_probs[i-10][di_nt]
				prob += positional_di_probs[i-10][di_nt]	# using log prob
			
		## prob /= 147.	# avg when adding
		
		# adjust the prob to its placement within the prob range
		adj_prob = prob + abs(log_prob_ranges[1])
		adj_prob /= log_prob_diff
		prob = adj_prob
		
		# create rates [on,off] for this position
##		rates = [NUCLEOSOME_ON_RATE*prob,1.-(NUCLEOSOME_OFF_RATE*prob)]
		rates = [NUCLEOSOME_ON_RATE*prob, NUCLEOSOME_OFF_RATE*(1.-prob)]
#		print "Adjusted prob [%d]"%pos,prob, "==>", adj_prob, rates
	
		# add positional rates [on,off]
		nuc_prob.append(rates)
		pos_prob.append(prob)
	
	if (NT_PER_GROUP > 1):
		# need to group the objects
		pos = 0
		while (pos < len(dna)):
			rates = [0,0]
			prob  = 0
			for i in range(NT_PER_GROUP):
				if (pos+i < len(dna)-1):
					# use max of each value
					if (rates[0] < nuc_prob[pos+i][0]):	
						rates[0] = nuc_prob[pos+i][0]
					if (rates[1] < nuc_prob[pos+i][1]):		
						rates[1] = nuc_prob[pos+i][1]
					if (prob < pos_prob[pos+i]):
						prob = pos_prob[pos+i]
						
			#		# use average					
			#		rates[0] += nuc_prob[pos+i][0]
			#		rates[1] += nuc_prob[pos+i][1]
		
			# use average
		#	if (rates[0] > 0):	
		#		rates[0] /= NT_PER_GROUP
		#	if (rates[1] > 0):		
		#		rates[1] /= NT_PER_GROUP
			
			# adjustments to match WASSON figures
			rates[0] *= .9
			rates[1] *= .9
			
			positional_nuc_rates.append(rates)			
			positional_prob.append(prob)
			
		#	print "\t%3d"%pos,dna[pos:pos+NT_PER_GROUP], rates
			pos += NT_PER_GROUP				
	else:
		for rates in nuc_prob:
			# adjustments to match WASSON figures
			rates[0] *= .9
			rates[1] *= .9
			
			positional_nuc_rates.append(rates)	

	min_rate = [1.,1.]
	max_rate = [0.,0.]
	sum = 0.
	for i,rates in enumerate(positional_nuc_rates[1:]):
			if (rates[0] > max_rate[0]):
				max_rate = rates
			if (rates[0] < min_rate[0]):
				min_rate = rates
			sum += rates[0]				
			#print "\t%3d"%i, rates
	print "Min rate:", min_rate
	print "Max rate:", max_rate
	print "Avg rate:", sum/len(positional_nuc_rates)
	
	# print the log probs as histogram / graph
		
	return positional_nuc_rates, positional_prob
#end Calc_WASSON_Nucleosome_Rates

############################################################

def Calc_WASSON_CORE_Nucleosome_Rates(filename, dna, NT_PER_GROUP, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE, log=None):
	positional_nuc_rates = [[NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE]]
	positional_prob = [0.]

	if (log == None):
		log = NOX_LogFile()
		
	log.Display("Using Calc_WASSON_CORE_Nucleosome_Rates([%s],...,%d,%f,%f):"%(filename, NT_PER_GROUP, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE))
	
	# read the positional di-nucleotide probabilities
	lines = open(filename).readlines()
	print "Read %d lines from [%s]"%(len(lines), filename)
	if (len(lines) != 127):
		log.Display("[%s] is not a di-nucleotide probability file"%filename)
		return positional_nuc_rates, positional_prob
		
	positional_di_probs = []
	for line in lines:
	#	print line
		fields = line.strip().split('\t')
		di_probs = []
		for f in fields:
	#		val = float(f)
			try:
				val = math.log(float(f))
			except:
				val = 0
				
			di_probs.append(val)
		positional_di_probs.append(di_probs)

	background_probs = [0.308512, 0.191488, 0.191488, 0.308512]		
	log_back_probs = []
	for p in background_probs:
		log_back_probs.append(math.log(p))
	alphabet_map = {"A":0, "C":1, "G":2, "T":3}

	print 
	log_prob_ranges = Calc_WASSON_Nucleosome_Prob_Range(positional_di_probs, background_probs, alphabet_map)
	log_prob_diff = log_prob_ranges[0] - log_prob_ranges[1]
	log.Display(("Wasson Nuc log(prob) range: %.8f"%log_prob_diff))
	
	# for each position in the DNA sequence
	#	calculate the probability of a nucleosome binding starting at this position
	#		using WASSON data: 10 background + 127 positional + 10 background
	#			prob = 1.0
	#			for i in range(10):
	#				prob *= background_probs[seq[pos+i]]		
	#			
	#			for i in range(76):
	#				di_nt = alphabet_map[seq[pos+i+10]] * 4 + alphabet_map[seq[pos+i+10+1]]
	#				prob *= positional_di_probs[i][di_nt]		
	#
	#			for i in range(10):
	#				prob *= background_probs[seq[pos+i+137]]		
	#
	#	if (grouping nucleotides)
	#		combine the probabilities at each nucleotide of the group
	use_background = False
	pos_prob = []
	nuc_prob = []	
	for pos in xrange(len(dna)):

		prob = 1.0
		
		# calculate the probability of nucleosome starting at this position
		for i in range(96):
			nt1 = nt2 = 0
			if (pos+i < len(dna)):
				nt1 = alphabet_map[dna[pos+i]]
			if (pos+i+1 < len(dna)):
				nt2 = alphabet_map[dna[pos+i+1]]
			
			if (i < 10) or (i >= 87):
				# use background prob of nt at this position
		#L		prob *= background_probs[nt1]
				if (use_background):
					prob += log_back_probs[nt1]
			else:
				di_nt = nt1 * 4 + nt2
				# print alphabet_map[dna[pos+i]],alphabet_map[dna[pos+i+1]], i-10, di_nt
		#L		prob *= positional_di_probs[i-10][di_nt]
				prob += positional_di_probs[i-10+25][di_nt]	# using log prob
			
		## prob /= 147.	# avg when adding
		
		# adjust the prob to its placement within the prob range
		adj_prob = prob + abs(log_prob_ranges[1])
		adj_prob /= log_prob_diff
		prob = adj_prob
		
		# create rates [on,off] for this position
##		rates = [NUCLEOSOME_ON_RATE*prob,1.-(NUCLEOSOME_OFF_RATE*prob)]
		rates = [NUCLEOSOME_ON_RATE*prob, NUCLEOSOME_OFF_RATE*(1.-prob)]
#		print "Adjusted prob [%d]"%pos,prob, "==>", adj_prob, rates
	
		# add positional rates [on,off]
		nuc_prob.append(rates)
		pos_prob.append(prob)
	
	if (NT_PER_GROUP > 1):
		# need to group the objects
		pos = 0
		while (pos < len(dna)):
			rates = [0,0]
			prob  = 0
			for i in range(NT_PER_GROUP):
				if (pos+i < len(dna)-1):
					# use max of each value
					if (rates[0] < nuc_prob[pos+i][0]):	
						rates[0] = nuc_prob[pos+i][0]
					if (rates[1] < nuc_prob[pos+i][1]):		
						rates[1] = nuc_prob[pos+i][1]
					if (prob < pos_prob[pos+i]):
						prob = pos_prob[pos+i]
						
			#		# use average					
			#		rates[0] += nuc_prob[pos+i][0]
			#		rates[1] += nuc_prob[pos+i][1]
		
			# use average
		#	if (rates[0] > 0):	
		#		rates[0] /= NT_PER_GROUP
		#	if (rates[1] > 0):		
		#		rates[1] /= NT_PER_GROUP
			
			# adjustments to match WASSON figures
			rates[0] *= .9
			rates[1] *= .9
			
			positional_nuc_rates.append(rates)			
			positional_prob.append(prob)
			
		#	print "\t%3d"%pos,dna[pos:pos+NT_PER_GROUP], rates
			pos += NT_PER_GROUP				
	else:
		for rates in nuc_prob:
			# adjustments to match WASSON figures
			rates[0] *= .9
			rates[1] *= .9
			
			positional_nuc_rates.append(rates)	

	min_rate = [1.,1.]
	max_rate = [0.,0.]
	sum = 0.
	for i,rates in enumerate(positional_nuc_rates[1:]):
			if (rates[0] > max_rate[0]):
				max_rate = rates
			if (rates[0] < min_rate[0]):
				min_rate = rates
			sum += rates[0]				
			#print "\t%3d"%i, rates
	print "Min rate:", min_rate
	print "Max rate:", max_rate
	print "Avg rate:", sum/len(positional_nuc_rates)
	
	# print the log probs as histogram / graph
		
	return positional_nuc_rates, positional_prob
#end Calc_WASSON_CORE_Nucleosome_Rates

###############################################################################
roman_strs = ["Z", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", 
             "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]
#arabic_strs = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", 
#             "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]

def NOX_ConvertRoman2Int(str):
	n = 0
	pos = roman_strs.find(str)
	if (pos >= 0):
		n = pos		# found match	
	return n

def NOX_ConvertInt2Roman(val):
	pos = 0
	if (val < len(roman_strs)):
		pos = val
	return roman_strs[pos]

def NOX_ConvertStr2Roman(str):
	try:
		c = int(str)
	except:
		c = 0
		print "failed to make int from [%s]"%str
		
	if (c >= len(roman_strs)):
		print "Number [%d] exceeds our limit of %d"%(str, len(roman_strs))
		c = 0

	return roman_strs[c]

###############################################################################
###############################################################################

class NOX_LogFile:
	def __init__(self, filename=None, echo=True):
		self.filename = ""	
		self.log = None 
		self.echo = echo		# 'echo' True if display also writes to output 
		if (filename):
			self.Load(filename)
		return
		
	def Load(self, filename):
		try:
			self.log = open(filename, "w", 0)
		except IOError, err: 
			print "Error opening log file [%s] for write."%filename
			print "I/O error:", err
			return False
		except:
			print "Error opening log file [%s] for write."%filename
			print "Error opening file", sys.exc_info()[0]
			return False
			
		return True

	def Display(self, str, force=False):
		if (self.log):
			try:
				self.log.write(str)
				self.log.write('\n')
			except:
				pass
		
		if (self.echo or force):
			try:
				print(str)
			except:
				pass			
					
# end of NOX_LOGFile class	
	
###############################################################################
###############################################################################

class NOX_GeneAttrs:
	def __init__(self, filename=None):
		self.filename = ""	
		self.id2name  = {}		# lookup for common name given yeast id
		self.name2id  = {}		# lookup for yeast id given common name
		self.tf_list  = {}		# table: for each gene, list of regulators of that gene
		self.attrlist = {}		# table: for each gene, dict of attributes
		
		self.ALIAS_LIST		= "AliasList"
		self.CHROMOSOME		= "Chromosome"
		self.CLASSIFICATION	= "ORFClassification"
		self.COMMON_NAME 	= "CommonName"
		self.END			= "End"
		self.MOTIF			= "MOTIF"
		self.NOTE			= "Note"
		self.ONTOLOGY		= "Ontology"
		self.POSITION		= "Position"
		self.PROMOTER		= "PROMOTER"
		self.PROTEIN_COUNT	= "ProteinCount"
		self.REGULATED_BY 	= "RegulatedBy"
		self.START			= "Start"
		self.STRAND			= "Strand"
		self.TR_REGION		= "TR_REGION"
					
		if (filename):
			self.Load(filename)
		return

	###########################################################################

	def LookupID(self, name):
	
		uname = name.upper()
		
		if (self.name2id.has_key(uname)):	# if it is a known common name / alias return ID
			return self.name2id[uname]
			
		if (self.id2name.has_key(uname)):	# if it is a legal ID return the ID
			return uname
		
		return name		# otherwise return the original name

	###########################################################################

	def LookupName(self, id):
	
		uid = id.upper()
		
		if (self.name2id.has_key(uid)):	# if it is a known common name, return name
			return uid
						
		if (self.id2name.has_key(uid)):	# if it is a legal ID return the name
			return self.id2name[uid][0]
		
		return id		# otherwise return the original name

	###########################################################################

	def IsValidName(self, name):
	
		uname = name.upper()
		
		if (self.name2id.has_key(uname)):	# if it is a known common name / alias return ID
			return True
			
		if (self.id2name.has_key(uname)):	# if it is a legal ID return the ID
			return True
		
		return False		

	###########################################################################

	def IsValidID(self, id):
	
		uid = id.upper()
								
		if (self.id2name.has_key(uid)):	# if it is a legal ID return the name
			return True
		
		return False

	###########################################################################

	def GetAttr(self, id, key, default=""):
		results = default
		id = self.LookupID(id)
		if (self.attrlist.has_key(id) and self.attrlist[id].has_key(key)):
			results = self.attrlist[id][key][0]
		return results
		
	###########################################################################
	#
	# read attributes file to collect mappings
	#
	def Load(self, filename):
		# Read data and create lookup tables
		
		try:
			file = open(filename, "r")
		except:
			sys.stderr.write("Error loading: [%s]\n"%filename)
			return
			
		self.filename = filename
		
		# read file records
	
		for line in file.readlines():
			line = line.strip()
			if (len(line) < 2): continue
			if (line[0] == '#'): continue

		
			fields = line.split("\t")
			yeast_id  = fields[0]
		
			if (fields[1] == "CommonName"):		
				common_name = fields[2] 
		
				if (self.id2name.has_key(yeast_id)):
					self.id2name[yeast_id].append(common_name)
				else:
					self.id2name[yeast_id] = [common_name]
			
				if (len(common_name) > 0):
					if (self.name2id.has_key(common_name)):
						sys.stderr.write("Duplicate: [%s] already has [%s] instead of [%s]\n"%(common_name,self.name2id[common_name],yeast_id))
						sys.stderr.write("[%s]\n"%line)
					else:
						self.name2id[common_name] = yeast_id
						self.name2id[yeast_id[:-1]] = yeast_id	# add the name of the ID without strand info
						
			elif (fields[1] == "Regulator"):
				# add regulator to list for this gene id
				reg_name = fields[2]
				if (self.tf_lists.has_key(yeast_id)):
					self.tf_lists[yeast_id].append(reg_name)
				else:
					self.tf_lists[yeast_id] = [reg_name]
					
			if (not self.attrlist.has_key(yeast_id)):
				self.attrlist[yeast_id] = {}
				
			if (not self.attrlist[yeast_id].has_key(fields[1])):
				self.attrlist[yeast_id][fields[1]] = []
			self.attrlist[yeast_id][fields[1]].append(fields[2])
				
			
		file.close()
		return
		
# end of NOX_GeneAttrs class	
	
###############################################################################
###############################################################################
		