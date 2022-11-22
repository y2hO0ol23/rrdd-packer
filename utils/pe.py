import pefile

IMAGE_SCN_CNT_CODE                =  0x00000020
IMAGE_SCN_CNT_INITIALIZED_DATA    =  0x00000040
IMAGE_SCN_CNT_UNINITIALIZED_DATA  =  0x00000080
IMAGE_SCN_MEM_EXECUTE             =  0x20000000
IMAGE_SCN_MEM_READ                =  0x40000000
IMAGE_SCN_MEM_WRITE               =  0x80000000

IMAGE_FILE_MACHINE_I386           =  0x014c
IMAGE_FILE_MACHINE_IA64           =  0x0200


def can_write(section:pefile.SectionStructure):
    return (section.Characteristics & IMAGE_SCN_MEM_WRITE) > 0

def can_execute(section:pefile.SectionStructure):
    return (section.Characteristics & IMAGE_SCN_MEM_EXECUTE) > 0

def is_386(cpu_ver):
    return (cpu_ver & IMAGE_FILE_MACHINE_I386) > 0

def is_A64(cpu_ver):
    return (cpu_ver & IMAGE_FILE_MACHINE_IA64) > 0