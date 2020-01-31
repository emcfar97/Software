#ifndef MATRIX_H
#define MATRIX_H

#include <iostream>
using namespace std;

class Matrix
{
private: 
	int rows;
	int cols;

public:
	Matrix();
	Matrix(int rows, int cols);
	void setMatrix(int row, int col, int val);
	Matrix get(int row, int col);
	Matrix operator+(Matrix other);
	//friend ostream& operator>> (ostream& inputStream, Matrix& m);
	friend ostream& operator<< (ostream& outputStream, Matrix& m);
};

#endif