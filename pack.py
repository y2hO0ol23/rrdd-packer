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


def bytetree(tree:dict)->bytes:
    last = 1
    save = {}
    for val in range(0x100):
        if val in tree:
            nodeNumber = 1
            for bit in tree[val]:
                nodeNumber *= 2
                if bit == "1":
                    nodeNumber += 1
            
            if last < nodeNumber:
                last = nodeNumber
            
            save[nodeNumber] = val

    bytetree = b""
    binary = ""
    count = 0
    for i in range(1, last + 1):
        if i in save:
            if count > 0:
                v = count.to_bytes(2,'little')
                binary += "0" + bin(v[0])[2:].zfill(8) + bin(v[1])[2:].zfill(8)
                count = 0
            binary += "1" + bin(save[i])[2:].zfill(8)
        else:
            count += 1
            if count == 0xffff:
                binary += "0" + "1"*16
                count = 0
        
        while len(binary) > 8:
            bytetree += bytes([int(binary[:8], 2)])
            binary = binary[8:]
    
    if len(binary) > 0:
        bytetree += bytes([int(binary.rjust(8,'0'), 2)])
    
    size = len(bytetree)
    return size.to_bytes(2,'little') + bytetree


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
        res += bytes([int(binary.rjust(8,'0'), 2)])
    
    return res


def set(file:str, sections:list)->bytes:
    global fd, tree

    fd = b"".join(open(file, 'rb').readlines())

    pack_range = []
    for section in sections:
        size = section.SizeOfRawData
        raw = section.PointerToRawData
        pack_range.append([raw,raw+size])
    
    tree = build_tree(pack_range)

    return bytetree(tree)


def run(start, size)->bytes:
    global fd, tree
    
    data = fd[start:start+size]

    res = pack(data, tree)

    return res


if __name__ == "__main__":
    error.send(error.USAGE)