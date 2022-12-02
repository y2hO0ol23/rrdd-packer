from keystone import *

func_rva = {}

class asm():
    def __init__(self, arch, mode):
        self.ks = Ks(arch, mode)
        self.data = b""
    
    def write(self, code:bytes)->None:
        encoding, count = self.ks.asm(code)
        self.data += bytes(encoding)


def make_iat(rva:int)->tuple:
    global func_rva

    dll_list = {
        b"KERNEL32.dll":[
            (0, b'GetProcAddress')
        ]
    }
    descriptor = b""
    descriptor_size = (len(dll_list) + 1) * 20
    dll_name_list = b'\x00'.join(dll_list.keys()) + b'\x00'
    data = b""

    # descriptor | dll_name_list | INT1_name_list | INT1 | IAT1 | INT2_name_list | INT2 | ...
    # rva        | dll_name_rva  | rva + offset                 | rva + offset(inc)
    
    dll_name_rva = rva + descriptor_size

    for dll_name in dll_list.keys():
        func_rva[dll_name] = {}
        offset = descriptor_size + len(dll_name_list) + len(data)

        INT = b""
        IAT = b""
        func_name_list = b"\x00".join(list(map(lambda x: x[0].to_bytes(2, 'little') + x[1], dll_list[dll_name]))) + b'\x00'
        data += func_name_list
        INT_name_offset = 0
        for hint, func in dll_list[dll_name]:
            INT_name_rva = rva + offset + INT_name_offset
            func_rva[dll_name][func] = INT_name_rva

            INT += INT_name_rva.to_bytes(8, 'little')
            IAT += INT_name_rva.to_bytes(8, 'little')

            INT_name_offset += 2 + len(func) + 1
        
        INT += b'\x00'*8
        IAT += b'\x00'*8
            
        INT_rva = rva + offset + len(func_name_list)
        IAT_rva = INT_rva + len(INT)
        data += INT + IAT

        descriptor += INT_rva.to_bytes(4, 'little')
        descriptor += b"\xff\xff\xff\xff"
        descriptor += b"\xff\xff\xff\xff"
        descriptor += dll_name_rva.to_bytes(4, 'little')
        descriptor += IAT_rva.to_bytes(4, 'little')
        
        dll_name_rva += len(dll_name) + 1

    descriptor += b'\x00' * 0x14
    return descriptor + dll_name_list + data, len(descriptor)


def build(packed_data_rva:int, tree_data_rva:int, case_size:int, internal_count:int, tree_size:int, entry_list:list)->bytes:
    global func_rva

    code = asm(KS_ARCH_X86, KS_MODE_64)
    code.write(b'push    rbp')
    code.write(b'push    rdi')
    code.write(b'sub     rsp, 0E8h')
    code.write(b'lea     rbp, [rsp+20h]')
    code.write(b'xor     eax, eax')
    code.write(b'lea     rsp, [rbp+0C8h]')
    code.write(b'pop     rdi')
    code.write(b'pop     rbp')
    code.write(b'rep')
    code.write(b'ret')

    return code.data