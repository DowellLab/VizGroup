
To run the simulation locally, you need to update lines 21-23 in `makefile` to point to the location of the simulation code and Dizzy install. Dizzy is included in the repo under KnoxModel/Dizzy/.


Example commands:

```
make INI=CLN2.ini DNA=CLN2_4 STEPS=1000

python PlotModelResults.py --DNA=DNA_CLN2_4 --param=CLN2.ini --objs-file=CLN2_4_objs.txt -v CLN2_4_Results/srb_CLN2_4.csv
```

This will output the file used for the unity visualization to CLN2_4_objs.txt