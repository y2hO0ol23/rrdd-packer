tree_data = eval("".join(open('tree_data','r').readlines()))
case_size = 378
internel_count = 258
tree_size = 29432

packed = eval("".join(open('packed','r').readlines()))

data = [
    [0, 6656, 4096, 1610612768],
    [5159, 4608, 12288, 1073741888],
    [7718, 512, 20480, 3221225536],
    [7885, 1024, 24576, 1073741888],
    [8276, 512, 28672, 1073741888],
    [8687, 512, 32768, 1107296320]
]

#############

tree = [-1] * tree_size
internel_offset = (case_size + 7) // 8
leaf_offset = internel_offset + internel_count
offset = 0b10000000

node = 1
internel_idx = 0
leaf_idx = 0

for i in range(case_size + 2):
    if i % 8 == 0:
        v = tree_data[i // 8]
    
    if offset & v:
        tree[node] = tree_data[leaf_offset + leaf_idx]
        leaf_idx += 1
        node += 1
    else:
        # node += (WORD*)(&tree_data[internel_offset])[internel_idx]
        idx = internel_offset + (internel_idx * 2)
        node += int.from_bytes(tree_data[idx:idx+2],'little')
        internel_idx += 1

    v <<= 1

"""
# for check tree
sv = {}

def find(node, now):
    if node < tree_size:
        if tree[node] == -1:
            find(node*2, now+"0")
            find(node*2+1, now+"1")
        else:
            sv[tree[node]] = now

find(1, "")
print(sv)
"""

def unpack(num):
    idx = 0
    offset = 0
    v = 0
    res = b""
    for _ in range(data[num][1]):
        node = 1
        while True:
            if offset == 0:
                v = packed[data[num][0] + idx]
                idx += 1
                offset = 0b10000000

            node *= 2
            if offset & v:
                node += 1
                
            offset >>= 1
            
            if tree[node] != -1:
                res += bytes([tree[node]])
                break
    
    return res

for i in range(len(data)):
    print(unpack(i))
