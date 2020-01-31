// Ethan McFarland
// 10/8/2018
// CS201L Exam #1

#include <iostream>
#include <fstream>
#include "Matrix.h"
using namespace std;

int main() {

	ifstream fileIn("input.txt");
	ofstream fileOut("output.txt");

	int rows, cols, val;

	/* Reads input from file, initializing matrices 1 and 2, then adds
	them to create matrix3, and then outputs this to the output file*/
	while (!fileIn.eof()) {
		fileIn >> rows >> cols;
		Matrix matrix1(rows, cols);
		Matrix matrix2(rows, cols);


		for (int i = 0; i < rows; i++) {
			for (int j = 0; j < cols; j++) {
				fileIn >> val;
				matrix1.setMatrix(i, j, val);
			}
		}

		for (int i = 0; i < rows; i++) {
			for (int j = 0; j < cols; j++) {
				fileIn >> val;
				matrix2.setMatrix(i, j, val);
			}
		}
		Matrix matrix3 = matrix1 + matrix2;
		fileOut << matrix3;
	}

	fileIn.close();
	fileOut.close();
	return 0;
}