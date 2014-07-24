#
# Makefile for running WASSON figure models
#

ifeq ($(DNA)x,x)
quit:
	@echo "No DNA section is defined DNA=$(DNA)"
	@exit 1
endif

ifeq ($(HOSTNAME),tuxedo.colorado.edu)
SOURCE_DIR = $(HOME)/SSA_Rule_Builder
DIZZY_DIR = /usr/local/src/Dizzy
DIZZY_SH  = $(DIZZY_DIR)/bin/runmodel.sh
else
ifeq ($(HOSTNAME),vieques.colorado.edu)
SOURCE_DIR = $(HOME)/SSA_Rule_Builder
DIZZY_DIR = /usr/local/src/Dizzy
DIZZY_SH  = $(DIZZY_DIR)/bin/runmodel.sh
else
SOURCE_DIR = $(HOME)/Documents/Drive/VizGroup/KnoxModel
DIZZY_DIR = $(HOME)/Documents/Drive/VizGroup/KnoxModel/Dizzy
DIZZY_SH  = $(SOURCE_DIR)/runmodel.sh
endif
endif

RULE_DIR_NAME = $(DNA)_Results
RULE_FILE = SRB_rules_$(DNA).cmdl
RULE_DIR  = $(SOURCE_DIR)/$(RULE_DIR_NAME)
#RULE_DIR  = $(SOURCE_DIR)/IME4_Results
#RULE_DIR  = $(SOURCE_DIR)/WassonResults
#RULE_DIR  = $(SOURCE_DIR)/LickwarResults
RULES     = $(RULE_DIR)/$(RULE_FILE)
CSV       = $(RULE_DIR)/srb_$(DNA).csv
UTILS     = $(SOURCE_DIR)/KnoxUtils.py

all: $(RULES) $(CSV) 

APP    = SRB.py
SOURCE = $(SOURCE_DIR)/$(APP)
INI    = $(SOURCE_DIR)/Wasson.ini
#INI    = $(SOURCE_DIR)/Lickwar.ini

#BUILDING   = @echo "Building Model ... $(DNA)" ; figlet "Building Model - $(DNA)"
#ANALYZING  = @echo "Analyzing Simulation ... $(DNA)" ; figlet "Analyzing Simulation - $(DNA)"	
#SIMULATING = @echo "Simulating Model ... $(DNA)" ; figlet "Simulating Model - $(DNA)" ; /bin/bash -c date | figlet 

BUILDING   = @echo "Building Model ... $(DNA)"
ANALYZING  = @echo "Analyzing Simulation ... $(DNA)"
SIMULATING = @echo "Simulating Model ... $(DNA)"


$(UTILS)c : $(UTILS)
	python $(UTILS)
	
RULE_OPTS = 
	
$(RULES): $(INI) $(SOURCE) $(UTILS)c $(SOURCE_DIR)/makefile
	$(BUILDING)
	python $(SOURCE) -p $(INI) -o $(RULE_FILE) --results=$(RULE_DIR) --DNA=DNA_$(DNA) $(RULE_OPTS)
	$(COUNT_RULES)
	$(COUNT_SPECIES)
#	@echo "count of rules:" $(RULES) ; grep -c -v --regex="^//" $(RULES) 

RULES: $(RULES) $(UTILS) $(UTILS)c

RM_RULES: 
	rm -f $(RULES)
	
MAKERULES =	python $(SOURCE) -p $(INI) -o $(RULE_FILE) --results=$(RULE_DIR) --DNA=DNA_

#COUNT_RULES = @echo "count of rules:" $(RULES) ; grep -c -v --regex="^//" $(RULES) 
COUNT_RULES = @echo "count of rules:" $(RULES) ; grep -v --regex="^//" $(RULES) | grep -c -v "= "
COUNT_SPECIES = @echo "count of species:" $(RULES) ; grep -v --regex="^//" $(RULES) | grep -c "= "

COUNTS:
	$(COUNT_RULES)
	$(COUNT_SPECIES)

# default count of time steps
STEPS = 500

SAMPLES = $(STEPS)

MODELER = gibson-bruck
#MODELER = gillespie-direct
#MODELER = tauleap-simple

$(CSV_OLD):  $(RULES) makefile
	date
	pushd	$(RULES_DIR)
	time nice $(DIZZY_SH) -simulator $(MODELER) -ensembleSize 1 -startTime 0 -stopTime $(STEPS) -numSamples $(SAMPLES) -modelFile $(RULE_FILE) > $(CSV) 
	popd

$(CSV_PREV):  $(RULES) makefile
	/bin/bash -c "date ;\
        pushd Results ; \
		time nice $(DIZZY_DIR)/bin/runmodel.sh -simulator $(MODELER) -ensembleSize 1 -startTime 0 -stopTime $(STEPS) -numSamples $(SAMPLES) -modelFile $(RULE_FILE) > $(CSV) ; \
        popd ; "

$(CSV):  $(RULES) makefile 
	@echo "Source:" $(SOURCE_DIR)
	@echo " Rules:" $(RULE_DIR)
	@echo "      :" $(RULE_FILE)
	@echo "   CSV:" $(CSV)
	$(SIMULATING)
	/bin/bash -c "date ;\
        pushd $(DIZZY_DIR)/bin ; \
		time nice $(DIZZY_DIR)/bin/runmodel.sh -simulator $(MODELER) -ensembleSize 1 -startTime 0 -stopTime $(STEPS) -numSamples $(SAMPLES) -modelFile $(RULE_DIR)/$(RULE_FILE) > $(CSV) ; \
        popd ; "

RESIM:
	@echo "Source:" $(SOURCE_DIR)
	@echo " Rules:" $(RULE_DIR)
	@echo "      :" $(RULE_FILE)
	@echo "   CSV:" $(CSV)
	$(COUNT_RULES)
	$(COUNT_SPECIES)
	$(SIMULATING)
	/bin/bash -c "date ;\
        pushd $(DIZZY_DIR)/bin ; \
		time nice $(DIZZY_DIR)/bin/runmodel.sh -simulator $(MODELER) -ensembleSize 1 -startTime 0 -stopTime $(STEPS) -numSamples $(SAMPLES) -modelFile $(RULE_DIR)/$(RULE_FILE) > $(CSV) ; \
        popd ; "
   
   
N_START = 1
#N_ITER = 5
N_ITER = 100
                
N_RESIM:
	@echo "Simulating current rule set:" 
	@echo "Source:" $(SOURCE_DIR)
	@echo " Rules:" $(RULE_DIR)
	@echo "      :" $(RULE_FILE)
	$(COUNT_RULES)
	$(COUNT_SPECIES)
	$(SIMULATING)

	@count=$(N_START) ; while [[ $$count -le $(N_ITER) ]] ; do \
		figlet -w 500 "       DNA: $(DNA)" ; \
		figlet -w 500 "       Iteration: $$count" ; \
		/bin/bash -c "date ;\
        pushd $(DIZZY_DIR)/bin ; \
		time nice $(DIZZY_DIR)/bin/runmodel.sh -simulator $(MODELER) -ensembleSize 1 -startTime 0 -stopTime $(STEPS) -numSamples $(SAMPLES) -modelFile $(RULE_DIR)/$(RULE_FILE) > $(RULE_DIR)/srb_$(DNA)_$$count.csv ; \
        popd ";  \
        ((count = count + 1)) ; \
		done
                        
N_CORR:
	@echo "Calculating correlations::" 
	@count=$(N_START) ; while [[ $$count -le $(N_ITER) ]] ; do \
		first=$(RULE_DIR)/srb_$(DNA)_$$count ; \
		second=_NUC_Occupancy.wig ; \
		echo $$first [$$second] ; \
		corrfile=$(RULE_DIR)/srb_$(DNA)_$$count"_NUC_Occupancy.wig" ; \
		echo "   WIG:" $$corrfile ; \
		python test_stats.py -S 65500 -E 67500 $$corrfile ; \
        ((count = count + 1)) ; \
		done
                        
N_VIS:
	@echo "Calculating correlations::" 
	@count=$(N_START) ; while [[ $$count -le $(N_ITER) ]] ; do \
		echo "   CSV:" $(RULE_DIR)/srb_$(DNA)_$$count.csv ; \
		nice python ./PlotModelResults.py --param=$(INI) --DNA=DNA_$(DNA) $(VIS_PARAM) $(RULE_DIR)/srb_$(DNA)_$$count.csv ; \
        ((count = count + 1)) ; \
		done
                        
CSV:  $(CSV)

LOG2:  
	@python ./WindowAvg.py -2 -w 40 $(RULE_DIR)/srb_$(DNA)_NUC_Occupancy.wig > $(RULE_DIR)/srb_$(DNA)_NUC_AVG_LOG2.wig
	@python ./test_stats.py $(RULE_DIR)/srb_$(DNA)_NUC_AVG_LOG2.wig 
	
FIG_LIST = FIG_1A FIG_1B

FIGS:   # $(RULES) makefile
	@echo "Step list: $(STEP_LIST)"
	@for FIG in  $(FIG_LIST) ; do  \
		echo "vvvvvvvv" ; \
		echo "Figure: $$FIG" ; \
		date  ; \
		make DNA=$$FIG
		echo "End of Figure: $$FIG" ; \
		echo "^^^^^^^^" ; \
	   	done
	   	
ROMAN = 
RANDOM_SELECT = 0
#VIS_PARAM =   -v -n -r $(RANDOM_SELECT) $(ROMAN)
VIS_PARAM =  -t 500 -v -n -r $(RANDOM_SELECT) $(ROMAN)
#VIS_PARAM = -n

VIS : $(RULES) $(CSV) 
	$(ANALYZING) 
	python ./PlotModelResults.py --param=$(INI) --DNA=DNA_$(DNA) $(VIS_PARAM) $(CSV)
	@echo visualizing $(DNA)

VIS2_PARAM = -v -n -s -d 277500:279800
VIS2 : $(RULES) $(CSV) 
	python ./PlotModelResults.py --param=$(INI) --DNA=DNA_$(DNA) $(VIS2_PARAM) $(CSV) 
	
VIS3 :  
	python ./PlotModelResults.py --param=$(INI) --DNA=DNA_$(DNA) $(VIS_PARAM) $(VIS3_PARAM) -o Output_$(DNA).out $(CSV) | tee PlotModelResults.log
	@echo visualizing $(DNA)
	sed 's/chr16/chrXVI/' Output_$(DNA).out | \
		sed 's/chr15/chrXV/'   | \
		sed 's/chr14/chrXIV/'  | \
		sed 's/chr13/chrXIII/' | \
		sed 's/chr12/chrXII/'  | \
		sed 's/chr11/chrXI/'   | \
		sed 's/chr10/chrX/'    | \
		sed 's/chr9/chrIX/'    | \
		sed 's/chr8/chrVIII/'  | \
		sed 's/chr7/chrVII/'   | \
		sed 's/chr6/chrVI/'    | \
		sed 's/chr5/chrV/'     | \
		sed 's/chr4/chrIV/'    | \
		sed 's/chr3/chrIII/'   | \
		sed 's/chr2/chrII/'    | \
		sed 's/chr1/chrI/'     > \
		Output_$(DNA).wig	

REVIS : 
	$(ANALYZING) 
	python ./PlotModelResults.py --param=$(INI) --DNA=DNA_$(DNA) $(VIS_PARAM) $(CSV)
	@echo visualizing $(DNA)

VISIT :  
	$(ANALYZING) 
	python ./VisModelResults.py --param=$(INI) --DNA=DNA_$(DNA) $(VIS_PARAM) $(CSV)
	@echo visualizing $(DNA)

STAT : 
	python ./test_stats.py  $(RULE_DIR)/srb_$(DNA)_NUC_Occupancy.wig

	
DROP = ~/Documents/Drive/KnoxModel/backup/.
DROPC = ~/Documents/Drive/KnoxModel/backup/.

BACKUP : 
	cp $(SOURCE_DIR)/makefile $(DROP)
	cp $(SOURCE_DIR)/*.mak $(DROP)
	cp $(SOURCE_DIR)/*.ini $(DROP)
	cp $(SOURCE_DIR)/*.py $(DROP)
	cp $(SOURCE_DIR)/bin/*.py $(DROP)
	cp $(SOURCE_DIR)/*.R $(DROP)
	cp $(SOURCE_DIR)/bin/*.R $(DROP)
	# backup Wasson compete changes
	cp $(SOURCE_DIR)/*.R $(DROPC)
	cp $(SOURCE_DIR)/*.rb $(DROPC)
	cp $(SOURCE_DIR)/*.yaml $(DROPC)
	cp $(SOURCE_DIR)/README.txt $(DROPC)
	# Copy all the Documentation
	cp $(SOURCE_DIR)/DOC/* $(DROP)/DOC/.
#	cp  $(DROP)
	
DNA_PREFIX = *
if [ -z $(DNA) ]; then \
	DNA_PREFIX = $(DNA); \
fi
clean:
	rm $(SOURCE_DIR)/Results/$(DNA_PREFIX)
	rmdir $(SOURCE_DIR)/Results
	
