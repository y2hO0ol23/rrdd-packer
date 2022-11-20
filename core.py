import sys
import subprocess
from utils import error

try:
    import pefile
except:
    print("install module name pefile...")
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable,'-m', 'pip', 'install', '--upgrade', 'pefile'])
    print("end to install pefile")

import struct

def start(file):
    try:    pe = pefile.PE(file)
    except: error.send("file : pe format error")

    for section in pe.sections:
        print(section.Name.decode('utf-8'))

if __name__ == "__main__":
    error.send(error.USAGE)