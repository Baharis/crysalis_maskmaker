# crysalis_maskmaker
A small python3 script containing one class 'Mask' dedicated to
preparing elliptical masks for CrysAlisPro software using multiple
"dc rejectrect" commands. Since the code depends only on generic functions
from 'numpy' package, it should run on any python 3.4+  interpreter.

To test the code, run the file `maskmaker.py` in python3 without modifications.
This should result in a file `edge_mask.mac` being created in working directory.
The file should consist of 100 lines of `dc rejectrect` commands,
masking for a 1000-radius circular area on 2048 x 2048 detector.
In order to create different masks, modify the code at the bottom of the file.

This small tool was made by Daniel Tchoń, dtchon at chem.uw.edu.pl,
for members of Crystallochemistry Laboratory at Faculty of Chemistry,
University of Warsaw.