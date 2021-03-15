'''import subprocess, sys
## command to run - tcp only ##
cmd = "pip --version"
 
## run it ##
p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
 
running = True
while running:
    out = p.stderr.read(1)
    if str(out) == "b''":
        running = False
    else:
        print(out)'''

for x in range(100):
    print("Line: " + str(y))
