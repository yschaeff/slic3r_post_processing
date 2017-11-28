#!/usr/bin/python3

## USAGE: ./gcode-post.py <file.gcode>
## post process gcode file in-place

##### Tunables #####
BEDX = 250.0        ## mm, Print bed width
BEDY = 210.0        ## mm, Print bed depth
ZHOP = 0.5          ## mm, Retract lift. Don't consider this a layet change. 0 -> disable
XPOS = BEDX*0.75    ## mm, X-coordinate for print head during picture
YPOS = BEDY*0.50    ## mm, Y-coordinate for print head during picture
XDRIFT = -0.5       ## mm, X-panning after each layer.
YDRIFT = 0.0        ## mm, Y-panning after each layer.
XMOVE = False       ## bool, move print head out of the way

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
    tokens = rawline.split(';')
    line = tokens[0].strip()
    if (len(tokens) > 1):
        comment = tokens[1].strip()
    else:
        comment = None
    if (comment == "AFTER_LAYER_CHANGE" and absolute_coordinates):
        if XMOVE:
            pre = "G1 X%f Y%f F%f; YBS pre\n" % (XPOS, YPOS, pos['F'])
        else:
            pre = "G1 Y%f F%f; YBS pre\n" % (YPOS, pos['F'])
        for i in range(10): pre += "G0; Filling print queue\n"
        if XMOVE:
            post = "G1 X%f Y%f F%f; YBS post\n" % (pos['X'], pos['Y'], pos['F'])
        else:
            post = "G1 Y%f F%f; YBS post\n" % (pos['Y'], pos['F'])
        #post += "M300 S440 P200\n" ##beep
        YPOS = max(0, min(BEDY, YPOS+YDRIFT))
        XPOS = max(0, min(BEDX, XPOS+XDRIFT))
    if G28.match(line): ## HOME
        pos = {'X':0, 'Y':0, 'Z':0, 'F':0, 'E':0}
    elif G90.match(line): ## ABS
        absolute_coordinates = True
    elif G1.match(line) and absolute_coordinates:
        coords = C.findall(line)
        for c in coords:
            #if c[1] == 'Z':
                #dz = int(1000*pos['Z'])-int(1000*float(c[2]))
                #zmove = (abs(dz) != int(1000*ZHOP))
            pos[c[1]] = float(c[2])
    if pre: output.append(pre)
    output.append(rawline)
    if post: output.append(post)

with open(sys.argv[1], 'wt') as fd: fd.writelines(output)
