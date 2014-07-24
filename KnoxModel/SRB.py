#
#Copyright (2011) University of Colorado
#All Rights Reserved
#Author: David Knox
#

import sys, os, math, errno, getopt, re
import TAMO
from   TAMO		import MotifTools
from   TAMO.seq import Fasta
import numpy as np
import KnoxUtils as K
#import SRB_Utils  need to move some of these routines to utils file

###############################################################################
#
# GLOBALS
#
###############################################################################
N_DNA                  = 0
NT_PER_GROUP           = 0
N_GROUP_PER_NUCLEOSOME = 0
N_INIT_STAGES          = 0
RNAP_N_POS             = 0
params = None
DNA_section	= ""

###############################################################################
# Utility routine to calculate length of DNA binding components in current grouping size
#
def N_DNA_POS(n_nt):
	global NT_PER_GROUP
	len = (n_nt + NT_PER_GROUP - 1)/ NT_PER_GROUP
	return len

###############################################################################
# Utility routine to calculate DNA position from chromosome position
#
def DNA_POS(chr_pos):
	global NT_PER_GROUP
	global N_DNA
	global DNA_section
	chr_start  = params.GetInt(DNA_section,"START",0)
	chr_pos -= chr_start
	len = (chr_pos + NT_PER_GROUP - 1)/ NT_PER_GROUP
	if (len > N_DNA):
		return -1
	return len
	
###############################################################################
#
# Routines for SSA Rules
#
###############################################################################
class SSA_Rule:
	def __init__(self, name):
		self.name    = name
		self.inputs  = []		# list of reactants
		self.outputs = []		# list of resultants
		self.rate    = 0.0		# rate of reaction
		self.steps   = 0		# number of steps
		self.comment = None
		return
		
		######################################################################
		
	def AddReactant(self, input):
		self.inputs.append(input)
		
		######################################################################
		
	def AddResultant(self, output):
		self.outputs.append(output)
		
		######################################################################

	def AddStableReactant(self, input):
		s_react = "$%s"%input
		self.inputs.append(s_react)
		
		######################################################################
		
	def AddStableResultant(self, output):	
		# dont add the reactanct to list
		return
		
		######################################################################
		
	def AddComment(self, str):
		if (self.comment):
			self.comment += "\n"
			self.comment += str
		else:
			self.comment = str
		
		######################################################################
		
	def Write(self, f):
		# write the rule to the file given
		if (len(self.name) > 0):
			reactants = ""
			for r in self.inputs:
				if (len(reactants) > 0):
					reactants += " + "
				reactants += r
			
			resultants = ""
			for r in self.outputs:
				if (len(resultants) > 0):
					resultants += " + "
				resultants += r
			f.write("%s, "%self.name)
			f.write("%s"%reactants)
			f.write(" -> ")
			f.write("%s"%resultants)
			f.write(", %f"%self.rate)
			if (self.steps >= 1):
				f.write(", steps: %d"%self.steps)
			f.write("; ")
			
		if (self.comment):
			# now works for multi-line comments
			comments = self.comment.split('\n')
			f.write("// %s"%comments[0]) 
			if (len(comments) > 1):
				for c in comments[2:]:
					f.write("\n// %s"%c) 
								
		f.write("\n")

# end of SSA_Rule
###############################################################################


###############################################################################
#
# Routines for SSA Nucleosome
#
#		reactants - dict of reactants to create and inital value
#		width     - footprint width (in DNA positions) of component on the DNA
#		count     - initial count of component molecules
#
###############################################################################
class SSA_Nucleosome:
	def __init__(self, name, params, output_file=None):
		self.MODELING   = params.GetInt("SRB","MODEL_NUCLEOSOME", 1)
		self.SIZE       = params.GetInt("NUCLEOSOME", "SIZE", 147)
		self.GROUPS     = (self.SIZE + NT_PER_GROUP-1) / NT_PER_GROUP	

		self.name       = name
		self.outfile    = output_file
		self.reactants  = {}		# dict of reactants to create and inital value

		self.linker_nt  = N_DNA_POS(params.GetInt("NUCLEOSOME","MIN_LINKER_SIZE",20))
		self.linker_size = (self.linker_nt + NT_PER_GROUP-1) / NT_PER_GROUP

		# list of rates (loaded from the param_file)				
		self.ON_RATE    = params.GetFloat("NUCLEOSOME","ON_RATE", 1.0)
		self.OFF_RATE   = params.GetFloat("NUCLEOSOME","OFF_RATE",1.0)
		self.ABORT_RATE = params.GetFloat("NUCLEOSOME","INIT_ABORT_RATE",1.0)

		self.ON_DELAY   = params.GetInt("NUCLEOSOME","ON_DELAY",0)
		self.OFF_DELAY  = params.GetInt("NUCLEOSOME","OFF_DELAY",0)


		return
		
	######################################################################

	def GetPositionalRates(self, params, DNA_section, dna):
		# Get the position dependent OFF rates based on DNA sequence
		prob_file = params.GetString("NUCLEOSOME","NUC_PROB_FILE")
		prob_file = params.GetString(DNA_section,"NUC_PROB_FILE",prob_file)		# override filename

		di_nt_prob_file = params.GetString("NUCLEOSOME","DI_NT_NUC_PROB_FILE")
		di_nt_prob_file = params.GetString(DNA_section,"DI_NT_NUC_PROB_FILE",di_nt_prob_file)		# override filename

		if (di_nt_prob_file):
			self.positional_nuc_rates, pos_prob = K.Calc_WASSON_Nucleosome_Rates(di_nt_prob_file, dna, NT_PER_GROUP, self.ON_RATE, self.OFF_RATE)
		elif (prob_file): #old SEGAL positional prob
			self.positional_nuc_rates = Calc_Nucleosome_Rates_From_File(prob_file, chromo, chr_start, chr_end, dna, self.ON_RATE, self.OFF_RATE, NT_PER_GROUP, START_POS)
		else:
			self.positional_nuc_rates = Calc_Nucleosome_Rates(dna, self.ON_RATE, self.OFF_RATE)

		return
		
	######################################################################
	
	def Set_Outfile(output_file):

		self.outfile    = output_file

		return
		
	######################################################################

	###############################################################################
	#
	#	Create Nucleosome variables
	# 
	###############################################################################
	def Init_Reactants(self, N_DNA):

		n_histone = params.GetInt("NUCLEOSOME","N_HISTONES",0)
		self.reactants["histones"] = n_histone
		self.reactants["NUC_SIZE"] = self.GROUPS
		self.reactants["NUC_BINDING"] = 0
		self.reactants["NUC_UNBINDING"] = 0
	
		for i in xrange(1,N_DNA+1):
			self.reactants["nuc_bound_%04d"%i] = 0
			self.reactants["nuc_binding_%04d"%i] = 0
			self.reactants["nuc_stable_%04d"%i] = 0
			self.reactants["nuc_unbinding_%04d"%i] = 0

		return
		
	######################################################################

	def Write_Reactants(self):

		if (not self.outfile): 
			# write error msg
			return

		self.outfile.write("//\n// %s\n//\n"%"Nucleosomes")
		self.outfile.write("// nuc_[i]           keep list of locations with Nucleosome bound\n")
		self.outfile.write("// nuc_binding_[i]   keep list of locations with Nucleosome binding\n")
		self.outfile.write("// nuc_stable_[i]    keep list of locations with Nucleosome stable\n")
		self.outfile.write("// nuc_unbinding_[i] keep list of locations with Nucleosome unbinding\n")	
			
		keys = self.reactants.keys()
		keys.sort()
		for key in keys:
			self.outfile.write("%-20s= %d;  \n"%(key, self.reactants[key]))
	
		return

	######################################################################

	def Initiate(self, pos):
		rules = []
		rule = SSA_Rule("Nucleosome_INITIATE_%04d"%(pos))
		rule.AddStableReactant("histones")
		for n in xrange(N_GROUP_PER_NUCLEOSOME):
			if (pos+n <= N_DNA):
				rule.AddReactant("dna_%04d"%(pos+n))
					
		rule.AddResultant("nuc_binding_%04d"%pos)
		rule.AddResultant("nuc_bound_%04d"%pos)

		rule.rate = max(self.positional_nuc_rates[pos][0], 1.e-10)	# min rate of 1 * 10**-10
		rules.append(rule)
		return rules

	######################################################################

	def Linker_Abort(self, side, pos, state, alt_pos, alt_state):
		# Another alt_state nucleosome bound to the SIDE of this state nucleosome
		rule = SSA_Rule("Nucleosome_LINKER_%c_%s_%04d_%s_%04d"%(side, alt_state, alt_pos, state, pos))
		rule.AddReactant("nuc_%s_%04d"%(state, pos))
		rule.AddReactant("nuc_%s_%04d"%(alt_state, alt_pos))
					
		rule.AddResultant("nuc_unbinding_%04d"%pos)
		rule.AddResultant("nuc_%s_%04d"%(alt_state,alt_pos))
				
		rule.rate = self.ABORT_RATE
		
		return [rule]

	######################################################################
	
	# Cause Nucleosome to Abort if another nucleosome (binding or stable) is in linker region 
	def Linker_Check(self, pos, linker_left, linker_right):
		rules = []
		# for each position of the linker
		#	calc alternate position
		#	if nucleosome bound at alternate position, abort this one
		for n in xrange(linker_left):
			# calculate the position to the left
			left_pos = pos - N_GROUP_PER_NUCLEOSOME - n

			if (left_pos > 0) and (left_pos <= N_DNA):
		
				new_rules = self.Linker_Abort("L", pos, "binding", left_pos, "binding")
				rules.extend(new_rules)
				new_rules = self.Linker_Abort("L", pos, "binding", left_pos, "stable")
				rules.extend(new_rules)
				new_rules = self.Linker_Abort("L", pos, "stable",  left_pos, "stable")
				rules.extend(new_rules)

		for n in xrange(linker_right):
			# calculate the position to the right
			right_pos = pos + N_GROUP_PER_NUCLEOSOME + n

			if (right_pos > 0) and (right_pos <= N_DNA):

				new_rules = self.Linker_Abort("R", pos, "binding", right_pos, "binding")
				rules.extend(new_rules)
				new_rules = self.Linker_Abort("R", pos, "binding", right_pos, "stable")
				rules.extend(new_rules)
				new_rules = self.Linker_Abort("R", pos, "stable",  right_pos, "stable")
				rules.extend(new_rules)

		return rules

	######################################################################

	def Bind(self, pos):
	
		rule = SSA_Rule("Nucleosome_BIND_%04d"%pos)
		rule.AddReactant("nuc_binding_%04d"%pos)		
		rule.AddResultant("nuc_stable_%04d"%pos)
		rule.rate = 1. # force transition
		rule.steps = self.ON_DELAY

		return [rule]
		
	######################################################################

	def Unbind(self, pos):		
	
		rule = SSA_Rule("Nucleosome_UNBIND_%04d"%pos)
		rule.AddReactant("nuc_stable_%04d"%pos)		
		rule.AddResultant("nuc_unbinding_%04d"%pos)
		rule.rate = max(0.09, self.positional_nuc_rates[pos][1])
		rule.steps = self.OFF_DELAY

		return [rule]
		
	######################################################################

	def Evict(self, pos):

		rule = SSA_Rule("Nucleosome_EVICT_%04d"%(pos))
		rule.AddReactant("nuc_unbinding_%04d"%(pos))		
		rule.AddReactant("nuc_bound_%04d"%(pos))		
		rule.AddStableResultant("histones")
		
		for n in xrange(self.GROUPS):
			if (pos+n <= N_DNA):
				rule.AddResultant("dna_%04d"%(pos+n))
		rule.AddResultant("NUC_UNBINDING")
		rule.rate = 100.0 # force transition

		return [rule]
		
	######################################################################

	def Generic_Routine(self, N_DNA):
		return
		
		
#
# end of SSA_Nucleosome
###############################################################################

###############################################################################
#
# Routines for SSA RNAP
#
#		reactants - dict of reactants to create and inital value
#		width     - footprint width (in DNA positions) of RNAP component on the DNA
#		stages    - number of initiation stages (used to regulate time from init to elongation)
#		count     - initial count of component molecules
#
###############################################################################
class SSA_RNAP:
	def __init__(self, name, params, section=None, output_file=None):
		sections = ["SRB"]
		if section: sections.append(section)
		self.MODELING   = params.GetOverridedInt(sections,"MODEL_RNAP",0)
		self.DEBUGGING  = True
		self.TATA       = False
		self.TATA_WIDTH = N_DNA_POS(8)
		self.outfile    = output_file
		self.name       = name
		self.reactants  = {}		# dict of reactants to create and inital value

		self.stages     = params.GetInt("RNAP","N_INIT_STAGES",1)
		self.count      = params.GetInt("RNAP","INITIAL_COUNT",0)
		self.width      = N_DNA_POS(params.GetInt("RNAP","RNAP_SIZE",25))
		self.maxpos     = 1		# range of valid DNA positions [1..N_DNA-1]
		
		# list of rates (loaded from the param_file)		
		self.on_rate    = params.GetFloat("RNAP","ON_RATE",1.0)
		self.off_rate   = params.GetFloat("RNAP","OFF_RATE",1.0)
		self.trans_rate = params.GetFloat("RNAP","TRANSCRIPTION_RATE",10.0)
		self.init_rate  = params.GetFloat("RNAP","INIT_RATE",1.0)
		self.abort_rate = params.GetFloat("RNAP","INIT_ABORT",1.0)

		return
		
		######################################################################
	
	def Set_Outfile(output_file):
		self.outfile = output_file
		return
		
		######################################################################

	def Init_Reactants(self, N_DNA):

		self.maxpos    = N_DNA		# range of valid DNA positions [1..N_DNA]

		if (self.DEBUGGING):
			# add debugging counters to reactants list
			self.reactants["TI_COLLISION"] = 0
			self.reactants["TI_COLLISION_SD"] = 0
			self.reactants["RNAP_INIT"] = 0
			self.reactants["RNAP_ELONGATED"] = 0
			self.reactants["RNAP_ABORTED"] = 0
			for dir in ['w','c']:
				self.reactants["RNAP_COMPLETED_%c"%(dir.upper())] = 0

		self.reactants["rnap"] = self.count

		for i in xrange(1,N_DNA+1):
			self.reactants["rnap_bound_%04d"%i] = 0
			
			for dir in ['w','c']:
				self.reactants["rnap_abort_%c_%04d"%(dir, i)] = 0
				if (self.DEBUGGING):
					self.reactants["RNAP_STARTED_%c_%04d"%(dir.upper(),i)] = 0
					self.reactants["RNAP_TERMINATED_%c_%04d"%(dir.upper(),i)] = 0
					self.reactants["RNAP_SCRIBED_%c_%04d"%(dir.upper(),i)] = 0
			
				for stage in xrange(self.stages):
					self.reactants["rnap_%c_init_%d_%04d"%(dir, stage,i)] = 0

				self.reactants["rnap_%c_%04d"%(dir, i)] = 0
				self.reactants["rnap_%c_scribed_%04d"%(dir, i)] = 0

		return
		
		######################################################################

	def Write_Reactants(self):

		if (not self.outfile): 
			# write error msg
			return
			
		keys = self.reactants.keys()
		keys.sort()
		for key in keys:
			self.outfile.write("%-20s= %d;  \n"%(key, self.reactants[key]))
	
		return


	##########################################################################
	# Transitions
	##########################################################################

		######################################################################
		#
		# Create rules for binding to position in a specific direction.  
		#		Create rule for each initialization stage
		#		Create rule for entering elongation state
		# Return list of SSA_Rules
		#
		# Globals:
		#		N_DNA
		#
	def Binding(self, pos, tf_names, id, dir, stage):

		if (id and (id[-1] != '_')): 
			id += '_'

		direction = 1
		if (dir != 'w'): direction = -1
		
		# RULE:  RNAP + DNA -> RNAP_INIT
		rule = SSA_Rule("%sRNAP_%c_INIT_%d_%04d"%(id, dir.upper(),stage,pos))
		for name in tf_names:
			rule.AddStableReactant(name)

		for rpos in xrange(self.width):
			if ((pos+rpos) > 0) and ((pos+rpos) <= self.maxpos):
				rule.AddReactant("dna_%04d"%(pos+rpos))
				
		rule.AddReactant("rnap")

		rule.AddResultant("rnap_%c_init_%d_%04d"%(dir,stage,pos))
		rule.AddResultant("rnap_bound_%04d"%pos)
		for name in tf_names:
			rule.AddStableResultant(name)

		if (self.DEBUGGING):
			rule.AddResultant("RNAP_INIT")
	
		rule.rate = self.on_rate  # should be dependent on DNA sequence
					
		return [rule]
		
		
		######################################################################
		#
		# Create rule(s) for aborting the binding at position.  
	def Binding_Abort(self, pos, dir, stage):
		
		if (stage == -2):
			# RNAP_?_scribed -> RNAP_ABORT
			rule = SSA_Rule("RNAP_%c_ABORT_SCRIBED_%04d"%(dir.upper(),pos))
			rule.AddReactant("rnap_%c_%04d"%(dir,pos))
			rule.AddResultant("rnap_abort_%c_%04d"%(dir,pos))
			rule.rate  = RNAP_OFF_RATE
		elif (stage == -1):
			# RNAP_? -> RNAP_ABORT
			rule = SSA_Rule("RNAP_%c_ABORT_%04d"%(dir.upper(),pos))
			rule.AddReactant("rnap_%c_%04d"%(dir,pos))
			rule.AddResultant("rnap_abort_%c_%04d"%(dir,pos))
			rule.rate  = self.off_rate
		else:		
			# Create Abort from binding
			# RNAP_?_INIT -> RNAP_ABORT
			rule = SSA_Rule("RNAP_%c_ABORT_INIT_%d_%04d"%(dir.upper(),stage,pos))
			rule.AddReactant("rnap_%c_init_%d_%04d"%(dir,stage,pos))
			rule.AddResultant("rnap_abort_%c_%04d"%(dir,pos))
			rule.rate  = self.abort_rate * ((1.0 * self.stages-stage) / self.stages)  # less likely at each stage to abort
		
		return [rule]
		
		
		######################################################################
		#
		# Create rule(s) for TF stabilization the binding at position.  
	def Binding_Stabilization(self, pos, dir, stage, tf_offset, tf_width):
		
		if (pos < 1) or (pos > self.maxpos): return []
		
		direction = 1
		tf_pos    = pos - tf_width - tf_offset	# upstream edge of TF binding
		if (dir != 'w'): 
			direction = -1
			# find left most position for TF binding tf_offset from right edge of RNAP
			offset = pos + self.width + tf_offset
		
		# Keep TATA from unbinding during init
		rule = SSA_Rule("TATA_RNAP_%c_STABLE_%d_%04d"%(dir.upper(),stage,pos))
		rule.AddReactant("rnap_w_init_%d_%04d"%(dir, stage, pos))
		rule.AddReactant("TF_TATA_bound_%04d"%(tf_pos))
		rule.AddResultant("rnap_%c_init_%d_%04d"%(dir, stage, i))
		rule.AddResultant("TF_TATA_bound_%04d"%(tf_pos))
		rule.AddResultant("TATA_STABLE")
		rule.rate  = 10.0
		
		return [rule]
		
		######################################################################
		#
		# Create rule(s) for transition to previous stage to this stage at position.  
	def Initiate(self, pos, dir, stage):

		if (pos < 1) or (pos > self.maxpos): return []

		# RNAP_INIT_[stage-1] -> RNAP_INIT_[stage]
		rule = SSA_Rule("RNAP_%c_INIT_%d_%04d"%(dir.upper(), stage, pos))
		rule.AddReactant("rnap_%c_init_%d_%04d"%(dir, stage-1, pos))
		rule.AddResultant("rnap_%c_init_%d_%04d"%(dir, stage, pos))
		rule.rate  = self.init_rate

		return [rule]
		
		######################################################################
		#
		# Create rule(s) for transition to elongation at position.  
	def Activate(self, pos, dir, tf_offset, tf_width):
		
		if (pos < 1) or (pos > self.maxpos): return []

		tf_pos    = pos - tf_width - tf_offset	# upstream edge of TF binding
				
		# Transition from INIT to RNAP state
		# Final state change to RNAP_W 
		rule = SSA_Rule("RNAP_%c_ACTIVATE_%04d"%(dir.upper(), pos))
		rule.AddReactant("rnap_%c_init_%d_%04d"%(dir,self.stages-1,pos))

		# release the TATA
		if (self.TATA):
			rule.AddReactant("TF_TATA_bound_%04d"%(tf_pos)) 

		rule.AddResultant("rnap_%c_%04d"%(dir,pos))
		rule.AddResultant("RNAP_STARTED_%c_%04d"%(dir.upper(), pos))
		rule.AddResultant("RNAP_ELONGATED")

		if (self.TATA):
			rule.AddResultant("TF_TATA_bound_%04d"%(tf_pos))

		rule.rate  = self.init_rate

		return [rule]

		######################################################################
		#
		# Create rule(s) for transitioning from Aborting to Unbound.
		#		Pos is always the left most position of the component
	def Evict(self, pos, dir):
		
		if (pos < 1) or (pos > self.maxpos): return []

		# RNAP_ABORT -> RNAP + DNA
		rule = SSA_Rule("RNAP_EVICT_%c_%04d"%(dir,pos))
		rule.AddReactant("rnap_abort_%c_%04d"%(dir,pos))
		rule.AddReactant("rnap_bound_%04d"%(pos))
		rule.AddResultant("rnap")
		for rpos in xrange(self.width):
			if ((pos+rpos) > 0) and ((pos+rpos) <= self.maxpos):		
				rule.AddResultant("dna_%04d"%(pos+rpos))
		rule.AddResultant("RNAP_ABORTED")
		rule.rate  = .5  # let it sit there a bit

		return [rule]
		
		######################################################################
		#
		# Create rule(s) for transitioning from Transcribing to Transcribed at a position in a direction.
	def Transcribe(self, pos, dir):

		if (pos < 1) or (pos > self.maxpos): return []
		
		# RNAP_W -> RNAP_W_TRANSCRIBED
		rule = SSA_Rule("RNAP_%c_TRANSCRIBE_%04d"%(dir.upper(),pos))
		rule.AddReactant("rnap_%c_%04d"%(dir,pos))
		rule.AddResultant("rnap_%c_scribed_%04d"%(dir,pos))
		if (self.DEBUGGING):
			rule.AddResultant("RNAP_SCRIBED_%c_%04d"%(dir.upper(),pos))
		rule.rate  = 1.0
		rule.steps = NT_PER_GROUP / self.trans_rate	# transcription rate

		return [rule]
		
		######################################################################
		#
		# Create rule(s) for transitioning from Transcribing to Transcribed at a position in a direction.
	def Move(self, pos, dir):
		
		next_dna_pos  = pos + self.width	# next DNA position downstream to right
		next_pos      = pos + 1
		release_pos   = pos					# DNA position to release
		
		if (dir != 'w'): 
			next_dna_pos  = pos - 1			# next DNA position downstream to left
			next_pos      = pos - 1
			release_pos   = pos + self.width-1
			
		if (next_dna_pos < 1) or (next_dna_pos > self.maxpos): return []
		if (next_pos < 1) or (next_pos > self.maxpos): return []
		if (release_pos < 1) or (release_pos > self.maxpos): return []
			
		# RNAP_W_TRANSCRIBED[i] + DNA[i+1] -> DNA[i] + RNAP_W[i+1]
		rule = SSA_Rule("RNAP_%c_MOVE_%04d"%(dir.upper(),pos))
		rule.AddReactant("rnap_bound_%04d"%(pos))
		rule.AddReactant("rnap_%c_scribed_%04d"%(dir,pos))
		rule.AddReactant("dna_%04d"%(next_dna_pos))
		rule.AddResultant("rnap_bound_%04d"%(next_pos))
		rule.AddResultant("rnap_%c_%04d"%(dir,next_pos))
		rule.AddResultant("dna_%04d"%(release_pos))
		rule.rate  = 1.0

		return [rule]
		
		
		######################################################################
		#
		# Create rule(s) for evicting a nucleosome ahead of the RNAP at a position in a direction.
	def Evict_Nucleosome(self, pos, dir):
		
		NUC_SIZE = N_DNA_POS(147)

		nuc_pos  = pos + self.width	# next DNA position downstream to right
		if (dir != 'w'): 
			nuc_pos  = pos - NUC_SIZE	# next DNA position downstream to left

		if (nuc_pos < 1) or (nuc_pos > self.maxpos): return []
		if (pos < 1) or (pos > self.maxpos): return []
			
		# Force the removal of nucleosome ahead of RNAP_W		
		rule = SSA_Rule("NUC_RNAP_EVICT_%c_%04d"%(dir.upper(),pos))
		rule.AddReactant("rnap_%c_scribed_%04d"%(dir,pos))
		rule.AddReactant("nuc_stable_%04d"%(nuc_pos))		
		rule.AddResultant("rnap_%c_scribed_%04d"%(dir,pos))
		rule.AddResultant("nuc_unbinding_%04d"%(nuc_pos))
		rule.rate = 10000

		return [rule]
						
						
		######################################################################
		#
		# Create rule(s) for collision of two active RNAP at a position in a direction.
	def Collision(self, pos, dir):

		w_pos	= pos		
		c_pos	= pos + self.width		# next DNA position downstream to right
		if (dir != 'w'): 
			w_pos = pos - self.width	# next DNA position downstream to left
			c_pos = pos

		if (w_pos < 1) or (w_pos > self.maxpos): return []
		if (c_pos < 1) or (c_pos > self.maxpos): return []
			
		# RNAP_W[i] + RNAP_C[i+1] -> RNAP_W_ABORTING + RNAP_C_ABORTING
		rule = SSA_Rule("RNAP_COLLISION_%04d"%w_pos)
		rule.AddReactant("rnap_w_scribed_%04d"%w_pos)
		rule.AddReactant("rnap_c_scribed_%04d"%c_pos)
		rule.AddResultant("rnap_abort_w_%04d"%w_pos)	
		rule.AddResultant("rnap_abort_c_%04d"%c_pos)
		rule.AddResultant("TI_COLLISION")
		rule.rate = 1.0

		return [rule]
						
		######################################################################
		#
		# Create rule(s) for collision of an active RNAP and an initializing RNAP
		# at a position in a direction.
	def SittingDuck(self, pos, dir, d, stage):

		duck_pos = pos + self.width		# next DNA position downstream to right
		if (dir != 'w'): 
			duck_pos = pos - self.width	# next DNA position downstream to left
			
		if (pos < 1) or (pos > self.maxpos): return []
		if (duck_pos < 1) or (duck_pos > self.maxpos): return []

		rule = SSA_Rule("RNAP_%c_SD_%c_%d_%04d"%(dir.upper(),d,stage,pos))
		rule.AddReactant("rnap_%c_scribed_%04d"%(dir,pos))
		rule.AddReactant("rnap_%c_init_%d_%04d"%(d,stage,duck_pos))
		rule.AddResultant("rnap_%c_scribed_%04d"%(dir,pos))			# put active RNAP back
		rule.AddResultant("rnap_abort_%c_%04d"%(d,duck_pos))		# abort the duck
		rule.AddResultant("TI_COLLISION_SD")
		rule.rate = 1.0
					
		return [rule]
						
					
		######################################################################
		#
		# Create rules for Transcriptional Interference at position.  
		# There are two interference mechanisms, Collision and Sitting Duck.
		#	Collision is between two active RNAP moving in opposite directions
		#	Sitting Duck refers to an active RNAP evicting an intializing RNAP.
	def Interference(self, pos, dir):
		results = []
		
		# Only add collision rule(s) once because they take RNAP from each direction 
		if (dir == 'w'):		
			new_rules = self.Collision(pos, dir)
			results.extend(new_rules)
			
		# This active RNAP can interact and evict initalizing RNAP in either direction 
		# Must create rules for each possible initialization stage in each direction
		for d in ('w','c'):
			for stage in xrange(self.stages):
				new_rules = self.SittingDuck(pos, dir, d, stage)
				results.extend(new_rules)
		return results
		
		######################################################################
		#
		# Create rule(s) for termination of an active RNAP at a position in a direction.
	def Terminate(self, pos, dir):

		if (pos < 1) or (pos > self.maxpos): return []

		rule = SSA_Rule("RNAP_%c_FORCE_TERM_%04d"%(dir.upper(),pos))
		rule.AddReactant("rnap_%c_scribed_%04d"%(dir,pos))
		rule.AddReactant("rnap_bound_%04d"%(pos))
		rule.AddResultant("rnap")
		for rpos in xrange(self.width):
			if ((pos+rpos) > 0) and ((pos+rpos) <= self.maxpos):		
				rule.AddResultant("dna_%04d"%(pos+rpos))
		rule.AddResultant("RNAP_COMPLETED_%c"%(dir.upper()))
		rule.rate  = 1.0
		
		return [rule]
						
					
		######################################################################
		#
		# Create rules for binding to position.  
		#	For each direction
		#		Create rule for each initialization stage
		#		Create rule for entering elongation state
		# Return list of SSA_Rules
		#
	def Create_Binding(self, pos, TF_Names):
		results = []

		TATA_SIZE = N_DNA_POS(8)
		tf_pos    = 0
		
		# create binding in both directions
		for d in ('w', 'c'):
			new_rules = self.Binding(pos, [], "", d, 0)
			results.extend(new_rules)
			new_rules = self.Binding_Abort(pos, d, 0)
			results.extend(new_rules)
		
			if (self.TATA):
				new_rules = Binding_Stabilization(pos, dir, 0, 1, TATA_WIDTH)
				results.extend(new_rules)

			# RNAP_INIT_0 -> RNAP_INIT_1 -> ... -> RNAP_INIT_N -> RNAP_W
			for stage in xrange(1,self.stages):

				new_rules = self.Initiate(pos, d, stage)
				results.extend(new_rules)
			
				new_rules = self.Binding_Abort(pos, d, stage)
				results.extend(new_rules)

				if (self.TATA):
					new_rules = self.Binding_Stabilization(pos, dir, stage, 1, TATA_SIZE)
					results.extend(new_rules)

			new_rules = self.Binding_Abort(pos, d, -1) # abort from 
			results.extend(new_rules)

			new_rules = self.Activate(pos, d, 1, TATA_SIZE)
			results.extend(new_rules)

			new_rules = self.Evict(pos, d)
			results.extend(new_rules)

			new_rules = self.Transcribe(pos, d)
			results.extend(new_rules)

			new_rules = self.Move(pos, d)
			results.extend(new_rules)

			new_rules = self.Interference(pos, d)
			results.extend(new_rules)

			new_rules = self.Evict_Nucleosome(pos, d)
			results.extend(new_rules)

		return results
		
		######################################################################

		######################################################################
		# TATA Binding Protein required to complete PIC
		######################################################################
	def Create_TATA_Binding(self, pos):
		
		if (self.TATA):
# 			outfile.write("//\n// %s\n//\n"%"TATA Regions")
 			name = "TATA"
# 			motif_str  = params.GetString(name,"MOTIF","TATAWA")
# 			motif = New_Motif(motif_str)
# 			thresh  = params.GetFloat(name,"MOTIF_THRESH", 0.4)
# 			matches = Find_Motif_Matches(dna, motif, thresh)
# 			count  = params.GetInt(name,"INITIAL_COUNT",5)
# 			print "calling Define_TATA: N_DNA =", N_DNA
# 			Define_TATA(name, count, matches, dna, outfile)		
# 			outfile.write("TATA_STABLE  = 0;\n")
		return
		######################################################################

# end of SSA_RNAP
###############################################################################
###############################################################################

def Make_Results_Dir(path):
	if not os.path.exists(path):
		os.makedirs(path)
#end Make_Results_Dir

###############################################################################

def Usage():
	print 'Usage: %s -p <parm_file> [-o <output_filename>] [--DNA=<section>] [--results=<dir>] '%(re.sub('^.*/','',sys.argv[0]))
	print '\t'
	print '\n'

##########################################################################################

def Read_PWM(filename):
	pwm = []
	f = open(filename)
	lines = f.readlines()
	fields = lines[0].split()
	#print "fields:", fields
	name = fields[4]
	
	vals_A = lines[1].split('\t')
	vals_C = lines[2].split('\t')
	vals_G = lines[3].split('\t')
	vals_T = lines[4].split('\t')

	for i in range(1,len(vals_A)):
		vals = [float(vals_A[i]), float(vals_C[i]), float(vals_G[i]), float(vals_T[i])]
		pwm.append(vals)
	
	f.close()
	
#	print "PWM:"
#	for v in pwm:
#		print "\t",v
		
	return name, pwm
#end Read_PWM
	
	
##########################################################################################

def Make_PWM_Motif(filename, name):

	print "# Reading PWM from: [%s]"%filename
	mname, pwm = Read_PWM(filename)
	
	print "Building motif:", name
	m = MotifTools.toDict(pwm)
	motif = MotifTools.Motif_from_counts(m)
	motif.source = name
	
#	print "Motif:", motif.source
#	print "Max Motif Score:", motif.maxscore
#	print "Motif Summary:", motif.summary()
#	motif.printlogo(2.3,10)
	
	return motif
#end Make_PWM_Motif


###############################################################################

def Define_TATA(name, initial, matches, dna, outfile):

	if (len(matches) == 0): return
	
	outfile.write("%-18.18s = %d;  \n"%(name,initial))
	size_label = "TF_%s_SIZE"%name
	outfile.write("%-18.18s = %d;  \n"%(size_label,matches[0][3]-matches[0][0]+1))

	# dummy rule to force SIZE col in output
	rule = SSA_Rule("%s_size_output"%(name))
	rule.AddStableReactant(size_label)
	rule.AddReactant("dna_%04d"%0)
	rule.AddResultant("dna_%04d"%0)
	rule.rate = 0.00000000001
	rule.Write(outfile)

	# check for overrides
	override_offrate     = params.GetFloat(name,"OFF_RATE", None)
	
	# Define TATA at every position
	for i in xrange(1,N_DNA+1):
		outfile.write("%-18s = %d;  \n"%("TF_%s_bound_%04d"%(name,i),0))
	
	prev = [-1,-1,-1,-1,-1,-1]  # {dna_pos, dscore, strand, dna_end, start_seq, end_seq}
	for m in matches:
		p = m[0]
		rate = m[1]
		print "TATA",m

		# check for override
		off_rate = (1.1 - rate) / 2		# should this be different rate?
		if (override_offrate):
			off_rate = override_offrate

		#create rule for TF binding at that position
		rule = SSA_Rule("%s_bind_%04d"%(name,m[4]))
		rule.AddReactant("dna_%04d"%p)
		rule.AddStableReactant(name)
		rule.AddResultant("TF_%s_bound_%04d"%(name,p))
		rule.AddResultant("TF_bound_%04d"%(p))  # generic binding at position
		rule.rate = rate / 2
		rule.Write(outfile)

		if (p == prev[0]): continue		# already added the removal rules
		
		#create rule for TF unbinding at that position
		rule = SSA_Rule("%s_unbind_%04d"%(name,p))
		rule.AddReactant("TF_%s_bound_%04d"%(name,p))
		rule.AddReactant("TF_bound_%04d"%(p))  # generic binding at position
		rule.AddStableResultant(name)
		rule.AddResultant("dna_%04d"%p)
#		rule.rate = (1.1 - rate)/2		# should this be different rate?
		rule.rate = off_rate
		rule.Write(outfile)
		
		# force TF unbinding if RNAP wants this space
		rule = SSA_Rule("%s_rnap_w_%04d"%(name,p))
		rule.AddReactant("TF_%s_bound_%04d"%(name,p))
		rule.AddReactant("TF_bound_%04d"%(p))  # generic binding at position
		rule.AddReactant("rnap_w_scribed_%04d"%(p-1))
		rule.AddStableResultant(name)
		rule.AddResultant("dna_%04d"%p)
		rule.AddResultant("rnap_w_scribed_%04d"%(p-1))
		rule.rate = 1.0
		if (p  > 1):
			rule.Write(outfile)
		
		# force TF unbinding if RNAP wants this space
		rule = SSA_Rule("%s_rnap_c_%04d"%(name,p))
		rule.AddReactant("TF_%s_bound_%04d"%(name,p))
		rule.AddReactant("TF_bound_%04d"%(p))  # generic binding at position
		rule.AddReactant("rnap_c_scribed_%04d"%(p+1))
		rule.AddStableResultant(name)
		rule.AddResultant("dna_%04d"%p)
		rule.AddResultant("rnap_c_scribed_%04d"%(p+1))
		rule.rate = 1.0
		if (p < N_DNA):
			rule.Write(outfile)
		
		# TATA recruits RNAP, add  rules to recruit
		offset = (params.GetInt(name,"RNAP_OFFSET",1) + NT_PER_GROUP-1) / NT_PER_GROUP
		recruit_rate = params.GetFloat(name, "RNAP_RECRUIT_RATE", 0.1)
		names = [ "TF_%s_bound_%04d"%(name,p) ]
		if (p+offset < N_DNA):
			RNAP_INIT(name, p+offset, 1, names, recruit_rate, dna, outfile)
		if (p-offset > 0):
			RNAP_INIT(name, p-offset, -1, names, recruit_rate, dna, outfile)

# end Define_TATA(name, initial, matches, dna, params, outfile)
###############################################################################
# Returns an adjusted strength based on score [0..1]
# returned value is in range [0..1]
def Strength_Sigmoidal(score):
	adjusted = score * 10. - 5.
	s = 1. / (1. + math.exp( -adjusted ))
	return s
	
###############################################################################
def Define_TF(name, initial, matches, dna, outfile, model_RNAP=True):
	global LOCAL_CONCENTRATION

	if (len(matches) == 0): return
	
	outfile.write("%-18.18s = %d;  \n"%(name,initial))
	size_label = "TF_%s_SIZE"%name
	outfile.write("%-18.18s = %d;  \n"%(size_label,matches[0][3]-matches[0][0]+1))
	
	# dummy rule to force SIZE col in output
	rule = SSA_Rule("%s_size_output"%(name))
	rule.AddStableReactant(size_label)
	rule.AddReactant("dna_%04d"%0)
	rule.AddResultant("dna_%04d"%0)
	rule.rate = 0.00000000001
	rule.Write(outfile)

	# check for overrides
	override_offrate     = params.GetFloat(name,"OFF_RATE", None)
	
	for m in matches:
		p       = m[0]
		on_rate = m[1]
		strand  = m[2]
		end_pos = m[3]
		score   = m[6] / m[7]
			
		# check for override
		if (override_offrate):
			if (override_offrate < 0):
				# try sigmoidal
				s = Strength_Sigmoidal(score)
				off_rate = (1 - s) * -override_offrate
				print "Score=%f"%score, "Strength=%f"%s,"Rate=%f"%(-override_offrate),"Off-rate=%f"%off_rate
				#off_rate = 1 - s * -override_offrate
				#off_rate = -override_offrate * score
			else:
				off_rate = override_offrate
		else:
			off_rate = 1
			if (on_rate < 1.0):
				off_rate = .99 - on_rate		# should this be different rate?
		
		if (p < 1): continue
		if (end_pos >= N_DNA): continue

		outfile.write("// %s (%d..%d) Score=%5.2f\n"%(name, m[4],m[5], score))
		
		outfile.write("%-18s = %d;  \n"%("TF_%s_bound_%04d"%(name,p),0))

		#create rule for TF binding at that position
		rule = SSA_Rule("%s_bind_%04d"%(name,p))
		for n in xrange(p, end_pos+1):
			rule.AddReactant("dna_%04d"%n)
		rule.AddStableReactant(name)
		rule.AddResultant("TF_%s_bound_%04d"%(name,p))
		rule.AddResultant("TF_bound_%04d"%(p))  # generic binding at position  DO I NEED SET THIS AT ALL POSITIONS OF TF???
		rule.rate = on_rate 
		rule.Write(outfile)

		#create rule for TF unbinding at that position
		rule = SSA_Rule("%s_unbind_%04d"%(name,p))
		rule.AddReactant("TF_%s_bound_%04d"%(name,p))
		rule.AddReactant("TF_bound_%04d"%(p))  # generic binding at position
		rule.AddStableResultant(name)
		for n in xrange(p, end_pos+1):
			rule.AddResultant("dna_%04d"%n)

		rule.rate = off_rate
		rule.Write(outfile)
		
		if (model_RNAP):
			# force TF unbinding if RNAP wants this space
			rule = SSA_Rule("%s_rnap_w_%04d"%(name,p))
			rule.AddReactant("TF_%s_bound_%04d"%(name,p))
			rule.AddReactant("TF_bound_%04d"%(p))  # generic binding at position
			rule.AddReactant("rnap_w_scribed_%04d"%(p-1))
			rule.AddStableResultant(name)
			for n in xrange(p, end_pos+1):
				rule.AddResultant("dna_%04d"%n)
			rule.AddResultant("rnap_w_scribed_%04d"%(p-1))
			rule.rate = 1.0
			if (p  > 1):
				rule.Write(outfile)
			
			# force TF unbinding if RNAP wants this space
			rule = SSA_Rule("%s_rnap_c_%04d"%(name,p))
			rule.AddReactant("TF_%s_bound_%04d"%(name,p))
			rule.AddReactant("TF_bound_%04d"%(p))  # generic binding at position
			rule.AddReactant("rnap_c_scribed_%04d"%(end_pos+1))
			rule.AddStableResultant(name)
			for n in xrange(p, end_pos+1):
				rule.AddResultant("dna_%04d"%n)
			rule.AddResultant("rnap_c_scribed_%04d"%(end_pos+1))
			rule.rate = 1.0
			if ((end_pos+1) < N_DNA):
				rule.Write(outfile)
			
			# if this TF recruits RNAP, add  rules to recruit
			recruits_rnap = params.GetInt(name,"RNAP_RECRUIT",0)
			if (recruits_rnap):
				offset = (params.GetInt(name,"RNAP_OFFSET",1) + NT_PER_GROUP-1) / NT_PER_GROUP
				recruit_rate = params.GetFloat(name, "RNAP_RECRUIT_RATE", 0.1)
				names = [ "TF_%s_bound_%04d"%(name,p) ]
				if (p+offset < N_DNA):
					RNAP_INIT(name, p+offset, 1, names, recruit_rate, dna, outfile)
				if (p-offset > 0):
					RNAP_INIT(name, p-offset, -1, names, recruit_rate, dna, outfile)


# end Define_TF(name, initial, matches, outfile, model_RNAP)

###############################################################################

def Define_TF_From_INI(name, dna, thresh, outfile, model_RNAP=True):
	motif = None
	motif_seq = params.GetString(name, "MOTIF")
	print name, motif_seq
	if (motif_seq):
		motif = New_Motif(motif_seq, name)
		matches = Find_Motif_Matches(dna, motif, thresh)
		count  = params.GetInt(name,"INITIAL_COUNT",5)
		count  = count * LOCAL_CONCENTRATION
 		Define_TF(name, count, matches, dna, outfile, model_RNAP)
	return motif

###############################################################################

def Find_DNA_Matches(dna, NT_PER_GROUP, N_DNA, motif):
	matches = []
	rev_motif = motif[::-1]
	prev = -1
	
	for pos in xrange(len(dna)-len(motif)):
		section = dna[pos:pos+len(motif)]
	#	print "Comparing (%s == %s) at %d"%(section,motif,pos)
		if (section == motif) or (section == rev_motif):
			dna_pos = (pos / NT_PER_GROUP) + 1
			if (dna_pos != prev):
				print "found motif match at", pos
				matches.append([dna_pos, 0.8])
				prev = dna_pos
				
	print "Matches:", matches
	return matches
	
#end Find_DNA_Matches

###############################################################################

def Calc_Nucleosome_Rates(dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE):
	positional_nuc_rates = [[NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE]]
	
	print "N_DNA =", N_DNA
	print "NT_PER_GROUP =", NT_PER_GROUP
	print "NUC prob:"
	
	pos = 0
	for i in xrange(N_DNA):
		# calc AT/GC ratio in group
		GC = 0.
		count = 0
		consecutive_A = 0
		consecutive_T = 0
		cA = cT = 0
		for n in xrange(NT_PER_GROUP):
			if (pos+n < len(dna)):
				if (dna[pos+n] == 'A'):		# either start or increase length of a series
					cA += 1
				else:
					if (cA > consecutive_A):
						consecutive_A = cA
					cA = 0

				if (dna[pos+n] == 'T'):		# either start or increase length of a series
					cT += 1
				else:
					if (cT > consecutive_T):
						consecutive_T = cT
					cT = 0
				
						
				if (dna[pos+n] == 'G') or (dna[pos+n] == 'C'):
					GC += 1
				count += 1
			
		GC_content = (GC / count)

		# create rates [on,off] for this position
		rates = [GC_content,1.-GC_content]
		
		if (consecutive_A >= 5) or (consecutive_T >= 5):
			# rate lower due to stiffness
			rates[0] /= 2
			rates[1] = 1. - rates[0]
			
		# add positional rates [on,off]
		positional_nuc_rates.append(rates)
		print "\t%3d"%i,dna[pos:pos+NT_PER_GROUP-1], rates[0], "(%2d of %2d) dA=%2d, dT=%2d"%(GC,count,consecutive_A,consecutive_T)
		pos += NT_PER_GROUP
	
	line1 = "     :" # 10 ths
	line2 = "     :" # 100 ths
	digits = "01234567890"
	for i in xrange(1,N_DNA+1):
		r = int((positional_nuc_rates[i][0]*10)%10)
		line1 += digits[r]
		r = int((positional_nuc_rates[i][0]*100)%10)
		line2 += digits[r]
#		print "        :",positional_nuc_rates[i:i+4]
	print line1
	#print line2

#	print positional_nuc_rates
	
	return positional_nuc_rates
#end Calc_Nucleosome_Rates

###############################################################################

def Read_Nuc_Occupancy_File(filename, chromo, DNA_start, DNA_end):
	# each line of the input file: "chromo \t position \t occupancy"

	# Open position/prob file
	occFile = open(filename, "r")
	finfo    = os.stat(filename)
#	sites = {} 		# for each chromosome, create list of entrys, <start, occ, orig line>
	occupancy = [(0,0,"")]
	
	# read file records
	print "Reading nucleosome position occupancy file [%s, [%d:%d]]:"%(chromo, DNA_start, DNA_end)
	
	total  = finfo.st_size
	n      = 0
	i      = 0	
	count  = 0
	
	leader = chromo
	if (leader[:3] == 'chr'):
		leader = leader[3:]
	
	for line in occFile.xreadlines():
		i += 1
		count += len(line)
		if ((i%100000) == 0): 
			sys.stdout.write("\r processing line: %-10d (%3d%%) %10d entries"%(i,count*100./total, n))
			sys.stdout.flush()
		
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		if (line[:len(leader)] != leader): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		chr    = fields[0]
		if (chr[:3] != 'chr'):
			chr = 'chr' + chr
		if (chr != chromo): continue

		# found an entry for the correct chromo
		start  = int(fields[1]) 
		if (start < DNA_start): continue
		if (start > DNA_end):   continue
		
		occ   = float(fields[2])
		if (occ < 0): print line
		
		# create entry = <start, occ, orig line>
		entry = (start, occ, line)
		occupancy.append(entry)
		n += 1
	
	print "\n",len(occupancy),"entries in occupancy list"
	occFile.close()
	return occupancy
# end of Read_Nuc_Occupancy_File

###############################################################################

def Read_Nuc_Prob_File(filename, chromo):
	# Open position/prob file
	probFile = open(filename, "r")
	finfo    = os.stat(filename)
#	sites = {} 		# for each chromosome, create list of entrys, <start, prob, orig line>
	probs = [(0,0,0,"")]
	
	# read file records
	print "Reading nucleosome position prob file [%s]:"%chromo
	total  = finfo.st_size
	n      = 0
	i      = 0	
	count  = 0
	
	leader = chromo
	if (leader[:3] == 'chr'):
		leader = leader[3:]
	
	for line in probFile.xreadlines():
		i += 1
		count += len(line)
		if ((i%100000) == 0): 
			sys.stdout.write("\r processing line: %-10d (%3d%%) %10d entries"%(i,count*100./total, n))
			sys.stdout.flush()
		
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		if (line[:len(leader)] != leader): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		chr    = fields[0]
		if (chr[:3] != 'chr'):
			chr = 'chr' + chr
		if (chr != chromo): continue
		start  = int(fields[2]) 
		prob   = float(fields[5])
		if (prob < 0): print line
		
		# create entry = <start, prob, orig line>
		end = int(fields[3])
		entry = (min(start,end), prob, line)
#		if (sites.has_key(chr)):
#			sites[chr].append(entry)
#		else:
#			sites[chr] = [entry]
		probs.append(entry)
		n += 1
	
	print "\n",len(probs),"entries in probs list"
	probFile.close()
	return probs
# end of Read_Nuc_Prob_File

###############################################################################

def Read_Nuc_Prob_File_OLD(filename, chromo):
	# Open position/prob file
	probFile = open(filename, "r")
#	sites = {} 		# for each chromosome, create list of entrys, <start, prob, orig line>
	probs = [(0,0,0,"")]
	
	# read file records
	print "Reading nucleosome position prob file [%s]:"%chromo
	lines = probFile.readlines()
	print "\tread %d lines"%len(lines)
	total = len(lines)
	n     = 0
	
	leader = chromo
	if (leader[:3] == 'chr'):
		leader = leader[3:]
	
	for i,line in enumerate(lines):
		if ((i%100000) == 0): 
			sys.stdout.write("\r processing line: %-10d (%3d%%) %10d entries"%(i,i*100./total, n))
			sys.stdout.flush()
		
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		if (line[:len(leader)] != leader): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split("\t")
		chr    = fields[0]
		if (chr[:3] != 'chr'):
			chr = 'chr' + chr
		if (chr != chromo): continue
		start  = int(fields[2]) 
		prob   = float(fields[5])
		if (prob < 0): print line
		
		# create entry = <start, prob, orig line>
		end = int(fields[3])
		entry = (min(start,end), prob, line)
#		if (sites.has_key(chr)):
#			sites[chr].append(entry)
#		else:
#			sites[chr] = [entry]
		probs.append(entry)
		n += 1
	
	print "\n",len(probs),"entries in probs list"
	probFile.close()
	return probs
# end of Read_Nuc_Prob_File

###############################################################################

def Calc_Nucleosome_Rates_From_File(filename, chromo, start, end, dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE, NT_PER_GROUP, START_POS):
	positional_nuc_rates = [[NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE]]
	
	print "NUCLEOSOME probability file (%s):"%filename
	probs = Read_Nuc_Prob_File(filename, chromo)
	
	n_dna = (end - start + 1 + NT_PER_GROUP-1) / NT_PER_GROUP
	print "Nucs from %d to %d (%d groups at %d per group)"%(start, end, n_dna, NT_PER_GROUP)
	
	pos = start
	for i in xrange(n_dna):
		sum   = 0.
		count = 0
		vals = []
		for n in xrange(NT_PER_GROUP):
			if ((pos+n) < len(probs)):
				entry = probs[pos+n] 
				sum += entry[1]
				vals.append(entry[1])
				count += 1
		#		print "\t%d %f"%(pos+n,entry[1])

#		# use avg for rate
#		rate = 0.
#		if (count > 0):
#			rate = (sum / count)

#		# use the max for the rate
#		rate = max(vals)
		
		# use the sum (multiply in normal space) for the rate
		rate = sum
		
	#	print "sum [%d - %d] = %f ==> %f ===>%d : MAX(%f)"%(pos, pos+NT_PER_GROUP,sum, rate, 100-int(math.ceil(-10 * math.log(rate,10))),max(vals))
		
		# check for poly A/T. Adjust rates if found
		nt_count = 0
		cA = cT  = 0
		for n in xrange(147+NT_PER_GROUP):
			dna_pos = pos-start+n
			if (dna_pos < len(dna)):
				if (dna[dna_pos] == 'A'):		# either start or increase length of a series
					cA += 1
				else:		# check to see if poly A requires reduction in formation probability
					if (cA >= 6):
						nt_count += cA
					cA = 0

				if (dna[dna_pos] == 'T'):		# either start or increase length of a series
					cT += 1
				else:
					if (cT >= 6):
						nt_count += cT
					cT = 0

		reduce = 1.0
		for k in xrange(nt_count/5):
			reduce /= 10 #3 # reduce by number of half turns of DNA
		note = ""
		if (reduce < 1.0):
			if (reduce < 0): reduce = 0.
			note = " >>>> reducing rate %.5f at %d by %.5f == %.5f [%d,%-d]"%(rate, pos, reduce, rate*reduce, pos, pos+147)
			rate *= reduce 		
		#	print "sum [%d - %d] = %f ==> %f ===>%d : MAX(%f)"%(pos, pos+NT_PER_GROUP,sum, rate, 100-int(math.ceil(-10 * math.log(rate,10))),max(vals))
#		print "positions[%d..%d]    cA=%d  cT=%d"%(pos, pos+147+NT_PER_GROUP, consecutive_A,consecutive_T)	
		
		# create rates [on,off] for this position
		on_rate  = NUCLEOSOME_ON_RATE
		off_rate = NUCLEOSOME_OFF_RATE
		mode = 5 # 3 # 1 
		if   (mode == 1):
			on_rate  = NUCLEOSOME_ON_RATE/2  + (NUCLEOSOME_ON_RATE * rate)
			off_rate = NUCLEOSOME_OFF_RATE*2 - (NUCLEOSOME_OFF_RATE * rate)
		elif (mode == 2):
			base_on  = .005
			base_off = .5
			on_rate  = (NUCLEOSOME_ON_RATE  * base_on)  + (NUCLEOSOME_ON_RATE  * rate)
			off_rate = (NUCLEOSOME_OFF_RATE * base_off) + (NUCLEOSOME_OFF_RATE * (1-rate))
		elif (mode == 3):
			base_on  = .001
			base_off = .001
			on_rate  = min((NUCLEOSOME_ON_RATE  * base_on)  + (NUCLEOSOME_ON_RATE  * rate),     1.)
			off_rate = min((NUCLEOSOME_OFF_RATE * base_off) + (NUCLEOSOME_OFF_RATE * (1-rate)), 1.)
		elif (mode == 4):
			base_on  = .1
			base_off = .5
			on_rate  = min((NUCLEOSOME_ON_RATE  * base_on), (NUCLEOSOME_ON_RATE  * rate))
			off_rate = max((NUCLEOSOME_OFF_RATE * base_off),(NUCLEOSOME_OFF_RATE * (1-rate)))
		elif (mode == 5):
			# use default rates * reduction for polyT
			on_rate  = NUCLEOSOME_ON_RATE  * reduce
			off_rate = NUCLEOSOME_OFF_RATE / reduce
		elif (mode > 0):
			on_rate  = (NUCLEOSOME_ON_RATE * rate)
			off_rate = (NUCLEOSOME_OFF_RATE * (1.-rate))
	
		rates = [on_rate, off_rate]
		
		# add positional rates [on,off]
		positional_nuc_rates.append(rates)
		print "\t%5d:[%10d,%10d] = [%.8f,%.8f]"%(i, pos,pos+NT_PER_GROUP-1,rates[0],rates[1]), note
		pos += NT_PER_GROUP
	
	#Print_Percent_Graph_LOG(positional_nuc_rates, "Nucleosome Positional Rates:", NT_PER_GROUP, START_POS)
	 
	return positional_nuc_rates
#end Calc_Nucleosome_Rates_From_File
###############################################################################

def Calc_Nucleosome_Rates_From_File_OLD(filename, chromo, start, end, dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE, NT_PER_GROUP, START_POS):
	positional_nuc_rates = [[NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE]]
	
	print "NUCLEOSOME probability file (%s):"%filename
	probs = Read_Nuc_Prob_File(filename, chromo)
	
	n_dna = (end - start + 1 + NT_PER_GROUP-1) / NT_PER_GROUP
	print "Nucs from %d to %d (%d groups at %d per group)"%(start, end, n_dna, NT_PER_GROUP)
	
	pos = start
	for i in xrange(n_dna):
		sum   = 0.
		count = 0
		vals = []
		for n in xrange(NT_PER_GROUP):
			if ((pos+n) < len(probs)):
				entry = probs[pos+n] 
				sum += entry[1]
				vals.append(entry[1])
				count += 1
		#		print "\t%d %f"%(pos+n,entry[1])

#		# use avg for rate
#		rate = 0.
#		if (count > 0):
#			rate = (sum / count)

#		# use the max for the rate
#		rate = max(vals)
		
		# use the sum (multiply in log space) for the rate
		rate = sum
		
	#	print "sum [%d - %d] = %f ==> %f ===>%d : MAX(%f)"%(pos, pos+NT_PER_GROUP,sum, rate, 100-int(math.ceil(-10 * math.log(rate,10))),max(vals))
		
		# check for poly A/T. Adjust rates if found
		consecutive_A = 0
		consecutive_T = 0
		cA = cT = 0
		for n in xrange(147+NT_PER_GROUP):
			dna_pos = pos-start+n
			if (dna_pos < len(dna)):
				if (dna[dna_pos] == 'A'):		# either start or increase length of a series
					cA += 1
				else:
					if (cA > consecutive_A):
						consecutive_A = cA
					cA = 0

				if (dna[dna_pos] == 'T'):		# either start or increase length of a series
					cT += 1
				else:
					if (cT > consecutive_T):
						consecutive_T = cT
					cT = 0

		if (consecutive_A >=6) or (consecutive_T >= 6):
			# rate -= 0.1 # reduce by const
			rate *= 0.8 # reduce by percentage (.8 = 20% reduction)
			
		#	print " >>>> reducing rate at", pos
		#	print "sum [%d - %d] = %f ==> %f ===>%d : MAX(%f)"%(pos, pos+NT_PER_GROUP,sum, rate, 100-int(math.ceil(-10 * math.log(rate,10))),max(vals))
#		print "positions[%d..%d]    cA=%d  cT=%d"%(pos, pos+147+NT_PER_GROUP, consecutive_A,consecutive_T)	
		
		# create rates [on,off] for this position
		off_rate = 1.-rate
		rates = [rate, off_rate]
		
		# add positional rates [on,off]
		positional_nuc_rates.append(rates)
	#	print "\t[",pos,pos+NT_PER_GROUP-1, "] = %f"%rates[0]
		pos += NT_PER_GROUP
	
	Print_Percent_Graph_LOG(positional_nuc_rates, "Nucleosome Positional Rates:", NT_PER_GROUP, START_POS)
	 
	return positional_nuc_rates
#end Calc_Nucleosome_Rates_From_File_OLD

###############################################################################

def Get_Motif(motifs, motif_name):
	for m in motifs:
		if (m.source.lower() == motif_name.lower()):
			return m
			
def New_Motif(s_motif, name=None):
		motif_999 = MotifTools.Motif_from_text(s_motif)	
		if (name):
			motif_999.source = name
		else:
			motif_999.source = "TF_%s_"%s_motif.upper()
		return motif_999

###############################################################################
# Find all positions with matches to motif
# Creaet list of matching positions with following format:
# [start pos, percent, strand, end pos, upstream occlusion pos, downstream occlusion pos, raw score, max score]
#
def Find_Motif_Matches(dna, motif, thresh):
	positions = []
	prev_start = -1
	prev_end   = -1
	
	use_raw_score = True	# if true, use raw score to create relative binding strength
	
	print "Find_Motif_Matches for %s @ %f"%(motif.source,thresh)
	
	subseqs,endpoints,scores = motif.scan(dna,(thresh*motif.maxscore)-0.0000001)

	line = "Matches: [%s]"%(motif.source)
	count = 0

	# Get Global occlusion sizes 
	upstream_occlusion   = params.GetFloat("SRB","OCCLUSION_5", 0)
	downstream_occlusion = params.GetFloat("SRB","OCCLUSION_3", 0)

	# check to see if there is an override
	max_on_rate          = params.GetFloat(motif.source, "ON_RATE",  0.1)
	upstream_occlusion   = params.GetFloat(motif.source,"OCCLUSION_5", upstream_occlusion)
	downstream_occlusion = params.GetFloat(motif.source,"OCCLUSION_3", downstream_occlusion)

	print "[%s] using -%d to +%d for occlusion area, length = %d"%(motif.source,upstream_occlusion, downstream_occlusion, len(motif.oneletter)+upstream_occlusion+downstream_occlusion)
	
	# process each match				
	for idx in range(len(subseqs)):
		start,stop = endpoints[idx]
	#	print "Motif found at [%7d,%7d]"%(start,stop)
		subseq     = subseqs[idx]
		score      = scores[idx]
	#	dscore     = ((score/motif.maxscore)) * max_on_rate
		# try sigmoidal function
		dscore = 1./(1.+math.exp(- (score/motif.maxscore*10-5.))) * max_on_rate
		if (use_raw_score):
			dscore = (score/20.) * max_on_rate
		rescore    = motif.score(subseq)
		strand     = "+"
		if (rescore < 0):
			strand   = "-"
			#dscore  *= -1.0

	##	print "\tfound motif match at", start
		dna_pos = int((start-upstream_occlusion) / NT_PER_GROUP) + 1
		dna_end = int((stop+downstream_occlusion) / NT_PER_GROUP) + 1
		if (dna_pos != prev_start) and (dna_end != prev_end):
	##		print "\tadding motif match at", start
			positions.append([dna_pos, dscore, strand, dna_end, start-upstream_occlusion, stop+downstream_occlusion, score, motif.maxscore])
			prev_start = dna_pos
			prev_end   = dna_end

			if (count%4 == 0):	
				line += "\n\t"
			line += " [%-7d(%7d..%-7d),(%4d..%-4d),%5f,%5.1f]"%(start+START_POS, start-upstream_occlusion+START_POS, stop+downstream_occlusion+START_POS, dna_pos, dna_end, dscore, score)
			count += 1		
					
	#print "Matches:", positions
	print line
	
	return positions

###############################################################################
# Binds a nucleosome to DNA where DNA for all positions is available and the
# DNA linker positions on either side are either available or TF bound
# 
###############################################################################
def Nucleosome_Binding(params, positional_nuc_rates, pos, TF_left, TF_right, outfile):
	N_GROUP_PER_NUCLEOSOME = (147 + NT_PER_GROUP-1) / NT_PER_GROUP	
	NUCLEOSOME_ON_RATE = params.GetFloat("NUCLEOSOME","ON_RATE",1.0)

	chr_L = 'F'
	if (TF_left): chr_L = 'T'
	chr_R = 'F'
	if (TF_right): chr_R = 'T'
	
	rule = SSA_Rule("Nucleosome_binding%c%c_%04d"%(chr_L,chr_R,pos))
	rule.AddStableReactant("histones")
	for n in xrange(N_GROUP_PER_NUCLEOSOME):
		if (pos+n <= N_DNA):
			rule.AddReactant("dna_%04d"%(pos+n))
	if (pos > 1):									# allow for linker
		if (TF_left):
			rule.AddReactant("TF_bound_%04d"%(pos-1))
		else:
			rule.AddReactant("dna_%04d"%(pos-1))
	if (pos+N_GROUP_PER_NUCLEOSOME <= N_DNA):		# allow for linker
		if (TF_right):
			rule.AddReactant("TF_bound_%04d"%(pos+N_GROUP_PER_NUCLEOSOME))			
		else:
			rule.AddReactant("dna_%04d"%(pos+N_GROUP_PER_NUCLEOSOME))			
	rule.AddResultant("nuc_binding_%04d"%pos)
	rule.AddResultant("nuc_bound_%04d"%pos)
#	rule.AddResultant("NUC_BINDING")
	if (pos > 1):									# release linker
		if (TF_left):
			rule.AddResultant("TF_bound_%04d"%(pos-1))			
		else:
			rule.AddResultant("dna_%04d"%(pos-1))
	if (pos+N_GROUP_PER_NUCLEOSOME <= N_DNA):		# release linker
		if (TF_right):
			rule.AddResultant("TF_bound_%04d"%(pos+N_GROUP_PER_NUCLEOSOME))			
		else:
			rule.AddResultant("dna_%04d"%(pos+N_GROUP_PER_NUCLEOSOME))
	rule.rate = max(positional_nuc_rates[pos][0], 0.00001)	# min rate of 0.00001
	rule.Write(outfile)

###############################################################################
# This version handles open DNA (variable length upto 32 DNA units) linker
# to left and right of nucleosome binding area
#
def Nucleosome_Binding2(params, positional_nuc_rates, pos, linkerLeft, TF_left, linkerRight, TF_right, outfile):

	N_GROUP_PER_NUCLEOSOME = (147 + NT_PER_GROUP-1) / NT_PER_GROUP	
	NUCLEOSOME_ON_RATE = params.GetFloat("NUCLEOSOME","ON_RATE",1.0)

	
	rule = SSA_Rule("Nucleosome_binding_%0*d_%0*d_%04d"%(linkerLeft, TF_left, linkerRight, TF_right, pos))
	rule.AddStableReactant("histones")
	for n in xrange(N_GROUP_PER_NUCLEOSOME):
		if (pos+n <= N_DNA):
			rule.AddReactant("dna_%04d"%(pos+n))

	# for each position to left, check if TF should be bound
	for i in xrange(linkerLeft):
		linker_pos = pos - 1 - i
		if (linker_pos > 0):
			if ((TF_left&(1<<i)) > 0):
				rule.AddReactant("TF_bound_%04d"%(linker_pos))
			else:
				rule.AddReactant("dna_%04d"%(linker_pos))
				
	# for each position to right, check if TF should be bound
	for i in xrange(linkerRight):
		linker_pos = pos + N_GROUP_PER_NUCLEOSOME + i
		if (linker_pos <= N_DNA):		# allow for linker
			if ((TF_right&(1<<i)) > 0):
				rule.AddReactant("TF_bound_%04d"%(linker_pos))			
			else:
				rule.AddReactant("dna_%04d"%(linker_pos))			
				
	rule.AddResultant("nuc_binding_%04d"%pos)
	rule.AddResultant("nuc_bound_%04d"%pos)
#	rule.AddResultant("NUC_BINDING")
	# for each position to left, check if TF should be released
	for i in xrange(linkerLeft):
		linker_pos = pos - 1 - i
		if (linker_pos > 0):
			if ((TF_left&(1<<i)) > 0):
				rule.AddResultant("TF_bound_%04d"%(linker_pos))
			else:
				rule.AddResultant("dna_%04d"%(linker_pos))
				
	# for each position to right, check if TF should be bound
	for i in xrange(linkerRight):
		linker_pos = pos + N_GROUP_PER_NUCLEOSOME + i
		if (linker_pos <= N_DNA):		# allow for linker
			if ((TF_right&(1<<i)) > 0):
				rule.AddResultant("TF_bound_%04d"%(linker_pos))			
			else:
				rule.AddResultant("dna_%04d"%(linker_pos))			

	rule.rate = max(positional_nuc_rates[pos][0], 0.00001)	# min rate of 0.00001
	rule.Write(outfile)

###############################################################################
# This version handles linker sizes on either side of nucleosome
# States: unbound -> binding -> stable -> unbinding -> unbound  - normal transitions
#		: unbound -> binding -> unbound  - when nucleosome binding too close to others
#
def Nucleosome_Binding3(params, positional_nuc_rates, pos, linkerLeft, linkerRight, outfile):

	if (pos >= N_DNA):
		return # cannot process the edge
		
	N_GROUP_PER_NUCLEOSOME = (147 + NT_PER_GROUP-1) / NT_PER_GROUP	
	NUCLEOSOME_ON_RATE     = params.GetFloat("NUCLEOSOME","ON_RATE",1.0)
	NUCLEOSOME_OFF_RATE    = params.GetFloat("NUCLEOSOME","OFF_RATE",1.0)
	NUCLEOSOME_ARORT_RATE  = params.GetFloat("NUCLEOSOME","ABORT_RATE",1000.0)
	
	rule = SSA_Rule("Nucleosome_binding_%04d"%(pos))
	rule.AddStableReactant("histones")
	for n in xrange(N_GROUP_PER_NUCLEOSOME):
		if (pos+n <= N_DNA):
			rule.AddReactant("dna_%04d"%(pos+n))
					
	rule.AddResultant("nuc_binding_%04d"%pos)
	rule.AddResultant("nuc_bound_%04d"%pos)

	rule.rate = max(positional_nuc_rates[pos][0], 1.e-10)	# min rate of 1 * 10**-10
	rule.Write(outfile)

	# for each position of the linker
	#	if nucleosome bound there, abort this one
	for n in xrange(linkerLeft):
		if (pos-N_GROUP_PER_NUCLEOSOME-n > 0):
			# create rule nuc_binding[pos] + nuc_bound[pos-N_GROUP-n] -> nuc_unbinding[pos] + nuc_bound[pos-N_GROUP-n]
			rule = SSA_Rule("Nucleosome_aborting_LB_%02d_%04d"%(n,pos))
			rule.AddReactant("nuc_binding_%04d"%pos)
			rule.AddReactant("nuc_binding_%04d"%(pos-N_GROUP_PER_NUCLEOSOME-n))
							
			rule.AddResultant("nuc_unbinding_%04d"%pos)
			rule.AddResultant("nuc_binding_%04d"%(pos-N_GROUP_PER_NUCLEOSOME-n))
						
			rule.rate = NUCLEOSOME_ARORT_RATE
			rule.Write(outfile)

			rule = SSA_Rule("Nucleosome_aborting_L_%02d_%04d"%(n,pos))
			rule.AddReactant("nuc_binding_%04d"%pos)
			rule.AddReactant("nuc_stable_%04d"%(pos-N_GROUP_PER_NUCLEOSOME-n))
							
			rule.AddResultant("nuc_unbinding_%04d"%pos)
			rule.AddResultant("nuc_stable_%04d"%(pos-N_GROUP_PER_NUCLEOSOME-n))
						
			rule.rate = NUCLEOSOME_ARORT_RATE
			rule.Write(outfile)

			# create rule nuc_binding[pos] + nuc_bound[pos-N_GROUP-n] -> nuc_unbinding[pos] + nuc_bound[pos-N_GROUP-n]
			rule = SSA_Rule("Nucleosome_aborting_LS_%02d_%04d"%(n,pos))
			rule.AddReactant("nuc_stable_%04d"%pos)
			rule.AddReactant("nuc_stable_%04d"%(pos-N_GROUP_PER_NUCLEOSOME-n))
							
			rule.AddResultant("nuc_unbinding_%04d"%pos)
			rule.AddResultant("nuc_stable_%04d"%(pos-N_GROUP_PER_NUCLEOSOME-n))
						
			rule.rate = NUCLEOSOME_ARORT_RATE
			rule.Write(outfile)

	for n in xrange(linkerRight):
		if (pos+N_GROUP_PER_NUCLEOSOME+n <= N_DNA):
			# create rule nuc_binding[pos] + nuc_bound[pos+N_GROUP+n] -> nuc_unbinding[pos] + nuc_bound[pos+N_GROUP+n]
			rule = SSA_Rule("Nucleosome_aborting_RB_%02d_%04d"%(n,pos))
			rule.AddReactant("nuc_binding_%04d"%pos)
			rule.AddReactant("nuc_binding_%04d"%(pos+N_GROUP_PER_NUCLEOSOME+n))
							
			rule.AddResultant("nuc_unbinding_%04d"%pos)
			rule.AddResultant("nuc_binding_%04d"%(pos+N_GROUP_PER_NUCLEOSOME+n))
						
			rule.rate = NUCLEOSOME_ARORT_RATE
			rule.Write(outfile)

			rule = SSA_Rule("Nucleosome_aborting_R_%02d_%04d"%(n,pos))
			rule.AddReactant("nuc_binding_%04d"%pos)
			rule.AddReactant("nuc_stable_%04d"%(pos+N_GROUP_PER_NUCLEOSOME+n))
							
			rule.AddResultant("nuc_unbinding_%04d"%pos)
			rule.AddResultant("nuc_stable_%04d"%(pos+N_GROUP_PER_NUCLEOSOME+n))
						
			rule.rate = NUCLEOSOME_ARORT_RATE
			rule.Write(outfile)

			# create rule nuc_binding[pos] + nuc_bound[pos+N_GROUP+n] -> nuc_unbinding[pos] + nuc_bound[pos+N_GROUP+n]
			rule = SSA_Rule("Nucleosome_aborting_RS_%02d_%04d"%(n,pos))
			rule.AddReactant("nuc_stable_%04d"%pos)
			rule.AddReactant("nuc_stable_%04d"%(pos+N_GROUP_PER_NUCLEOSOME+n))
							
			rule.AddResultant("nuc_unbinding_%04d"%pos)
			rule.AddResultant("nuc_stable_%04d"%(pos+N_GROUP_PER_NUCLEOSOME+n))
						
			rule.rate = NUCLEOSOME_ARORT_RATE
			rule.Write(outfile)
		
# end  Nucleosome_Binding3()
###############################################################################

def RNAP_INIT(id, i, direction, TF_names, RNAP_ON_RATE, dna, outfile):
	NT_PER_GROUP = params.GetInt(DNA_section,"GROUPING")
	RNAP_N_POS   = (params.GetInt("RNAP","RNAP_SIZE",25) + NT_PER_GROUP - 1)/ NT_PER_GROUP
	if (RNAP_ON_RATE < 0):
		RNAP_ON_RATE    = params.GetFloat("RNAP","ON_RATE",1.0)

#	print "RNAP_INIT([%s],%d,%d,%s,%f,...)"%(id,i,direction,str(TF_names), RNAP_ON_RATE)
	dir = 'w'
	if (direction < 0): dir = 'c'
	
	if (id and (id[-1] != '_')): id += '_'
	
	# RNAP + DNA -> RNAP_INIT
	rule = SSA_Rule("%sRNAP_%c_init_%04d"%(id, dir,i))
	for name in TF_names:
		rule.AddStableReactant(name)
	# need to have enought nt available for RNAP
	for n in xrange(RNAP_N_POS):
		if ((i-(direction*n) > 0) and (i-(direction*n) <= N_DNA)):
			rule.AddReactant("dna_%04d"%(i-(direction*n)))
	rule.AddReactant("rnap")
	rule.AddResultant("rnap_%c_init_0_%04d"%(dir,i))
	rule.AddResultant("rnap_bound_%04d"%i)
	for name in TF_names:
		rule.AddStableResultant(name)
	rule.AddResultant("RNAP_INIT")
	rule.rate = RNAP_ON_RATE  # should be dependent on DNA sequence
	rule.Write(outfile)
	
###################################################################################################
def	Print_Percent_Graph_LOG(counts, title, NT_PER_GROUP, START_POS):
	
	divider = BuildDivider(len(counts), NT_PER_GROUP, START_POS)
	
	max_count = max(counts)
	n_lines = 10
	
	print "Log Scale [%s] max=%d in %d entries"%(title, max_count[0], len(counts))
	print divider
	
	for n in xrange(n_lines):
		limit = (n_lines-n) * n_lines
		line = "%5d:"%limit
		
		for val in counts:
			v = val[0]
			v = 100 - int(math.ceil(-10 * math.log(v,10)))
			if (v >= limit):
				line += "*"
			else:
				line += " "
				
		print line
		
	print divider
# end of Print_Percent_Graph_LOG

###################################################################################################
def BuildDividerLocal(N_DNA):
	line1 = "     :"
	line2 = "     :"
	for dna_pos in xrange(1,N_DNA):
		line2 += "%d"%(dna_pos%10)
		if ((dna_pos%10) == 0):
			line1 += "%10d"%(dna_pos/10)
	divider =  line1
	divider += "\n"
	divider += line2
	return divider

def BuildDivider(N_DNA, NT_PER_GROUP, START_POS):
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

def Read_Common_Names(filename):
	# Create two maps one from common to yeast names, the other yeast to common names.
	file = open(filename, "r")
	yeast_to_common_names = {} 	
	common_to_yeast_names = {} 	

	# read file records
	print "Reading common names:"
	lines = file.readlines()
	print "\tread %d lines"%len(lines)
	
	for line in lines:
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		
		# add to list
		line = line.strip()
	#	print "[%s]"%line
		fields = line.split(",")
		yeast_name  = fields[0]
		common_name = fields[1] 
		
		if (yeast_to_common_names.has_key(yeast_name)):
			yeast_to_common_names[yeast_name].append(common_name)
		else:
			yeast_to_common_names[yeast_name] = [common_name]
			
		if (len(common_name) > 0):
			if (common_to_yeast_names.has_key(common_name)):
				print "Duplicate: [%s][%s]"%(common_name,yeast_name)
			else:
				common_to_yeast_names[common_name] = yeast_name
						
	file.close()
	return 	yeast_to_common_names, common_to_yeast_names

# end of Read_Common_Names

###################################################################################################

def Read_Protein_Counts(filename, verbose=False):
	# Create map from yeast name to count
	file = open(filename, "r")
	yeast_counts = {} 	

	# read file records
	if (verbose):	print "Reading counts:"
	lines = file.readlines()
	if (verbose):	print "\tread %d lines"%len(lines)
	
	outline = ""
	for line in lines:
		if (len(line) < 2): continue
		if (line[0] == '#'): continue
		
		line = line.strip()
		outline += "[%20.20s]"%line
		if (len(outline) > 320):
			if (verbose):	print outline
			outline = ""
			
		# add to list
		fields = line.split(",")
		yeast_name  = fields[0]
		
		try:
			count = int(math.ceil(float(fields[2])))
		except:
			if (fields[2] == "\%"):
				count = 50
			count = 0
		
		if (yeast_counts.has_key(yeast_name)):
			if (verbose):	print "duplicate entry:[%s]"%yeast_name
		yeast_counts[yeast_name] = count
						
	file.close()
	return 	yeast_counts

# end of Read_Protein_Counts

###################################################################################################

def Main():
	global N_DNA
	global NT_PER_GROUP
	global N_GROUP_PER_NUCLEOSOME
	global N_INIT_STAGES
	global RNAP_N_POS 
	global params
	global DNA_section
	global START_POS
	global LOCAL_CONCENTRATION
	
	test_params = False
	test_rules  = False
	test_SSA_RNAP = False
	test_SSA_NUC  = False
	paramfile   = "PARAM.INI"
	outfilename	= "SRB_rules.cmdl"
	outdir		= "Results"
	model		= "SRB_model"
	chromo		= 0
	chr_start	= -1
	chr_end		= -1
	DNA_section = ""
	model_RNAP  = False
	model_NUC   = True
	model_TATA  = False
	try:
		opts, args = getopt.getopt(sys.argv[1:], "o:p:", ["help", "DNA=", "results=", "TEST_RNAP", "TEST_NUC"])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)
	if not opts:
		Usage()
		sys.exit(1)

	motifs = []							 
	for opt, value in opts:
		#print opt, value
		if	 opt == '-p':  			paramfile   = value
		elif opt == '-o':			outfilename = value
		elif opt == '--DNA':		DNA_section = value
		elif opt == '--results':	outdir	    = value
		elif opt == '--TEST_RNAP':	test_SSA_RNAP = True
		elif opt == '--TEST_NUC':	test_SSA_NUC  = True
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	Make_Results_Dir(outdir)
	outfile = open(outdir+'/'+outfilename, 'w',0)

	log_filename = outdir + '/' + "SRB.log"
	log = K.NOX_LogFile(log_filename)
	line = "["
	line += "][".join(sys.argv)
	line += "]"
	log.Display(line)

	log.Display("Rule file:%s/%s"%(outdir,outfilename))
	log.Display("Log file: %s/SRB.log"%outdir)
	
	params = K.NOX_ParamFile(paramfile)
	print "sections:",params.sections
#	params.Dump()	
#	print "String Value for %s,%s = %s"%("REB1","OFF_RATE",params.GetString("REB1","OFF_RATE"))
#	print "Float  Value for %s,%s = %s"%("REB1","OFF_RATE",params.GetFloat("REB1","OFF_RATE"))
	
	if (test_params):
		params.Dump()
		print "Sections:",params.Sections()
	
		key = 'one'
		section = "section1"
		print "String Value for %s,%s = %s"%(section,key,params.GetString(section,key))
		section = "section2"
		print "String Value for %s,%s = %s"%(section,key,params.GetString(section,key))
		print "Int Value for %s,%s = %s"%(section,key,params.GetInt(section,key))
		print "Float Value for %s,%s = %s"%(section,key,params.GetFloat(section,key))
		
		key = 'three'
		print "String Value for %s,%s = %s"%(section,key,params.GetString(section,key))
		print "Int Value for %s,%s = %s"%(section,key,params.GetInt(section,key))
		print "Float Value for %s,%s = %s"%(section,key,params.GetFloat(section,key))
	
		key = 'two'
		print "String Value for %s,%s = %s"%(section,key,params.GetString(section,key))
		print "Int Value for %s,%s = %s"%(section,key,params.GetInt(section,key))
		print "Float Value for %s,%s = %s"%(section,key,params.GetFloat(section,key))

	if (test_rules):	
		###############################################################################
		#
		# Test the SSA Rule class
		#
		###############################################################################	
		rule = SSA_Rule("test")
		
		for i in xrange(1,10):
			rule.AddReactant("DNA[%d]"%i)
		rule.AddReactant("RNAP")
		
		rule.AddResultant("RNAP_INIT[1]")
		rule.rate = .86
		
		rule.Write(sys.stdout)
		
		rule.steps = 8
		rule.Write(sys.stdout)
		
	###############################################################################
	#
	#	Write header to rules file
	# 
	###############################################################################

	if (DNA_section == ""):
		DNA_section = params.GetString("SRB","DNA", "DNA")
	print "processing DNA section [%s]"%DNA_section
		
	outfile.write("//\n// %s\n//\n"%outfilename)
	header = 	"//	\n"\
				"// This document contains a model description of a simple stochastic model of the transcription of \n"\
				"// the %s gene, with transcriptional interference between two oppisite strand transcriptions.	\n"\
				"//	\n"\
				"// The rate constants and initial populations are	\n"\
				"// not taken from any experiments; the purpose of	\n"\
				"// this model is just to explore the effects of	\n"\
				"// stochasticity in comparsion to deterministic 	\n"\
				"// dynamics.	\n"\
				"//	\n"\
				"// The model description is in the CMDL	\n"\
				"// (Chemical Model Definition Language)	\n"\
				"// language, and is meant to be parsed by the	\n"\
				"// \"Dizzy\" software system.  For more information,	\n"\
				"// please refer to the home page for the Dizzy	\n"\
				"// software system.	\n"\
				"//	\n"\
				"// Copyright (2011) University of Colorado	\n"\
				"// All Rights Reserved	\n"\
				"// Author: David Knox	\n"\
				"// Date:    2011/11/09 	\n"\
				"//	\n"\
				"// Variable name rules 	\n"\
				"//	ALL_CAPS - constant values	\n"\
				"//	First_cap  - reaction names	\n"\
				"//	all_lower  - reactant name	\n"\
				"//"%DNA_section

	outfile.write("%s\n"%header)
	outfile.write("#model \"%s\";\n"%model)

	###############################################################################
	#
	# Read molecule counts for each protein
	#
	###############################################################################
	counts_filename = params.GetString("SRB","PROTEIN_COUNTS", "DATA/YeastProteinCounts.txt")
	yeast_counts = Read_Protein_Counts(counts_filename)
	yeast_to_common, common_to_yeast = Read_Common_Names(counts_filename)	
		
	###############################################################################
	#
	# Set concentration of local are being modeled.  All per cell values are adjusted by this value.
	#
	###############################################################################
	LOCAL_CONCENTRATION = params.GetFloat("SRB", "LOCAL_CONCENTRATION", 1.0)
	# check for specific DNA locus override
	LOCAL_CONCENTRATION = params.GetFloat(DNA_section, "LOCAL_CONCENTRATION", LOCAL_CONCENTRATION)
	print "Using local concentration of proteins:", LOCAL_CONCENTRATION
	
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
		chr_start  = params.GetInt(DNA_section,"START",0)
		chr_end    = params.GetInt(DNA_section,"END")
		if (not chr_end):
			chr_end = params.GetInt(DNA_section,"LENGTH",0)
			chr_end += chr_start
		START_POS = chr_start
		
		log.Display("Loading fasta: [%s]"%fastafile)
		seqs = Fasta.load(fastafile)
		seqkeys = seqs.keys()
		seqkeys.sort()
		n = 0
		for chr in seqkeys:
			n += len(seqs[chr])
		log.Display("Genome length = %d, # chromosomes = %d"%(n, len(seqkeys)))
		
		if (seqs.has_key(chromo)):
			seq = seqs[chromo]
			log.Display("Chr[%s] = %d nt"%(chromo,len(seq)))
			dna = seq[chr_start:chr_end]
			log.Display("DNA[%d:%d] = %d nt"%(chr_start,chr_end,len(dna)))
		else:
			log.Display("Cannot find [%s] chromosome in %s"%(chromo, filename))
		log.Display("DNA:[%s]"%dna)
	else:
		log.Display("No sequence given [%s]"%DNA_section, True)
	
	NT_PER_GROUP = params.GetInt(DNA_section,"GROUPING",10)
	N_DNA = (len(dna) + NT_PER_GROUP-1) / NT_PER_GROUP	
	log.Display("N_DNA = %d"%N_DNA)
	
	outfile.write("//\n// %s\n//\n"%"Define DNA")
	log.Display("Initalizing dna[1..%d]"%N_DNA)
	outfile.write("dna_0000 = 0;\n") # dummy position used to force columns into output
	for i in xrange(1,N_DNA+1):
		outfile.write("dna_%04d = 1;\n"%i)
		outfile.write("TF_bound_%04d = 0;\n"%i)	 	# generic TF binding at position

	###############################################################################
	#
	#	Check to see what we are modeling
	# 
	###############################################################################
	
	model_RNAP = params.GetInt("SRB","MODEL_RNAP",model_RNAP)
	model_RNAP = params.GetInt(DNA_section,"MODEL_RNAP",model_RNAP)
	
	model_NUC  = params.GetInt("SRB","MODEL_NUC",model_NUC)
	model_NUC  = params.GetInt(DNA_section,"MODEL_NUC",model_NUC)
	
	model_TATA = params.GetInt("SRB","MODEL_TATA",model_TATA)
	model_TATA = params.GetInt(DNA_section,"MODEL_TATA",model_TATA)
	
	###############################################################################
	#
	#	Create Nucleosome variables
	# 
	###############################################################################
	N_GROUP_PER_NUCLEOSOME = (147 + NT_PER_GROUP-1) / NT_PER_GROUP	

	if (test_SSA_NUC and model_NUC):
		Generate_NUC_Rules(params, outfile, dna)
		
	elif (model_NUC):	
		outfile.write("//\n// %s\n//\n"%"Nucleosomes")
		outfile.write("// nuc_[i]           keep list of locations with Nucleosome bound\n")
		outfile.write("// nuc_binding_[i]   keep list of locations with Nucleosome binding\n")
		outfile.write("// nuc_unbinding_[i] keep list of locations with Nucleosome unbinding\n")
	
		n_histone = params.GetInt("NUCLEOSOME","N_HISTONES",0)
		if (n_histone > 0):
			n_histone = int(n_histone / NT_PER_GROUP * LOCAL_CONCENTRATION)  # adjust concentration relative to number of possible starting locations
			if (n_histone < 1):
				n_histone = 1	# if there are suppose to be items available, make one available
				
		outfile.write("histones           = %d;  \n"%n_histone)
		outfile.write("NUC_BINDING        = 0;   // Count number of binding events \n")
		outfile.write("NUC_UNBINDING      = 0;   // Count number of unbinding events \n")

		outfile.write("NUC_SIZE           = %d;  \n"%N_GROUP_PER_NUCLEOSOME)
		# dummy rule to force SIZE col in output
		rule = SSA_Rule("%s_size_output"%("NUC_size_output"))
		rule.AddStableReactant("NUC_SIZE")
		rule.AddReactant("dna_%04d"%0)
		rule.AddResultant("dna_%04d"%0)
		rule.rate = 0.00000000001
		rule.Write(outfile)

		for i in xrange(1,N_DNA+1):
			outfile.write("nuc_bound_%04d     = 0;  \n"%i)
			outfile.write("nuc_binding_%04d   = 0;  \n"%i)
			outfile.write("nuc_stable_%04d    = 0;  \n"%i)
			outfile.write("nuc_unbinding_%04d = 0;  \n"%i)
			
		###############################################################################
		#
		#	Rules for nucleosome formation and breakup
		# 
		###############################################################################
		outfile.write("//\n// %s\n//\n"%"Nucleosome Rules")
		NUCLEOSOME_ON_RATE  = params.GetFloat("NUCLEOSOME","ON_RATE", 1.0)
		NUCLEOSOME_OFF_RATE = params.GetFloat("NUCLEOSOME","OFF_RATE",1.0)
		linker_nt           = params.GetInt("NUCLEOSOME","MIN_LINKER_SIZE",30)
	
		# Get the position dependent OFF rates based on DNA sequence
		prob_file = params.GetString("NUCLEOSOME","NUC_PROB_FILE")
		prob_file = params.GetString(DNA_section,"NUC_PROB_FILE",prob_file)		# override filename

		di_nt_prob_file = params.GetString("NUCLEOSOME","DI_NT_NUC_PROB_FILE")
		di_nt_prob_file = params.GetString(DNA_section,"DI_NT_NUC_PROB_FILE",di_nt_prob_file)		# override filename

		if (di_nt_prob_file):
			positional_nuc_rates, pos_prob = K.Calc_WASSON_Nucleosome_Rates(di_nt_prob_file, dna, NT_PER_GROUP, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE)
		elif (prob_file): #old SEGAL positional prob
			positional_nuc_rates = Calc_Nucleosome_Rates_From_File(prob_file, chromo, chr_start, chr_end, dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE, NT_PER_GROUP, START_POS)
		else:
			positional_nuc_rates = Calc_Nucleosome_Rates(dna, NUCLEOSOME_ON_RATE, NUCLEOSOME_OFF_RATE)
	
		linker_size = (linker_nt + NT_PER_GROUP-1) / NT_PER_GROUP
		#bits = int(math.pow(2,linker_size))
		print "Nucleosome N_GROUPS=%d, Linker=%d, +/- %d positions, %d extra rules per position"%(N_GROUP_PER_NUCLEOSOME, linker_nt, linker_size, linker_size*2)
		for i in xrange(1,N_DNA+1):
		#	Nucleosome_Binding(params, positional_nuc_rates, i, False, False, outfile)
		#	Nucleosome_Binding(params, positional_nuc_rates, i, True,  False, outfile)
		#	Nucleosome_Binding(params, positional_nuc_rates, i, False, True,  outfile)
		#	Nucleosome_Binding(params, positional_nuc_rates, i, True,  True,  outfile)
		##	for left in xrange(bits):
		##		for right in xrange(bits):
		##			Nucleosome_Binding2(params, positional_nuc_rates, i, linker_size, left,  linker_size, right,  outfile)
			Nucleosome_Binding3(params, positional_nuc_rates, i, linker_size, linker_size, outfile)
			
		for i in xrange(1,N_DNA+1):
			rule = SSA_Rule("Nucleosome_bound_%04d"%i)
			rule.AddReactant("nuc_binding_%04d"%i)		
			rule.AddResultant("nuc_stable_%04d"%i)
			rule.rate = 1. #10.0
			rule.steps = params.GetInt("NUCLEOSOME","ON_DELAY",0)
			rule.Write(outfile)
			
		for i in xrange(1,N_DNA+1):
			rule = SSA_Rule("Nucleosome_unbinding_%04d"%i)
			rule.AddReactant("nuc_stable_%04d"%i)		
			rule.AddResultant("nuc_unbinding_%04d"%i)
			rule.rate = max(0.09, positional_nuc_rates[i][1])
			rule.steps = params.GetInt("NUCLEOSOME","OFF_DELAY",0)
			rule.Write(outfile)
			
		for i in xrange(1,N_DNA+1):
			rule = SSA_Rule("Nucleosome_unbound_%04d"%i)
			rule.AddReactant("nuc_unbinding_%04d"%i)
			rule.AddReactant("nuc_bound_%04d"%i)
			rule.AddStableResultant("histones")
			for n in xrange(N_GROUP_PER_NUCLEOSOME):
				if (i+n <= N_DNA):
					rule.AddResultant("dna_%04d"%(i+n))
			rule.AddResultant("NUC_UNBINDING")
			rule.rate = 100.0 # 10.
			rule.Write(outfile)

	###############################################################################
	#
	#	RNAP
	# 
	###############################################################################
	outfile.write("//\n// %s\n//\n"%"----------START of RNAP Section---------")
	
	if (test_SSA_RNAP and model_RNAP):
	#	Generate_RNAP_Rules(params, outfile)
		Generate_Specific_RNAP_Rules(params, outfile)
		
	elif (model_RNAP):	
		outfile.write("//\n// %s\n//\n"%"RNAP")
	
		RNAP_ON_RATE    = params.GetFloat("RNAP","ON_RATE",1.0)
		RNAP_OFF_RATE   = params.GetFloat("RNAP","OFF_RATE",1.0)
		RNAP_TRANS_RATE = params.GetFloat("RNAP","TRANSCRIPTION_RATE",10.0)
		RNAP_INIT_RATE  = params.GetFloat("RNAP","INIT_RATE",1.0)
		RNAP_ABORT_RATE = params.GetFloat("RNAP","INIT_ABORT",1.0)
	
		N_INIT_STAGES   = params.GetInt("RNAP","N_INIT_STAGES",1)
		RNAP_N_POS      = (params.GetInt("RNAP","RNAP_SIZE",25) + NT_PER_GROUP - 1)/ NT_PER_GROUP
		
		rnap_count = params.GetInt("RNAP","INITIAL_COUNT",0)
		outfile.write("rnap              = %d;  \n"%rnap_count)
		outfile.write("TI_COLLISION      = 0;  \n")
		outfile.write("TI_COLLISION_SD   = 0;  \n")
		outfile.write("RNAP_INIT         = 0;  \n")
		outfile.write("RNAP_ELONGATED    = 0;  \n")
		outfile.write("RNAP_ABORTED      = 0;  \n")
		outfile.write("RNAP_COMPLETED_W  = 0;  \n")
		outfile.write("RNAP_COMPLETED_C  = 0;  \n")
	
		for i in xrange(1,N_DNA+1):
			outfile.write("rnap_bound_%04d      = 0;\n"%i)	# generic RNAP binding at position
			outfile.write("rnap_abort_w_%04d    = 0;\n"%i)
			outfile.write("rnap_abort_c_%04d    = 0;\n"%i)
			for n in xrange(N_INIT_STAGES):
				outfile.write("rnap_w_init_%d_%04d  = 0;\n"%(n,i))
			outfile.write("rnap_w_%04d          = 0;\n"%i)
			outfile.write("rnap_w_scribed_%04d  = 0;\n"%i)	
			for n in xrange(N_INIT_STAGES):
				outfile.write("rnap_c_init_%d_%04d  = 0;\n"%(n,i))
			outfile.write("rnap_c_%04d  = 0;\n"%i)
			outfile.write("rnap_c_scribed_%04d  = 0;\n"%i)	
			outfile.write("RNAP_STARTED_W_%04d  = 0;\n"%i)
			outfile.write("RNAP_STARTED_C_%04d  = 0;\n"%i)
			
		###############################################################################
		# TATA Binding Protein required to complete PIC
		###############################################################################
		if (model_TATA):
			outfile.write("//\n// %s\n//\n"%"TATA Regions")
			name = "TATA"
			motif_str  = params.GetString(name,"MOTIF","TATAWA")
			motif = New_Motif(motif_str)
			thresh  = params.GetFloat(name,"MOTIF_THRESH", 0.4)
			matches = Find_Motif_Matches(dna, motif, thresh)
			count  = params.GetInt(name,"INITIAL_COUNT",5)
			print "calling Define_TATA: N_DNA =", N_DNA
			Define_TATA(name, count, matches, dna, outfile)		
			outfile.write("TATA_STABLE  = 0;\n")

		###############################################################################
		# RNAP Rules
		###############################################################################
		if (rnap_count > 0):
			outfile.write("//\n// %s\n//\n"%"RNAP Rules")
			for i in xrange(1,N_DNA+1):
				RNAP_INIT("", i, 1, [], -1, dna, outfile)
	
				# RNAP_W_INIT -> RNAP_ABORT
				rule = SSA_Rule("RNAP_W_abort_init_%04d"%i)
				rule.AddReactant("rnap_w_init_0_%04d"%i)
				rule.AddResultant("rnap_abort_w_%04d"%i)
				rule.rate  = RNAP_ABORT_RATE
				rule.Write(outfile)
	
				if (model_TATA):
					# Keep TATA from unbinding during init
					rule = SSA_Rule("TATA_RNAP_W_STABLE_%d_%04d"%(0,i))
					rule.AddReactant("rnap_w_init_%d_%04d"%(0,i))
					rule.AddReactant("TF_TATA_bound_%04d"%(i-RNAP_N_POS))
					rule.AddResultant("rnap_w_init_%d_%04d"%(0,i))
					rule.AddResultant("TF_TATA_bound_%04d"%(i-RNAP_N_POS))
					rule.AddResultant("TATA_STABLE")
					rule.rate  = 10.0
					if (i > RNAP_N_POS):
						rule.Write(outfile)
		
				# RNAP_INIT_0 -> RNAP_INIT_1 -> ... -> RNAP_INIT_N -> RNAP_W
				for n in xrange(1,N_INIT_STAGES):
					rule = SSA_Rule("RNAP_W_init_%d_%04d"%(n,i))
					rule.AddReactant("rnap_w_init_%d_%04d"%(n-1,i))
					rule.AddResultant("rnap_w_init_%d_%04d"%(n,i))
					rule.rate  = RNAP_INIT_RATE
				#	rule.steps = 2
					rule.Write(outfile)
	
					# RNAP_W -> RNAP_ABORT
					rule = SSA_Rule("RNAP_W_abort_init_%d_%04d"%(n,i))
					rule.AddReactant("rnap_w_init_%d_%04d"%(n,i))
					rule.AddResultant("rnap_abort_w_%04d"%i)
					rule.rate  = RNAP_ABORT_RATE * ((1.0 * N_INIT_STAGES-n) / N_INIT_STAGES)  # less likely at each stage to abort
					rule.Write(outfile)
	
					if (model_TATA):
						# Keep TATA from unbinding during init
						rule = SSA_Rule("TATA_RNAP_W_STABLE_%d_%04d"%(n,i))
						rule.AddReactant("rnap_w_init_%d_%04d"%(n,i))
						rule.AddReactant("TF_TATA_bound_%04d"%(i-RNAP_N_POS))
						rule.AddResultant("rnap_w_init_%d_%04d"%(n,i))
						rule.AddResultant("TF_TATA_bound_%04d"%(i-RNAP_N_POS))
						rule.AddResultant("TATA_STABLE")
						rule.rate  = 10.0
						if (i > RNAP_N_POS):
							rule.Write(outfile)
	
				# Final state change to RNAP_W 
				rule = SSA_Rule("RNAP_W_bound_%04d"%i)
				rule.AddReactant("rnap_w_init_%d_%04d"%(N_INIT_STAGES-1,i))
				if (model_TATA):
					rule.AddReactant("TF_TATA_bound_%04d"%(i-RNAP_N_POS))
				rule.AddResultant("rnap_w_%04d"%i)
				rule.AddResultant("RNAP_STARTED_W_%04d"%i)
				rule.AddResultant("RNAP_ELONGATED")
				if (model_TATA):
					rule.AddResultant("TF_TATA_bound_%04d"%(i-RNAP_N_POS))
				rule.rate  = RNAP_INIT_RATE
				if (i > RNAP_N_POS):
					rule.Write(outfile)
			
				# RNAP_W -> RNAP_ABORT
				rule = SSA_Rule("RNAP_W_abort_%04d"%i)
				rule.AddReactant("rnap_w_%04d"%i)
				rule.AddResultant("rnap_abort_w_%04d"%i)
				rule.rate  = RNAP_OFF_RATE
				rule.Write(outfile)
	
				# RNAP_W -> RNAP_W_TRANSCRIBED
				rule = SSA_Rule("RNAP_W_transcribed_%04d"%i)
				rule.AddReactant("rnap_w_%04d"%i)
				rule.AddResultant("rnap_w_scribed_%04d"%i)
				rule.rate  = 1.0
				rule.steps = NT_PER_GROUP / RNAP_TRANS_RATE	# transcription rate
				rule.Write(outfile)
	
				# RNAP_W_TRANSCRIBED[i] + DNA[i+1] -> DNA[i] + RNAP_W[i+1]
				rule = SSA_Rule("RNAP_W_move_%04d"%i)
				rule.AddReactant("rnap_bound_%04d"%i)
				rule.AddReactant("rnap_w_scribed_%04d"%i)
				rule.AddReactant("dna_%04d"%(i+1))
				rule.AddResultant("rnap_bound_%04d"%(i+1))
				rule.AddResultant("rnap_w_%04d"%(i+1))
				if ((i-RNAP_N_POS+1) > 0):
					rule.AddResultant("dna_%04d"%(i-RNAP_N_POS+1))
				rule.rate  = 1.0
				if (i < N_DNA):
					rule.Write(outfile)
	
				# RNAP_ABORT -> RNAP + DNA
				rule = SSA_Rule("RNAP_abort_w_%04d"%i)
				rule.AddReactant("rnap_abort_w_%04d"%i)
				rule.AddReactant("rnap_bound_%04d"%i)
				rule.AddResultant("rnap")
				for n in xrange(RNAP_N_POS):
					if (i-n > 0):
						rule.AddResultant("dna_%04d"%(i-n))
				rule.AddResultant("RNAP_ABORTED")
				rule.rate  = .5  # let it sit there a bit
				rule.Write(outfile)
			
				# Force the removal of nucleosome ahead of RNAP_W		
				rule = SSA_Rule("Nucleosome_RNAP_W_%04d"%i)
				rule.AddReactant("rnap_w_scribed_%04d"%i)
				rule.AddReactant("nuc_stable_%04d"%(i+RNAP_N_POS))		
				rule.AddResultant("rnap_w_scribed_%04d"%i)
				rule.AddResultant("nuc_unbinding_%04d"%(i+RNAP_N_POS))
				rule.rate = 10000
				if ((i+RNAP_N_POS) <= N_DNA):
					rule.Write(outfile)
	
				#
				# define rules for Crick strand
				#
	
				# RNAP + DNA -> RNAP_INIT
				RNAP_INIT("", i, -1, [], -1, dna, outfile)
	
				# RNAP_INIT -> RNAP_ABORT
				rule = SSA_Rule("RNAP_C_abort_init_0_%04d"%i)
				rule.AddReactant("rnap_c_init_0_%04d"%i)
				rule.AddResultant("rnap_abort_c_%04d"%i)
				rule.rate  = RNAP_ABORT_RATE
				rule.Write(outfile)
	
				if (model_TATA):
					# Keep TATA from unbinding during init
					rule = SSA_Rule("TATA_RNAP_C_STABLE_%d_%04d"%(0,i))
					rule.AddReactant("rnap_c_init_%d_%04d"%(0,i))
					rule.AddReactant("TF_TATA_bound_%04d"%(i+RNAP_N_POS))
					rule.AddResultant("rnap_c_init_%d_%04d"%(0,i))
					rule.AddResultant("TF_TATA_bound_%04d"%(i+RNAP_N_POS))
					rule.AddResultant("TATA_STABLE")
					rule.rate  = 10.0
					if (i <= N_DNA-RNAP_N_POS):
						rule.Write(outfile)
	
				# RNAP_INIT_0 -> RNAP_INIT_1 -> ... -> RNAP_INIT_N -> RNAP_C
				for n in xrange(1,N_INIT_STAGES):
					rule = SSA_Rule("RNAP_C_init_%d_%04d"%(n,i))
					rule.AddReactant("rnap_c_init_%d_%04d"%(n-1,i))
					rule.AddResultant("rnap_c_init_%d_%04d"%(n,i))
					rule.rate  = RNAP_INIT_RATE
				#	rule.steps = 2
					rule.Write(outfile)
	
					# RNAP_W -> RNAP + DNA
					rule = SSA_Rule("RNAP_C_abort_init_%d_%04d"%(n,i))
					rule.AddReactant("rnap_c_init_%d_%04d"%(n,i))
					rule.AddResultant("rnap_abort_c_%04d"%i)
					rule.rate  = RNAP_ABORT_RATE * ((1.0 * N_INIT_STAGES-n) / N_INIT_STAGES)  # less likely at each stage to abort
					rule.Write(outfile)
				
					if (model_TATA):
						# Keep TATA from unbinding during init
						rule = SSA_Rule("TATA_RNAP_C_STABLE_%d_%04d"%(n,i))
						rule.AddReactant("rnap_c_init_%d_%04d"%(n,i))
						rule.AddReactant("TF_TATA_bound_%04d"%(i+RNAP_N_POS))
						rule.AddResultant("rnap_c_init_%d_%04d"%(n,i))
						rule.AddResultant("TF_TATA_bound_%04d"%(i+RNAP_N_POS))
						rule.AddResultant("TATA_STABLE")
						rule.rate  = 10.0
						if (i <= N_DNA-RNAP_N_POS):
							rule.Write(outfile)
				
			
				# Final state change to RNAP_C 
				rule = SSA_Rule("RNAP_C_bound_%04d"%i)
				rule.AddReactant("rnap_c_init_%d_%04d"%(N_INIT_STAGES-1,i))
				if (model_TATA): 
					rule.AddReactant("TF_TATA_bound_%04d"%(i+RNAP_N_POS))
				rule.AddResultant("rnap_c_%04d"%i)
				rule.AddResultant("RNAP_STARTED_C_%04d"%i)
				rule.AddResultant("RNAP_ELONGATED")
				if (model_TATA):
					rule.AddResultant("TF_TATA_bound_%04d"%(i+RNAP_N_POS))
				rule.rate  = RNAP_INIT_RATE
				if (i <= N_DNA-RNAP_N_POS):
					rule.Write(outfile)
			
				# RNAP_C -> RNAP_ABORT
				rule = SSA_Rule("RNAP_C_abort_%04d"%i)
				rule.AddReactant("rnap_c_%04d"%i)
				rule.AddResultant("rnap_abort_c_%04d"%i)
				rule.rate  = RNAP_OFF_RATE
				rule.Write(outfile)
	
				# RNAP_C -> RNAP_C_TRANSCRIBED
				rule = SSA_Rule("RNAP_C_transcribed_%04d"%i)
				rule.AddReactant("rnap_c_%04d"%i)
				rule.AddResultant("rnap_c_scribed_%04d"%i)
				rule.rate  = 1.0
				rule.steps = NT_PER_GROUP / RNAP_TRANS_RATE	# transcription rate
				rule.Write(outfile)
	
				# RNAP_C_TRANSCRIBED[i] + DNA[i-1] -> DNA[i] + RNAP_C[i-1]
				rule = SSA_Rule("RNAP_C_move_%04d"%i)
				rule.AddReactant("rnap_bound_%04d"%i)
				rule.AddReactant("rnap_c_scribed_%04d"%i)
				rule.AddReactant("dna_%04d"%(i-1))
				rule.AddResultant("rnap_bound_%04d"%(i-1))
				rule.AddResultant("rnap_c_%04d"%(i-1))
				if ((i+RNAP_N_POS-1) <= N_DNA):
					rule.AddResultant("dna_%04d"%(i+RNAP_N_POS-1))
				rule.rate  = 1.0
				if (i > 1):
					rule.Write(outfile)
			
				# RNAP_ABORT -> RNAP + DNA
				rule = SSA_Rule("RNAP_abort_c_%04d"%i)
				rule.AddReactant("rnap_abort_c_%04d"%i)
				rule.AddReactant("rnap_bound_%04d"%i)
				rule.AddResultant("rnap")
				for n in xrange(RNAP_N_POS):
					if (i+n <= N_DNA):
						rule.AddResultant("dna_%04d"%(i+n))
				rule.AddResultant("RNAP_ABORTED")
				rule.rate  = .5  # let it sit there a bit
				rule.Write(outfile)
	
			# RNAP_W -> RNAP + DNA  # Force termination at end of DNA region
			start = max(N_DNA-10, 1) 
			for i in xrange (start, N_DNA+1):
				rule = SSA_Rule("RNAP_W_FORCE_TERM_%04d"%i)
				rule.AddReactant("rnap_w_scribed_%04d"%i)
				rule.AddReactant("rnap_bound_%04d"%i)
				rule.AddResultant("rnap")
				for n in xrange(RNAP_N_POS):
					if (i-n > 0):
						rule.AddResultant("dna_%04d"%(i-n))
				rule.AddResultant("RNAP_COMPLETED_W")
				rule.rate  = 1.0
				rule.Write(outfile)
	
			# RNAP_C -> RNAP + DNA  # Force termination at end of DNA region
			end = min(N_DNA, 10)
			for i in xrange (1, end+1):
				rule = SSA_Rule("RNAP_C_FORCE_TERM_%04d"%i)
				rule.AddReactant("rnap_c_scribed_%04d"%i)
				rule.AddReactant("rnap_bound_%04d"%i)
				rule.AddResultant("rnap")
				for n in xrange(RNAP_N_POS):
					if (i+n <= N_DNA):
						rule.AddResultant("dna_%04d"%(i+n))
				rule.AddResultant("RNAP_COMPLETED_C")
				rule.rate  = 1.0
				rule.Write(outfile)
	
			for i in xrange(1,N_DNA-1):
				# RNAP_W[i] + RNAP_C[i+1] -> RNAP + DNA + RNAP + DNA
				rule = SSA_Rule("RNAP_collision_%04d"%i)
				rule.AddReactant("rnap_w_scribed_%04d"%i)
				rule.AddReactant("rnap_c_scribed_%04d"%(i+1))
				rule.AddResultant("rnap_abort_w_%04d"%i)	
				rule.AddResultant("rnap_abort_c_%04d"%(i+1))
				rule.AddResultant("TI_COLLISION")
				rule.rate = 1.0
				rule.Write(outfile)
	
				# Sitting Duck RNAP_W collides with RNAP_W_init_[0,1,...]
				for n in xrange(N_INIT_STAGES):
					rule = SSA_Rule("RNAP_W_sd_w_%d_%04d"%(n,i))
					rule.AddReactant("rnap_w_scribed_%04d"%i)
					rule.AddReactant("rnap_w_init_%d_%04d"%(n,i+RNAP_N_POS))
					rule.AddResultant("rnap_w_scribed_%04d"%i)
					rule.AddResultant("rnap_abort_w_%04d"%(i+RNAP_N_POS))
					rule.AddResultant("TI_COLLISION_SD")
					rule.rate = 1.0
					if (i < N_DNA-RNAP_N_POS):
						rule.Write(outfile)
	
				# Sitting Duck  RNAP_W collides with RNAP_C_init_[0,1,...]
				for n in xrange(N_INIT_STAGES):
					rule = SSA_Rule("RNAP_W_sd_c_%d_%04d"%(n,i))
					rule.AddReactant("rnap_w_scribed_%04d"%i)
					rule.AddReactant("rnap_c_init_%d_%04d"%(n,i+1))
					rule.AddResultant("rnap_w_scribed_%04d"%i)
					rule.AddResultant("rnap_abort_c_%04d"%(i+1))
					rule.AddResultant("TI_COLLISION_SD")
					rule.rate = 1.0
					if (i < N_DNA):
						rule.Write(outfile)
	
				# Sitting Duck RNAP_C collides with RNAP_C_init_[0,1,...]
				for n in xrange(N_INIT_STAGES):
					rule = SSA_Rule("RNAP_C_sd_c_%d_%04d"%(n,i))
					rule.AddReactant("rnap_c_scribed_%04d"%i)
					rule.AddReactant("rnap_c_init_%d_%04d"%(n,i-RNAP_N_POS))
					rule.AddResultant("rnap_c_scribed_%04d"%i)
					rule.AddResultant("rnap_abort_c_%04d"%(i-RNAP_N_POS))
					rule.AddResultant("TI_COLLISION_SD")
					rule.rate = 1.0
					if (i > RNAP_N_POS):
						rule.Write(outfile)
	
				# Sitting Duck RNAP_C collides with RNAP_W_init_[0,1,...]
				for n in xrange(N_INIT_STAGES):
					rule = SSA_Rule("RNAP_C_sd_w_%d_%04d"%(n,i))
					rule.AddReactant("rnap_c_scribed_%04d"%i)
					rule.AddReactant("rnap_w_init_%d_%04d"%(n,i-1))
					rule.AddResultant("rnap_c_scribed_%04d"%i)
					rule.AddResultant("rnap_abort_w_%04d"%(i-1))
					rule.AddResultant("TI_COLLISION_SD")
					rule.rate = 1.0
					if (i > RNAP_N_POS):
						rule.Write(outfile)
	
				# Force the removal of nucleosome ahead of RNAP_C		
				rule = SSA_Rule("Nucleosome_RNAP_C_%04d"%i)
				rule.AddReactant("rnap_c_scribed_%04d"%i)
				rule.AddReactant("nuc_stable_%04d"%(i-N_GROUP_PER_NUCLEOSOME))		
				rule.AddResultant("rnap_c_scribed_%04d"%i)
				rule.AddResultant("nuc_unbinding_%04d"%(i-N_GROUP_PER_NUCLEOSOME))
				rule.rate = 10000
				if ((i-N_GROUP_PER_NUCLEOSOME) > 0):
					rule.Write(outfile)
		#end if rnap_count > 0
	# end if MODEL_RNAP
	outfile.write("//\n// %s\n//\n"%"----------END of RNAP Section---------")
					
	###############################################################################
	#
	#	Load Motifs from TAMO file
	# 
	###############################################################################
	motiffile = params.GetString("SRB","MOTIF_FILE")
	motiffile = params.GetString(DNA_section,"MOTIF_FILE", motiffile)
	motifs = None
	motif_names = None
	motif_thresh = params.GetFloat("SRB","MOTIF_THRESH", 0.7)
	motif_list = params.GetString("SRB","TF_LIST",None)
	motif_list = params.GetString(DNA_section,"TF_LIST",motif_list)

	log.Display("Motif threshhold: %f"%motif_thresh)
	
	if (motif_list):
		log.Display("# Using selected motifs: [%s]"%motif_list)
		motif_names = []
		names = motif_list.split(',')
		for name in names:
			name = name.strip()
			motif_names.append(name)
			
	if motiffile:
		log.Display("# Reading motifs from: [%s]"%motiffile)
		motifs = MotifTools.load(motiffile)
		if (not motif_names):
			motif_names = []
			for m in motifs:
				motif_names.append(m.source)
	
	if (motif_names):
		motif_names.sort()
		log.Display("Motifs:")
		for name in motif_names:
			log.Display("\t%s"%name)

	active_TF = []
	
	if (motifs):
		outfile.write("//\n// %s\n//\n"%"Transcription Factors")
		
		names_to_process = motif_names
		motif_names = []
 		for name in names_to_process:
 			# find the initial molecule count
			count = 1
			yeast_name = name
			if (common_to_yeast.has_key(name)):
				yeast_name = common_to_yeast[name]
			if (yeast_counts.has_key(yeast_name)):
				count = yeast_counts[yeast_name]
				if (count > 0):
					count = max(1,count)  # max(1,count/500)
				print "******** protein experimental count=%d for [%s][%s]"%(count, name, yeast_name)
				
			count  = params.GetInt(name,"INITIAL_COUNT",count)
			count  = count * LOCAL_CONCENTRATION
			print "******** using count=%d for [%s][%s]"%(count, name, yeast_name)
			
			if (count <= 0): continue
 		
 			# if pwm file specified, read it
 			# otherwise use TAMO yeast motifs
 			motiffile = params.GetString(name,"MOTIF_PWM", None)
 			if (motiffile): 			
				motif = Make_PWM_Motif(motiffile, name)
 			else:
				motif = Get_Motif(motifs, name)
			if (not motif): 
				motif_names.append(name)
				continue
			
			thresh = params.GetFloat(name,"MOTIF_THRESH", motif_thresh)
			if (thresh != motif_thresh):
				log.Display("\tLocal Motif threshhold: %f"%motif_thresh)
		 	
			matches = Find_Motif_Matches(dna, motif, thresh)
			if (not matches): continue
			
			if (len(matches) > 0):
				active_TF.append(name)
			else:
				continue
				
 			Define_TF(name, count, matches, dna, outfile, model_RNAP)

	if (motif_names):
		print "Processing motifs:",motif_names
		outfile.write("//\n// %s\n//\n"%"Transcription Factors")
		
 		for name in motif_names:
 			# find the initial molecule count
			count = 1
			yeast_name = name
			if (common_to_yeast.has_key(name)):
				yeast_name = common_to_yeast[name]
			if (yeast_counts.has_key(yeast_name)):
				count = yeast_counts[yeast_name]
				if (count > 0):
					count = max(1,count/500)
				print "******** protein count=%d for [%s][%s]"%(count, name, yeast_name)
				
			count  = params.GetInt(name,"INITIAL_COUNT",count)
			count  = count * LOCAL_CONCENTRATION
			print "******** using count=%d for [%s][%s]"%(count, name, yeast_name)
			
			if (count <= 0): continue

 			# if pwm file specified, read it
 			# otherwise use TAMO yeast motifs
 			motiffile = params.GetString(name,"MOTIF_PWM", None)
 			if (motiffile): 			
				motif = Make_PWM_Motif(motiffile, name)
 			else:
				motif = Get_Motif(motifs, name)
			if (motif): 			
				thresh = params.GetFloat(name,"MOTIF_THRESH", motif_thresh)
				if (thresh != motif_thresh):
					log.Display("\tLocal Motif threshhold: %f"%motif_thresh)
	
				matches = Find_Motif_Matches(dna, motif, thresh)
				if (not matches): continue
			
				if (len(matches) > 0):
					active_TF.append(name)
				else:
					continue
				
				Define_TF(name, count, matches, dna, outfile, model_RNAP)
			else:
				# unknown motif
				motif_seq = params.GetString(name, "MOTIF")
				if (motif_seq):
					thresh = params.GetFloat(name,"MOTIF_THRESH", motif_thresh)
					if (thresh != motif_thresh):
						log.Display("\tLocal Motif threshhold: %f"%motif_thresh)
					outfile.write("//\n// %s Regions\n//\n"%name)
					Define_TF_From_INI(name, dna, thresh, outfile, model_RNAP)
					active_TF.append(name)				
 			
	if ("GAL4x" in motif_names):
		GAL4_pwm = [
					[0.01379,0.42295,0.01401,0.54925],
					[0.00441,0.98239,0.00414,0.00907],
					[0.00429,0.01594,0.97461,0.00515],
					[0.00796,0.00293,0.97852,0.01059],
					[0.20601,0.11372,0.63746,0.04282],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.25,0.25,0.25,0.25],
					[0.01059,0.97852,0.00293,0.00796],
					[0.00515,0.97461,0.01594,0.00429],
					[0.00907,0.00414,0.98239,0.00441],
					[0.54925,0.01401,0.42295,0.01379]
					]	
		m = MotifTools.toDict(GAL4_pwm)
		motif = MotifTools.Motif_from_counts(m)
		motif.source = "GAL4"
		
		print "Motif:", motif.source
		print "Max Motif Score:", motif.maxscore
		print "Motif Summary:", motif.summary()
		matches = Find_Motif_Matches(dna, motif, motif_thresh)
		for m in matches:
			m[1] *= 10
	#	print "Matches:", matches
		
		outfile.write("//\n// %s\n//\n"%"GAL4 Regions")
		count  = params.GetInt("GAL4","INITIAL_COUNT",5)
		count  = count * LOCAL_CONCENTRATION
 		Define_TF(name, count, matches, dna, outfile, model_RNAP)
 		active_TF.append("GAL4")		
			
	if ("GALx" in motif_names):
		# Define the GAL4 Dimer 
		thresh = params.GetFloat("GALx","MOTIF_THRESH", motif_thresh)
		outfile.write("//\n// %s\n//\n"%"GALx Regions")
		Define_TF_From_INI("GALx", dna, motif_thresh, outfile, model_RNAP)
		active_TF.append("GALx")

	if ("FKH2_MCM1" in motif_names):
		# Define the A1/Alpha2 Dimer inhibitor
		thresh = params.GetFloat("FKH2_MCM1","MOTIF_THRESH", thresh)
		outfile.write("//\n// %s\n//\n"%"FKH2_MCM1 Regions")
		Define_TF_From_INI("FKH2_MCM1", dna, thresh, outfile, model_RNAP)
		active_TF.append("FKH2_MCM1")

	if ("A1_ALPHA2" in motif_names):
		# Define the A1/Alpha2 Dimer inhibitor
		thresh = params.GetFloat("A1_ALPHA2","MOTIF_THRESH", 0.7)
		outfile.write("//\n// %s\n//\n"%"A1/Alpha2 Regions")
		Define_TF_From_INI("A1_ALPHA2", dna, thresh, outfile, model_RNAP)
		active_TF.append("A1_ALPHA2")

# 	if ("RSC3" in motif_names):
# 		# Define the RSC3 TF
# 		thresh = params.GetFloat("RSC3","MOTIF_THRESH", motif_thresh)
# 		if (thresh != motif_thresh):
# 			log.Display("\tLocal Motif threshhold: %f"%motif_thresh)
# 		outfile.write("//\n// %s\n//\n"%"RSC3 Regions")
# 		Define_TF_From_INI("RSC3", dna, thresh, outfile, model_RNAP)
# 		active_TF.append("RSC3")
		
	if ("POLY_A_T" in motif_names):
		# Define the Poly_A_T nucleosome inhibitor
		outfile.write("//\n// %s\n//\n"%"Poly_A_T Regions")
		Define_TF_From_INI("POLY_A_T", dna, .99, outfile, model_RNAP)
		
	if ("TERM" in motif_names):
		# Define the STOP sites
		outfile.write("//\n// %s\n//\n"%"Termination Regions")
		Define_TF_From_INI("TERM", dna, .99, outfile, model_RNAP)
	
	outfile.write("//\n// %s\n//\n"%"Active Transcription Factors")
	for tf in active_TF:
		outfile.write("//       %s\n"%tf)
		
	# write out some code to insert in PlotModelResults.py
	names = ""
	count = 0
	for tf in active_TF:
		if (len(names) > 0):
			names += ','
		names += '"'
		names += tf
		names += '"'
		count += 1
		if (count % 10 == 0):
			names += "\n\t "
			count = 0
			
	print "tf =\t[", names, "\t]"

		
	###############################################################################
	#
	#	Cleanup before exiting
	# 
	###############################################################################
		
	if (outfile):	
		outfile.close()


###################################################################################################

def Write_Rule_Set(rules, outfile):
	for rule in rules:
		#print rule.name
		rule.Write(outfile)
	return
	
###################################################################################################

def Generate_Specific_RNAP_Rules(params, outfile):

	print "Processing via Generate_Specific_RNAP_Rules()"
	
	TATA_SIZE = N_DNA_POS(8)

	# (we allow either random initiation or more restrictive initiation at given locations)
	# get list of positions from params or specified file
	# for each position in the list
	# 		generate binding at that position (direction)
	#		activation
	#
	# Create rules for the following transition sets:
	#		ABORT
	#		EVICT
	#		TRANSCRIBE
	#		MOVE
	#		INTERFERENCE
	#		EVICT_NUCLEOSOME
	#		
	
	## Get pos list or position file from param file
	## if no positions specified
	## 		use whole DNA range 
	pos_list = []
	position_filename = params.GetString("RNAP","POSITION_FILE")
	specific_pos = params.GetString("RNAP","POSITIONS")
	if (position_filename):
		# load the positions from a file (Only handling GFF3 or BED formats)
		# Need list of positions and direction (use strand info for direction, if missing assume both directions)
		if (position_file[-3:] == "BED") or  (position_file[-3:] == "bed"):
			# read a BED file
			# 	for each chromosome, creates list of entrys, entry format:<start, end, name, score, strand, orig line>
			specific_sites = K.NOX_Read_BED(position_filename, thresh=-1)

			# only process the positions in the correct chromo region
			chr = ""
			site_list = specific_sites[chr]
			for site in site_list:
				pos = s[0]
				pos = DNA_POS(pos)		# change pos from chromo position to model DNA position

				directions =  "wc" 	# assume both directions
				if (s[3] != ""):
					if (s[3] == "+"):
						directions = "w"
					elif (s[3] == "-"):
						directions = "w"

				pos_list.append( [pos, directions] )	
				print "Appending:",  [pos, fields[1]]

			
		else: # assume it is a GFF3 formatted file
			# read GFF3 file
			# 	for each chromosome, creates list of entrys, entry format:<start, score, strand, orig line>
			specific_sites = K.NOX_Read_GFF3(position_filename, thresh=-1)

			# only process the positions in the correct chromo region
			chr = ""
			site_list = specific_sites[chr]
			for site in site_list:
				pos = s[0]
				pos = DNA_POS(pos)		# change pos from chromo position to model DNA position

				directions =  "wc" 	# assume both directions
				if (s[2] != ""):
					if (s[2] == "+"):
						directions = "w"
					elif (s[2] == "-"):
						directions = "w"

				pos_list.append( [pos, directions] )	
				print "Appending:",  [pos, fields[1]]
						
	elif (specific_pos):
		print "\tProcessing specific RNAP positions:", specific_pos
		# parse the line
		# 		Entry format: "[pos,directions],[pos2, dir2]..." with comma separator
		# add each item to the pos list
		specific_pos = specific_pos.strip()
		specific_pos = specific_pos.replace(' ','') #strip out all spacing
		positions = specific_pos.split("],")
		# last item has a closing ']', remove it
		if (positions[-1][-1] == ']'):
			positions[-1] = positions[-1][:-1]
		# each item in positions has format "[pos,directions" without closing bracket
		# for each item in positions
		#	split into two values (pos, dir_list)
		#	create entry in position list
		for item in positions:
			item = item[1:]  	# strip off '['
			fields = item.split(',')
			try :
				pos = int(fields[0])
				# change pos from chromo position to model DNA position
				pos = DNA_POS(pos)
				pos_list.append( [pos, fields[1]] )
				print "Appending:",  [pos, fields[1]]
			except:
				print "Trouble parsing item:", item
	else:
		print "Assigning all positions for RNAP init"
		for i in range(1,N_DNA+1):
			# add entry for this position of DNA, both directions
			pos_list.append( [i, "wc"] )		
		
	outfile.write("//\n// ----%s----\n//\n"%"SSA_RNAP Reactants")

	s = SSA_RNAP("test", params, DNA_section, outfile)
	if (not s.MODELING):	return
	
#	s.Init_List_Reactants(pos_list, N_DNA)
	s.Init_Reactants(N_DNA)
	s.Write_Reactants()

	outfile.write("//\n// ----%s----\n//\n"%"SSA_RNAP Rules")
	
	rules = []
	rule = SSA_Rule("")
	rule.AddComment("%s"%"RNAP Rules")
	rules.append(rule)		

	##########################
	#	For each transition/action create a set of rules across all positions
	
			
	# create BINDING at positions given in directions given
	#		Transitions/Actions: 	BINDING
	#								BINDING_ABORT
	#								BINDING_STABILIZAION
	#								INITIATION
	#								
	#								
	for pos,dirs in pos_list:	# positions of initiation
		# get directions from parameters
		if (dirs):
			dir_list = list(dirs)
		else:
			dir_list = ('w', 'c')
			
		#if direction specified for this pos
		#	dir_list = direction(s)
		
		for d in dir_list:
			if (specific_pos):
				print "BINDING at",pos,d
			new_rules = s.Binding(pos, [], "", d, 0)
			rules.extend(new_rules)

			new_rules = s.Binding_Abort(pos, d, 0)
			rules.extend(new_rules)
		
			if (s.TATA):
				new_rules = s.Binding_Stabilization(pos, dir, 0, 1, s.TATA_WIDTH)
				rules.extend(new_rules)

			# RNAP_INIT_0 -> RNAP_INIT_1 -> ... -> RNAP_INIT_N -> RNAP_W
			for stage in xrange(1,s.stages):

				new_rules = s.Initiate(pos, d, stage)
				rules.extend(new_rules)
			
				new_rules = s.Binding_Abort(pos, d, stage)
				rules.extend(new_rules)

				if (s.TATA):
					new_rules = s.Binding_Stabilization(pos, dir, stage, 1, s.TATA_WIDTH)
					rules.extend(new_rules)

			new_rules = s.Binding_Abort(pos, d, -1) # abort from 
			rules.extend(new_rules)
			
	Write_Rule_Set(rules, outfile)	
	rules = []
	
	##########################
	# ACTIVATION
	for pos,dirs in pos_list:	# positions of initiation
		# get directions from parameters
		if (dirs):
			dir_list = list(dirs)
		else:
			dir_list = ('w', 'c')
		
		for d in dir_list:
			if (specific_pos):
				print "ACTIVATING at",pos,d
			new_rules = s.Activate(pos, d, 1, TATA_SIZE)
			rules.extend(new_rules)
	Write_Rule_Set(rules, sys.stdout)	

	# EVICT
	for pos in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Evict(pos, d)
			rules.extend(new_rules)

	# TRANSCRIBE
	for pos in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Transcribe(pos, d)
			rules.extend(new_rules)

	# MOVE
	for pos in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Move(pos, d)
			rules.extend(new_rules)

	# TRANSCRIPTIONAL INTERFERENCE
	for pos in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Interference(pos, d)
			rules.extend(new_rules)

	# EVICT_NUCLEOSOME
	for pos in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Evict_Nucleosome(pos, d)
			rules.extend(new_rules)

	Write_Rule_Set(rules, outfile)	
	rules = []

	##########################
	# mark ends of DNA to terminate the RNAP
	for i in range(s.width+10):
		new_rules = s.Terminate(i+1, 'c')	# terminate Crick RNAP near left edge
		rules.extend(new_rules)

	for i in range(s.width+10):
		new_rules = s.Terminate(N_DNA-i, 'w')		# terminate Watson RNAP near right edge
		rules.extend(new_rules)

	##########################
		
	Write_Rule_Set(rules, outfile)	
	outfile.write("//\n// !!^^^^%s^^^^!!\n//\n"%"SSA_RNAP Rules")

	return
###################################################################################################

def Generate_RNAP_Rules(params, outfile):

	TATA_SIZE = N_DNA_POS(8)

	outfile.write("//\n// ----%s----\n//\n"%"SSA_RNAP Reactants")

	s = SSA_RNAP("test", params, DNA_section, outfile)
	if (not s.MODELING):	return
	
	s.Init_Reactants(N_DNA)
	s.Write_Reactants()

	outfile.write("//\n// ----%s----\n//\n"%"SSA_RNAP Rules")
	
	rules = []
	rule = SSA_Rule("")
	rule.AddComment("%s"%"RNAP Rules")
	rules.append(rule)		

	##########################
	#	For each transition/action create a set of rules across all positions
	#
	# create BINDING in both directions
	#		Transitions/Actions: 	BINDING
	#								BINDING_ABORT
	#								BINDING_STABILIZAION
	#								INITIATION
	#								
	#								
	
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Binding(pos, [], "", d, 0)
			rules.extend(new_rules)

			new_rules = s.Binding_Abort(pos, d, 0)
			rules.extend(new_rules)
		
			if (s.TATA):
				new_rules = s.Binding_Stabilization(pos, dir, 0, 1, s.TATA_WIDTH)
				rules.extend(new_rules)

			# RNAP_INIT_0 -> RNAP_INIT_1 -> ... -> RNAP_INIT_N -> RNAP_W
			for stage in xrange(1,s.stages):

				new_rules = s.Initiate(pos, d, stage)
				rules.extend(new_rules)
			
				new_rules = s.Binding_Abort(pos, d, stage)
				rules.extend(new_rules)

				if (s.TATA):
					new_rules = s.Binding_Stabilization(pos, dir, stage, 1, s.TATA_WIDTH)
					rules.extend(new_rules)

			new_rules = s.Binding_Abort(pos, d, -1) # abort from 
			rules.extend(new_rules)
			
	Write_Rule_Set(rules, outfile)	
	rules = []
	
	##########################
	# ACTIVATION
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Activate(pos, d, 1, TATA_SIZE)
			rules.extend(new_rules)

	# EVICT
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Evict(pos, d)
			rules.extend(new_rules)

	# TRANSCRIBE
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Transcribe(pos, d)
			rules.extend(new_rules)

	# MOVE
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Move(pos, d)
			rules.extend(new_rules)

	# TRANSCRIPTIONAL INTERFERENCE
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Interference(pos, d)
			rules.extend(new_rules)

	# EVICT_NUCLEOSOME
	for i in range(1,N_DNA+1):		# valid range is from [1..N_DNA]
		for d in ('w', 'c'):
			new_rules = s.Evict_Nucleosome(pos, d)
			rules.extend(new_rules)

	Write_Rule_Set(rules, outfile)	
	rules = []

	##########################
	# mark ends of DNA to terminate the RNAP
	for i in range(s.width+10):
		new_rules = s.Terminate(i+1, 'c')	# terminate Crick RNAP near left edge
		rules.extend(new_rules)

	for i in range(s.width+10):
		new_rules = s.Terminate(N_DNA-i, 'w')		# terminate Watson RNAP near right edge
		rules.extend(new_rules)

	##########################
		
	Write_Rule_Set(rules, outfile)	
	outfile.write("//\n// ^^^^%s^^^^\n//\n"%"SSA_RNAP Rules")

	return
	
###################################################################################################

def Test_SSA_RNAP():
	global N_DNA
	global NT_PER_GROUP
	global N_GROUP_PER_NUCLEOSOME
	global N_INIT_STAGES
	global RNAP_N_POS 
	global params
	global DNA_section
	global START_POS
	global LOCAL_CONCENTRATION
	
	test_params = False
	test_rules  = False
	paramfile   = "PARAM.INI"
	outfilename	= "SRB_rules.cmdl"
	outdir		= "Results"
	model		= "SRB_model"
	chromo		= 0
	chr_start	= -1
	chr_end		= -1
	DNA_section = ""
	model_RNAP  = False
	model_NUC   = True
	model_TATA  = False
	try:
		opts, args = getopt.getopt(sys.argv[1:], "o:p:", ["help", "DNA=", "results="])
	except getopt.GetoptError:
		Usage()
		sys.exit(1)
	if not opts:
		Usage()
		sys.exit(1)

	motifs = []							 
	for opt, value in opts:
		#print opt, value
		if	 opt == '-p':  			paramfile   = value
		elif opt == '-o':			outfilename = value
		elif opt == '--DNA':		DNA_section = value
		elif opt == '--results':	outdir	    = value
		else: 
			print "Unhandled opt [%s][%s]"%(opt,value)

	Make_Results_Dir(outdir)
	outfile = open(outdir+'/'+outfilename, 'w',0)

	log_filename = outdir + '/' + "SRB.log"
	log = K.NOX_LogFile(log_filename)
	line = "["
	line += "][".join(sys.argv)
	line += "]"
	log.Display(line)

	log.Display("Rule file:%s/%s"%(outdir,outfilename))
	log.Display("Log file: %s/SRB.log"%outdir)
	
	params = K.NOX_ParamFile(paramfile)
	print "sections:",params.sections
	
	NT_PER_GROUP = 25

	Generate_RNAP_Rules(params, sys.stdout)

###############################################################################

def Make_Comment_Rule(comment):
	rule = SSA_Rule("")
	rule.AddComment(comment)
	return rule

###############################################################################

def Generate_NUC_Rules(params, outfile, dna):
	global N_DNA
	global DNA_section

	nuc = SSA_Nucleosome("test", params, outfile)
	if (not nuc.MODELING):	
		outfile.write("//\n// ----%s----\n//\n"%"NOT modeling nucleosomes")
		return
	
	outfile.write("//\n// ----%s----\n//\n"%"SSA_NUC Reactants")
	nuc.Init_Reactants(N_DNA)
	nuc.Write_Reactants()

	outfile.write("//\n// ----%s----\n//\n"%"SSA_NUC Rules")
	
	rules = []
	rules.append(Make_Comment_Rule("%s"%"NUCLEOSOME Rules"))		

	nuc.GetPositionalRates(params,DNA_section,dna)
			
	###############################################################################
	#
	#	Rules for nucleosome Formation and Eviction
	# 
	###############################################################################

	comment = "Nucleosome N_GROUPS=%d, Linker=%d, +/- %d positions, %d extra rules per position"%(nuc.GROUPS, nuc.linker_size, nuc.linker_size, nuc.linker_size*2)
	rules.append(Make_Comment_Rule(comment))
			
	for pos in xrange(1,N_DNA+1):
	
		new_rules = nuc.Initiate(pos)
		rules.extend(new_rules)		

		new_rules = nuc.Bind(pos)
		rules.extend(new_rules)		

		new_rules = nuc.Linker_Check(pos, nuc.linker_size, nuc.linker_size)
		rules.extend(new_rules)		

		new_rules = nuc.Unbind(pos)
		rules.extend(new_rules)		
		
		new_rules = nuc.Evict(pos)
		rules.extend(new_rules)		
		
	Write_Rule_Set(rules, outfile)	
	outfile.write("//\n// ^^^^%s^^^^\n//\n"%"SSA_NUC Rules")

	return
#
#  Run dizzy modeler:
#  		../bin/runmodel.sh -simulator gillespie-direct -ensembleSize 1         \   
#       	              -startTime 0 -stopTime 3000 -numSamples 3000      \
#           	          -modelFile model.cmdl> output.csv
#  Visualized with:
#		python PlotModelResults.py -v -n output.csv
#
###############################################################################
if __name__ == '__main__':
    Main()
#	Test_SSA_RNAP()
	
###############################################################################
###############################################################################
