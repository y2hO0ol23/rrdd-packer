#include <windows.h>
#include <iostream>
#include <stdexcept>
#include <cstring>

using namespace std;

void hideConsole() {
	HWND hWnd = GetConsoleWindow();
	ShowWindow(hWnd, SW_HIDE);
}

wchar_t filename[MAX_PATH + 4];
char cmd[MAX_PATH + 4 + 14] = "attrib +s +h ";
unsigned char *tree, *fd, *is_internal;

#define case_size 0/*@case_size*/
#define tree_size 0/*@tree_size*/
#define internal_count 0/*@internal_count*/
#define data_size 0/*@data_size*/

#define internal_offset ((case_size + 7) / 8)
#define leaf_offset (internal_offset + internal_count)
#define offset 0b10000000

unsigned char packed[] = { 0/*@packed*/ };
unsigned char tree_data[] = { 0/*@tree_data*/ };

void build_tree() {
	tree = (unsigned char*)malloc(tree_size);
	is_internal = (unsigned char*)malloc(tree_size);
	memset(is_internal, 1, tree_size);

	unsigned char v;
	unsigned int node = 1;
	unsigned int internal_idx = 0;
	unsigned int leaf_idx = 0;

	for (int i = 0; i < case_size + 2; i++) {
		if (i & 7) {}
		else {
			v = tree_data[i / 8];
		}

		if (offset & v) {
			tree[node] = tree_data[leaf_offset+leaf_idx];
			is_internal[node] = 0;
			leaf_idx++;
			node++;
		}
		else {
			node += ((unsigned short*)(&tree_data[internal_offset]))[internal_idx];
			internal_idx++;
		}
		v <<= 1;
	}
}

void unpack() {
	fd = (unsigned char*)malloc(data_size);
	unsigned char off = 0;
	unsigned char v = 0;
	unsigned int idx = 0;
	for (int i = 0; i < data_size; i++) {
		unsigned int node = 1;
		while (1) {
			if (off == 0) {
				v = packed[idx++];
				off = offset;
			}
			node <<= 1;
			if (off & v)
				node++;

			off >>= 1;
			if (is_internal[node]){}
			else{
				fd[i] = tree[node];
				break;
			}
		}
	}
}

int main(int argc, char* argv[]) {
	int filelen = GetModuleFileNameW(nullptr, filename, MAX_PATH - 4);
	filename[filelen - 3] = L'o';
	filename[filelen - 2] = L'u';
	filename[filelen - 1] = L't';
	filename[filelen - 0] = L'.';
	filename[filelen + 1] = L'e';
	filename[filelen + 2] = L'x';
	filename[filelen + 3] = L'e';

	HANDLE  hFile = CreateFile(filename, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);

	build_tree();
	unpack();

	WriteFile(hFile, fd, data_size, NULL, NULL);
	CloseHandle(hFile);

	unsigned int len;

	len = WideCharToMultiByte(CP_ACP, 0, filename, -1, NULL, 0, NULL, NULL);
	WideCharToMultiByte(CP_ACP, 0, filename, -1, cmd + 13, len, NULL, NULL);
	system(cmd);

	len = WideCharToMultiByte(CP_ACP, 0, filename, -1, NULL, 0, NULL, NULL);
	char* cfilename = (char*)malloc(len + 1);
	WideCharToMultiByte(CP_ACP, 0, filename, -1, cfilename, len, NULL, NULL);
	string v(cfilename);

	for (int i = 1; i < argc;i++) {
		v += ' ';
		v += argv[i];
	}

	system(v.c_str());

	DeleteFile(filename);

	return 0;
}

