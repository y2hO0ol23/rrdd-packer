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

class MODIFY():
    def __init__(self, file:str):
        open(".MODIFY",'wb').write(b"".join(open(file, 'rb').readlines()))
        self.pe = pefile.PE(".MODIFY")
        self.file = file
    
    def close(self):
        self.pe.close()
        os.remove(".MODIFY")

    def set(self):
        self.pe.write(self.file)
    

def make_section(file:str, count:int):
    m = MODIFY(file)

    # set count of sections
    m.pe.FILE_HEADER.NumberOfSections = count

    # set size of header
    NT_base = m.pe.DOS_HEADER.e_lfanew
    section_base = NT_base + 24 + m.pe.FILE_HEADER.SizeOfOptionalHeader
    section_end = m.pe.OPTIONAL_HEADER.SizeOfHeaders

    m.pe.OPTIONAL_HEADER.SizeOfHeaders = section_base + 0x28 * count

    # set alignments to 1
    m.pe.OPTIONAL_HEADER.FileAlignment = 0x200
    m.pe.OPTIONAL_HEADER.SectionAlignment = 0x200

    m.set()

    # remove sections
    fd = b"".join(open(file, 'rb').readlines())
    items = [[0, fd, len(fd)]]

    for section in m.pe.sections:
        raw = section.PointerToRawData
        size = section.SizeOfRawData
        items = cut(items, raw, raw+size)
        
    m.close()

    items = cut(items, section_base + 0x28, section_end)
    items = b"".join([i[1] for i in items])
    items = items + items[section_base:section_base+0x28] * (count - 1)

    open(file,'wb').write(items)


def set_section(file:str, section_list:list)->None:
    make_section(file, len(section_list))

    m = MODIFY(file)
    header_end = m.pe.OPTIONAL_HEADER.SizeOfHeaders
    raw_start = utils.pe.align(header_end)

    raw_pos = raw_start
    raw_list = []
    section_data = b""
    for i, section in enumerate(section_list):
        m.pe.sections[i].Name = (section["name"].ljust(8,'\x00')[:8]).encode()
        m.pe.sections[i].Misc_VirtualSize = len(section["data"])
        m.pe.sections[i].VirtualAddress = section["rva"]
        m.pe.sections[i].SizeOfRawData = len(section["data"])
        m.pe.sections[i].PointerToRawData = raw_pos
        m.pe.sections[i].PointerToRelocations = 0x00000000
        m.pe.sections[i].PointerToLinenumbers = 0x00000000
        m.pe.sections[i].NumberOfRelocations = 0x0000
        m.pe.sections[i].NumberOfLinenumbers = 0x0000
        m.pe.sections[i].Characteristics = section["Characteristics"]

        raw_list.append(raw_pos)
        raw_pos = utils.pe.align(raw_pos + len(section["data"]))
        section_data += section_list[i]["data"]
        if i != len(section_list) - 1:
            section_data += b'\x00'*(raw_pos - raw_start - len(section_data))

    m.set()
    m.close()

    fd = b"".join(open(file, 'rb').readlines())
    open(file,'wb').write(fd[:header_end] + b'\x00'*(raw_start - header_end) + section_data)


def iat(file:str, address:int, size:int):
    m = MODIFY(file)
    for i in range(len(m.pe.OPTIONAL_HEADER.DATA_DIRECTORY)):
        m.pe.OPTIONAL_HEADER.DATA_DIRECTORY[i].VirtualAddress = 0
        m.pe.OPTIONAL_HEADER.DATA_DIRECTORY[i].Size = 0

    m.pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].VirtualAddress = address
    m.pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].Size = size

    m.set()
    m.close()


def base(file:str, code_rva:int, data_rva):
    m = MODIFY(file)
    m.pe.OPTIONAL_HEADER.AddressOfEntryPoint = code_rva
    m.pe.OPTIONAL_HEADER.BaseOfCode = code_rva
    m.pe.OPTIONAL_HEADER.BaseOfData = code_rva
    m.set()
    m.close()