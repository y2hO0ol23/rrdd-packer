from keystone import *

func_rva = {}

class asm():
    def __init__(self):
        self.data = b""
    
    def write(self, code:bytes)->None:
        self.data += b"\n"
        self.data += code


def make_iat(rva:int)->bytes:
    global func_rva

    HINT = 0xbbaa
    dll_list = {
        b"api-ms-win-crt-heap-l1-1-0.dll":[
            (HINT, b"calloc"),
            (HINT, b"free")
        ],
        b"KERNEL32.dll":[
            (HINT, b'GetProcAddress')
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
        print(dll_list[dll_name])
        func_name_list = b"\x00".join(list(map(lambda x: x[1], dll_list[dll_name]))) + b'\x00'
        data += func_name_list 
        INT_name_offset = 0
        for hint, func in dll_list[dll_name]:
            INT_name_rva = rva + offset + INT_name_offset
            func_rva[dll_name][func] = INT_name_rva

            INT += hint.to_bytes(2, 'little') + INT_name_rva.to_bytes(4, 'little')
            IAT += INT_name_rva.to_bytes(4, 'little')

            INT_name_offset += len(func) + 1
        
        INT += b'\x00'*4
        IAT += b'\x00'*4
            
        INT_rva = offset + len(func_name_list)
        IAT_rva = INT_rva + len(INT)
        data += INT + IAT

        descriptor += INT_rva.to_bytes(4, 'little')
        descriptor += b"\xff\xff\xff\xff"
        descriptor += b"\xff\xff\xff\xff"
        descriptor += dll_name_rva.to_bytes(4, 'little')
        descriptor += IAT_rva.to_bytes(4, 'little')
        
        dll_name_rva += len(dll_name) + 1

    print(hex(rva))
    print(descriptor)
    print(data)

    print(descriptor + b'\x00'*20 + data)

    return descriptor + b'\x00'*20 + data


def build(new_section_data:list, packed_offset:int, tree_offset:int, case_size:int, internal_count:int, tree_size:int, entry_list:list):    
    """ks = Ks(KS_ARCH_X86, KS_MODE_32)
    code = asm()
    code.write(b'') # malloc(tree_size)
    code.write(b'')
    encoding, count = ks.asm(code)
    """
    pass