from utils import error, huffman
from queue import PriorityQueue

global fd, tree


def init(pack_range:bytes)->PriorityQueue:
    global fd

    res = [0 for _ in range(0x100)]
    pq = PriorityQueue()

    for st, ed in pack_range:
        for i in range(st, ed):
            res[fd[i]] += 1

    for val, cnt in enumerate(res):
        if cnt != 0:
            new = huffman.Node(val, cnt)
            pq.put((new.freq, new))
    
    return pq


def tree_data()->tuple:
    size = 1
    save = {}
    for val in range(0x100):
        if val in tree:
            nodeNumber = 1
            for bit in tree[val]:
                nodeNumber *= 2
                if bit == "1":
                    nodeNumber += 1
            
            if size < nodeNumber + 1:
                size = nodeNumber + 1
            
            save[nodeNumber] = val

    case_bin = b""
    internal_data = b""
    leaf_data = b""
    binary = ""
    
    case_size = 0
    count = 0
    for i in range(1, size):
        if i in save:
            while count > 0:
                binary += "0"
                internal_data += (count & 0xffff).to_bytes(2,'little')
                count //= 0x10000
                case_size += 1
            binary += "1"
            leaf_data += bytes([save[i]])
            case_size += 1
        else:
            count += 1
        
        while len(binary) > 8:
            case_bin += bytes([int(binary[:8], 2)])
            binary = binary[8:]
    
    if len(binary) > 0:
        case_bin += bytes([int(binary.ljust(8,'0'), 2)])
    
    return case_bin + internal_data + leaf_data, case_size, len(internal_data), size


def build_tree(pack_range:list)->dict:
    pq = init(pack_range)

    while pq.qsize() > 1:
        left = pq.get()[1]
        right = pq.get()[1]

        new = huffman.Node(left, right)
        pq.put((new.freq, new))
    
    tree = pq.get()[1].result()

    return tree


def pack(data:bytes, tree:dict)->bytes:
    res = b""
    binary = ""
    for item in data:
        binary += tree[item]
        while len(binary) > 8:
            res += bytes([int(binary[:8], 2)])
            binary = binary[8:]
    
    if len(binary) > 0:
        res += bytes([int(binary.ljust(8,'0'), 2)])
    
    return res


def set(file:str, sections:list)->tuple:
    global fd, tree

    fd = b"".join(open(file, 'rb').readlines())

    pack_range = []
    for section in sections:
        size = section.SizeOfRawData
        raw = section.PointerToRawData
        pack_range.append([raw,raw+size])
    
    tree = build_tree(pack_range)

    return tree_data()


def run(start, size)->bytes:
    global fd, tree
    
    data = fd[start:start+size]

    res = pack(data, tree)

    return res


if __name__ == "__main__":
    error.send(error.USAGE)