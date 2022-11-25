import pefile

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


def clear_section(file:str, pe:pefile.PE):
    with open(file, 'rb') as f:
        fd = b"".join(f.readlines())
        f.close()
    items = [[0, fd, len(fd)]]

    for section in pe.sections:
        raw = section.PointerToRawData
        size = section.SizeOfRawData
        items = cut(items, raw, raw+size)
    
    fd = open(file,'wb')


def section(file:str, pe:pefile.PE, packed:list):
    clear_section(file, pe)
        
    pe.sections[0].Name = '.huffman'.rjust(8,'\x00')

    pe.sections[1].Name = '.vm'.rjust(8,'\x00')

    pe.sections[2].Name = '.code'.rjust(8,'\x00')