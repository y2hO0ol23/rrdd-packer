#include<stdio.h>
int unpack(int num);
char tree_data[10] = "asdf";
int case_size = 378, internal_count = 258, tree_size = 29432;
char packed=[10] = "zxcv";
int data[6][4] = {
    {0, 6656, 4096, 1610612768},
    {5159, 4608, 12288, 1073741888},
    {7718, 512, 20480, 3221225536},
    {7885, 1024, 24576, 1073741888},
    {8276, 512, 28672, 1073741888},
    {8687, 512, 32768, 1107296320}
};

int main(){
    int tree[tree_size] = {-1,};
    int internal_offset = (case_size+7)/8;
    int leaf_offset = internal_offset+internal_count;
    int offset = 0b10000000;
    
    int node = 1, internal_idx = 0, leaf_idx = 0,idx;
    for(int i=0;i<case_size+2){
        if(i%8 == 0) char v = tree_data[i/8];

        if(offset&v){
            tree[node] = tree_data[leaf_offset + leaf_idx];
            ++leaf_idx;
            ++node;
        }
        else{
            idx = internal_offset + (internal_idx * 2);
            for(int j=idx+1;j>idx-1;j--){
                node += tree_data[j];
            }
        }
        v <<=1;
    }

}

int unpack(int num){
    int idx = 0,offset=0,v=0,node,res_idx=0;
    char res[50] = "";
    for(int i=0;i<data[num][i];i++){
        node = 1
        while(1){
            if(offset == 0){
                v=packed[data[num][0]+idx];
                ++idx;
                offset = 0b10000000;
            }
            
            node *= 2;
            if(offset & v){
                ++node;
            }

            offset >>=1;

            if(tree[node] != -1){
                res[res_dix+=] = tree[node];
                break; 
            }
        }
    }
    return res;
}
