# ECE5740-UofU-Final-Project-Scheduling
Final project repository for the ECE 5740 course from the UofU. This is for creating a scheduling program

---Running the Program---
To run the program, open up the terminal and cd to the directory the src, test, bench, etc. folders are in
Then run: python3 src/auto_schedule.py -l=# -a=# -g=[file]
-l=# is the latency constraint
-a=# is the memory constraint
-g=[file] is the filepath to an .edgelist file type

Example: python3 src/auto_schedule.py -l=5 -a=20 -g=test/test1.edgelist
The above will run the schedule script with latency = 5, memory = 20 and test1.edgelist as inputs

The outputs for the program are:
latencyMin.ilp - contains the generated ILP file for the latency minimization
memoryMin.ilp - contains the generated ILP file for the memory minimization
latOutput.sol - GLPK's glpsol output for the latency minimization
memOutput.sol - GLPK's glpsol output for the latency minimization

---Additional Notes---
This program is not fully completed. Due to struggles with understanding GLPK's ILP file format for this specific graphing format and poor understanding of what was specific to the project, there was too much time spend on having to fix errors and restructuring the project in a new way. Currently it will create 2 ILP files (that are the same) that GLPK process and returns outputs on.

If the -l=# value is too small, an exception will be thrown and displayed in the terminal on purpose. Increase the -l=# value until the exception is no longer thrown. Reason for this is because you cannot minimize a graph to a latency that is lower than the number of levels actually needed to have a functioning DFG

---Bugs---
When doing test on the rand_DFG_s50_1.edgelist with an l=50 value, GLPK does not work because values like the x124 is used repeatedly in the constraint conditions causing a CPLX LP file processing error. We were able to fix the issue with the i#: sectioins but it also happens in the constraints area c#: and we didn't have time to fix it. For all the benchmakr rand_DFG_s10_#.edgelist versions the program works
