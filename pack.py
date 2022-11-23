from utils import error, huffman
from queue import PriorityQueue

global fd

def set(file)->None:
    global fd

    fd = open(file, 'rb')


def init(data:bytes)->PriorityQueue:
    res = [0 for _ in range(0x100)]
    pq = PriorityQueue()

    for item in data:
        res[item] += 1

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
    for i in range(1, nodeNumber + 1):
        if i in save:
            binary += "1" + bin(i)[2:].zfill(8)
        else:
            binary += "0"
        
        while len(binary) > 8:
            bytetree += bytes([int(binary[:8], 2)])
            binary = binary[8:]
    
    if len(binary) > 0:
        bytetree += bytes([int(binary.rjust(8,'0'), 2)])
    
    print(len(bytetree))
    return bytes([len(bytetree)]) + bytetree


def build_tree(data:bytes)->dict:
    pq = init(data)

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


def run(start:int, size:int)->tuple:
    global fd

    end = start + size
    data = b"".join(fd.readlines())[start:end]
    
    tree = build_tree(data)
    res = pack(data, tree)

    return res, bytetree(tree)


if __name__ == "__main__":
    error.send(error.USAGE)