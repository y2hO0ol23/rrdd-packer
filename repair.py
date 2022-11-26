import pefile
import os

import utils.pe

def cut(items:list, st:int, ed:int)->list:
    for i in range(len(items)):
        l, pice, r = items[i]
        if l <= st and ed <= r:
            left = []
            if l != st: left.append([l,pice[:st-l],st])
            if ed != r: left.append([ed,pice[ed-l:],r])

            items = items[:i] + left + items[i+1:]
            break
    
    return items

class TEMP():
    def __init__(self, file:str):
        open(".TEMP",'wb').write(b"".join(open(file, 'rb').readlines()))
        self.pe = pefile.PE(".TEMP")
        self.file = file
    
    def close(self):
        self.pe.close()
        os.remove(".TEMP")

    def set(self):
        self.pe.write(self.file)
    

def make_section(file:str, count:int):
    t = TEMP(file)

    # set count of sections
    t.pe.FILE_HEADER.NumberOfSections = count

    # set size of header
    NT_base = t.pe.DOS_HEADER.e_lfanew
    section_base = NT_base + 24 + t.pe.FILE_HEADER.SizeOfOptionalHeader
    section_end = t.pe.OPTIONAL_HEADER.SizeOfHeaders

    t.pe.OPTIONAL_HEADER.SizeOfHeaders = section_base + 0x28 * count

    # set alignments to 1
    t.pe.OPTIONAL_HEADER.FileAlignment = 1
    t.pe.OPTIONAL_HEADER.SectionAlignment = 1

    t.set()

    # remove sections
    fd = b"".join(open(file, 'rb').readlines())
    items = [[0, fd, len(fd)]]

    for section in t.pe.sections:
        raw = section.PointerToRawData
        size = section.SizeOfRawData
        items = cut(items, raw, raw+size)
        
    t.close()

    items = cut(items, section_base + 0x28, section_end)
    items = b"".join([i[1] for i in items])
    items = items + items[section_base:section_base+0x28] * (count - 1)

    open(file,'wb').write(items)


def set_section(file:str, section_list:list):
    make_section(file, len(section_list))

    t = TEMP(file)
    header_end = t.pe.OPTIONAL_HEADER.SizeOfHeaders
    raw_pos = header_end
    for i, section in enumerate(section_list):
        t.pe.sections[i].Name = (section["name"].rjust(8,'\x00')[:8]).encode()
        t.pe.sections[i].Misc_VirtualSize = len(section["data"])
        t.pe.sections[i].VirtualAddress = section["rva"]
        t.pe.sections[i].SizeOfRawData = len(section["data"])
        t.pe.sections[i].PointerToRawData = raw_pos
        t.pe.sections[i].PointerToRelocations = 0x00000000
        t.pe.sections[i].PointerToLinenumbers = 0x00000000
        t.pe.sections[i].NumberOfRelocations = 0x0000
        t.pe.sections[i].NumberOfLinenumbers = 0x0000
        t.pe.sections[i].Characteristics = section["Characteristics"]

        raw_pos += len(section["data"])
    
    t.set()
    t.close()

    fd = b"".join(open(file, 'rb').readlines())
    open(file,'wb').write(fd[:header_end] + b"".join([i["data"] for i in section_list]) + fd[header_end:])



