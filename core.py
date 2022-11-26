import pefile
import os

import pack
import repair

from utils import error
import utils.pe

class form:
    def __init__(self, offset, data, rva, option):
        self.offset = offset
        self.data = data
        self.rva = rva
        self.option = option


def backup(file:str)->None:
    backup_name = file+'.backup'

    fd = b"".join(open(file, 'rb').readlines())
    open(backup_name, 'wb').write(fd)

    return backup_name


def start(file:str)->None:
    try:
        pe = pefile.PE(file)
    except: error.send("file : pe format error")
    
    if pe.FILE_HEADER.NumberOfSections == 0:
        error.send("file : no section!")
    pe.close()
    
    pe = pefile.PE(backup(file))
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

    
    section = [
        {
            "name" : ".packed",
            "data" : b"".join([i.data for i in packed]),
            "rva" : last,
            "Characteristics" : utils.pe.IMAGE_SCN_MEM_READ | utils.pe.IMAGE_SCN_CNT_INITIALIZED_DATA
        }
    ]
    pe = repair.set_section(file, section)


if __name__ == "__main__":
    error.send(error.USAGE)