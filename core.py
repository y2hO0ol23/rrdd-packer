import pefile
import os
import shutil

import pack

from utils import error

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
    pe.close()
    
    # make backup and make tree
    tree_data, case_size, internal_count, tree_size = pack.set_tree(file)
    packed, data_size = pack.run(file)

    code = "".join(open('./code.cpp','r').readlines())

    code = code.replace('0/*@data_size*/'       , str(data_size))
    code = code.replace('0/*@case_size*/'       , str(case_size))
    code = code.replace('0/*@tree_size*/'       , str(tree_size))
    code = code.replace('0/*@internal_count*/'  , str(internal_count))
    code = code.replace('0/*@packed*/'          , str([i for i in packed])[1:-1])
    code = code.replace('0/*@tree_data*/'       , str([i for i in tree_data])[1:-1])

    os.remove('./builder/build/source.cpp')
    open('./builder/build/source.cpp','w').write(code)

    path = os.path.dirname(os.path.realpath(__file__))
    cmd = 'powershell.exe -c "&{Import-Module ./builder/Microsoft.VisualStudio.DevShell.dll; Enter-VsDevShell 578e8fee; cd %s/builder; msbuild}"'%path

    os.system(cmd)
    os.remove(file)
    shutil.copy('./builder/x64/Release/build.exe', file)

if __name__ == "__main__":
    error.send(error.USAGE)