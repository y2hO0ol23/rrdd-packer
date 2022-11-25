import pefile
import os

import pack
import repair

from utils import error
import utils.pe
import copy

class form:
    def __init__(self, offset, data, rva, option):
        self.offset = offset
        self.data = data
        self.rva = rva
        self.option = option


def start(file:str)->None:
    try:
        fd = b"".join(open(file, 'rb').readlines())
        print(fd)
        open(file+'.backup', 'wb').write(fd)
        pe = pefile.PE(file+'.backup')
    except: 
        os.remove(file+'.backup')
        error.send("file : pe format error")
    
    tree = pack.set(file, pe.sections)

    packed = []
    last = 0
    for section in pe.sections:
        raw = section.PointerToRawData
        size = section.SizeOfRawData
        res = pack.run(raw, size)

        rva = section.VirtualAddress
        option = section.Characteristics

        packed.append(form(last, res, rva, option))
        last += len(res)
        print(section.Name, option)
    
    pe = repair.section(file, pe, last)


if __name__ == "__main__":
    error.send(error.USAGE)