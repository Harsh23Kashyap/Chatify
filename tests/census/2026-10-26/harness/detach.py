import os, sys, subprocess
if os.fork() > 0: sys.exit(0)
os.setsid()
if os.fork() > 0: sys.exit(0)
devnull = os.open(os.devnull, os.O_RDWR)
os.dup2(devnull, 0); os.dup2(devnull, 1); os.dup2(devnull, 2)
os.execvp(sys.argv[1], sys.argv[1:])
