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
    tree_data, case_size, internal_count, tree_size = pack.set_tree(file, pe.sections)
 
    packed = []
    raw_end = 0
    rva_end = 0
    for section in pe.sections:
        raw = section.PointerToRawData
        size = section.SizeOfRawData
        res = pack.run(raw, size)

        rva = section.VirtualAddress
        option = section.Characteristics

        packed.append(form(raw_end, size, res, rva, option))
        raw_end += len(res)
        rva_end = max(utils.pe.align(rva + size), rva_end)

    packed_data = b"".join([i.data for i in packed])

    iat_data, iat_descriptor_size = machine.make_iat(rva_end)

    section = [
        {
            "name" : ".data",
            "data" : iat_data + packed_data + tree_data,
            "rva" : rva_end,
            "Characteristics" : utils.pe.IMAGE_SCN_MEM_READ  | 
                                utils.pe.IMAGE_SCN_MEM_WRITE | 
                                utils.pe.IMAGE_SCN_CNT_INITIALIZED_DATA
        }
    ]
    
    code = machine.build(section, len(iat_data), len(iat_data) + len(packed_data), case_size, internal_count, tree_size, pe.DIRECTORY_ENTRY_IMPORT)
    code_rva = utils.pe.align(rva_end + len(section[0]["data"]))
    section.append({
        "name" : ".text",
        "data" : code,
        "rva" : code_rva,
        "Characteristics" : utils.pe.IMAGE_SCN_MEM_READ     |  
                            utils.pe.IMAGE_SCN_MEM_EXECUTE  |
                            utils.pe.IMAGE_SCN_CNT_CODE
    })
    repair.set_section(file, section)
    
    #print(tree_data)
    #print(case_size, internal_count, tree_size)
    #print(packed_data)
    #for i in packed:
    #    print("[%d, %d, %d, %d]"%(i.offset,i.size,i.rva,i.option))

    repair.iat(file, rva_end, iat_descriptor_size)
    repair.base(file, code_rva, rva_end)


if __name__ == "__main__":
    error.send(error.USAGE)