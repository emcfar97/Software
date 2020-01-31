#include "Matrix.h"

Matrix::Matrix(int rows, int cols) {
	
	this[rows][cols];
}

void Matrix::setMatrix(int row, int col, int val) {
	
	this[row][col] = val;
}

Matrix Matrix::get(int row, int col) {
	
	return this[row][col];
}

Matrix Matrix::operator+(Matrix other) {

	Matrix sum(rows, cols);

	for (int i = 0; i < rows; i++) {
		for (int j = 0; j < cols; j++) {
			sum[i][j] = this->get(i, j) + other.get(i, j);
		}
	}
	return sum;
}

ostream& Matrix::operator<<(ostream& outputStream, Matrix& m) {

	for (int i = 0; i < rows; i++) {
		for (int j = 0; j < cols; j++) {
			outputStream << m.get(i, j) << ' ';
		}
		outputStream << endl;
	}
}


