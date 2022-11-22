from utils import error

def set(file, cpu_bit):
    global fd

    fd = open(file, 'rb')


def run(start, size):
    global fd

    end = start + size
    asm = b"".join(fd.readlines())[start:end]

    print(asm)


if __name__ == "__main__":
    error.send(error.USAGE)