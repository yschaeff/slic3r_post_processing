#!/usr/bin/python3

## USAGE: ./gcode-post.py <file.gcode>
## post process gcode file in-place

##### Tunables #####
BEDX = 250.0        ## mm, Print bed width
BEDY = 210.0        ## mm, Print bed depth
ZHOP = 0.5          ## mm, Retract lift. Don't consider this a layet change. 0 -> disable
XPOS = BEDX*0.75    ## mm, X-coordinate for print head during picture
YPOS = BEDY*0.25    ## mm, Y-coordinate for print head during picture
XDRIFT = -0.1       ## mm, Y-panning after each layer.
YDRIFT = 0.1        ## mm, Y-panning after each layer.

import re, sys
if len(sys.argv) != 2: sys.exit("Provide exactly 1 argument: filename.gcode")
G1 = re.compile('^G1 ')
G90 = re.compile('^G90')
G28 = re.compile('^G28')
C = re.compile('(([XYZEF])(-?\d+(\.\d+)?))')
with open(sys.argv[1]) as fd: lines = fd.readlines()
pos = {'X':0, 'Y':0, 'Z':0, 'F':0, 'E':0}
absolute_coordinates = False
output = []

for rawline in lines:
    pre = post = None
    line = rawline.split(';')[0].strip()
    if G28.match(line): ## HOME
        pos = {'X':0, 'Y':0, 'Z':0, 'F':0, 'E':0}
    elif G90.match(line): ## ABS
        absolute_coordinates = True
    elif G1.match(line) and absolute_coordinates:
        coords = C.findall(line)
        zmove = False
        for c in coords:
            if c[1] == 'Z':
                dz = int(1000*pos['Z'])-int(1000*float(c[2]))
                zmove = (abs(dz) != int(1000*ZHOP))
            pos[c[1]] = float(c[2])
        if zmove:
            pre = "G1 X%f Y%f F%f; YBS pre\n" % (XPOS, YPOS, pos['F'])
            for i in range(10): pre += "G4 P1; Filling print queue\n"
            post = "G1 X%f Y%f F%f; YBS post\n" % (pos['X'], pos['Y'], pos['F'])
            YPOS = max(0, min(BEDY, YPOS+YDRIFT))
            XPOS = max(0, min(BEDX, XPOS+XDRIFT))
    if pre: output.append(pre)
    output.append(rawline)
    if post: output.append(post)

with open(sys.argv[1], 'wt') as fd: fd.writelines(output)
