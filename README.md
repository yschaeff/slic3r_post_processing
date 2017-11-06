Post processing script for Slic3r generated gcode
==
slic3r-post.py: Move the printhead out of the way before each layer change and put the model in a know location. This will add some print time but time lapses become much nicer to look at.
- Save the file on your disk and make it executable.
- In Slic3r add the path to: Print Settings/Output options/Post-processing scripts
- In Octoprint capture images "on Z change" and make sure Octoprint, Slic3r and the script agree on Z-hop.

Now whenever Slic3r generates a gcode file it will pass through the script. It is also possible to run the script stand-alone.
- python3 slic3r-post.py <file>
  
Note: Slic3r complained about import errors on stdout for me. Setting the following environment variables worked for me: 
- export PYTHONHOME=/usr/lib/python3.6/ 
- export PYTHONPATH=/usr/lib/python3.6/
