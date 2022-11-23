import pefile

import pack

from utils import error
import utils.pe

def select_section(sections:list)->list:
    can_pack = []

    for i, section in enumerate(sections):
        if not utils.pe.can_write(section) and utils.pe.can_execute(section):
            can_pack.append(i)
    
    return can_pack


def start(file:str)->None:
    try:    pe = pefile.PE(file)
    except: error.send("file : pe format error")

    pack_list = select_section(pe.sections)

    pack.set(file)
    for i in pack_list:
        section = pe.sections[i]

        res, tree = pack.run(section.PointerToRawData, section.SizeOfRawData)
        
        print(res)
        print(tree)
        


if __name__ == "__main__":
    error.send(error.USAGE)