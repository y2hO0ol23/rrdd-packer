import pefile
import os

import pack
import repair
import machine

from utils import error
import utils.pe

class form:
    def __init__(self, offset, size, data, rva, option):
        self.offset = offset
        self.size = size
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
    
    # make backup and make tree
    pe = pefile.PE(backup(file))
    tree_data, case_size, internel_count, tree_size = pack.set(file, pe.sections)
 
    packed = []
    last = 0
    for section in pe.sections:
        raw = section.PointerToRawData
        size = section.SizeOfRawData
        res = pack.run(raw, size)

        rva = section.VirtualAddress
        option = section.Characteristics

        packed.append(form(last, size, res, rva, option))
        last += len(res)

    code = machine.build(packed)

    packed_data = b"".join([i.data for i in packed])
    
    section = [
        {
            "name" : ".packed",
            "data" : packed_data,
            "rva" : last,
            "Characteristics" : utils.pe.IMAGE_SCN_MEM_READ  | 
                                utils.pe.IMAGE_SCN_MEM_WRITE | 
                                utils.pe.IMAGE_SCN_CNT_INITIALIZED_DATA
        },
        {
            "name" : ".tree",
            "data" : tree_data,
            "rva" : last + len(packed_data),
            "Characteristics" : utils.pe.IMAGE_SCN_MEM_READ  | 
                                utils.pe.IMAGE_SCN_MEM_WRITE | 
                                utils.pe.IMAGE_SCN_CNT_INITIALIZED_DATA
        }
    ]
    pe = repair.set_section(file, section) 
    
    print(tree_data)
    print(case_size, internel_count, tree_size)
    print(packed_data)
    for i in packed:
        print("[%d, %d, %d, %d]"%(i.offset,i.size,i.rva,i.option))


if __name__ == "__main__":
    error.send(error.USAGE)