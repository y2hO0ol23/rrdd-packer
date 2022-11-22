import pefile

import obfuscator

from utils import error
import utils.pe


def select_section(sections:list)->None:
    can_pack = []

    for i, section in enumerate(sections):
        if not utils.pe.can_write(section) and utils.pe.can_execute(section):
            can_pack.append(i)
    
    return can_pack


def check_cpu(pe:pefile.PE):
    cpu_ver = pe.FILE_HEADER.Machine

    if utils.pe.is_386(cpu_ver):
        return 32
    
    if utils.pe.is_A64(cpu_ver):
        return 64
    
    error.send("file : support only Intel 32 or 64")


def start(file:str)->None:
    try:    pe = pefile.PE(file)
    except: error.send("file : pe format error")
    
    cpu_bit = check_cpu(pe)
    obfuscator.set(file, cpu_bit)

    pack_list = select_section(pe.sections)

    for i in pack_list:
        section = pe.sections[i]

        obfuscator.run(section.PointerToRawData, section.SizeOfRawData)
        print(section.Name.decode('utf-8'))


if __name__ == "__main__":
    error.send(error.USAGE)