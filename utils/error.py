import sys

USAGE = "usage : python run.py <file>"

def send(msg:str="Error") -> None:
    print(msg)
    sys.exit()

if __name__ == "__main__":
    send(USAGE)
