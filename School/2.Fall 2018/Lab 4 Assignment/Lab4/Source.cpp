// Ethan McFarland
// 09/17/2018
// CS201L Lab #4 (2D arrays)

#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main() {
	ifstream fin;
	ofstream fout;
	/*
	int rows, cols;
	int matrix[20][20];*/

	fin.open("input.txt");
	fout.open("output.txt");

	if (fin.is_open()) {
		std::string val;
		while (getline(fin, val)) {
			fout << 10 << endl;
		}
	}

	/* Failed attetmpt
	while (fin >> rows >> cols) {
		fout << rows << " " << cols << endl;
			
		for (int i=0; i<rows; i++) {
			for (int j=0; j<cols; j++) {
				int val;
				fin >> val;
				matrix[i][j] = val;
				//fout << 10;
			}
		}
	}*/
	
	fout.close();
	fin.close();

	return 0;
}