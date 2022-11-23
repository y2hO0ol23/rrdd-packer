import sys
import subprocess
import os
import core

try:
    import pefile
except:
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'pefile'])
    import pefile

try:
    import keystone
except:
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'keystone-engine'])
    import keystone

from utils import error

def main()->None:
    if len(sys.argv) != 2:
        error.send(error.USAGE)

    file = sys.argv[1]
    if not os.path.isfile(file):
        error.send("error : file not exist")
    
    core.start(file)


if __name__ == "__main__":
    main()