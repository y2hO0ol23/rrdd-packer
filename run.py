import sys
import os
import core
from utils import error

def main():
    if len(sys.argv) != 2:
        error.send(error.USAGE)

    file = sys.argv[1]
    if not os.path.isfile(file):
        error.send("error : file not exist")
    
    core.start(file)

if __name__ == "__main__":
    main()