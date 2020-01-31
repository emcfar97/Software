// Ethan McFarland
// 9/24/2018
// CS201L Lab #6

#include <iostream>
#include <math.h>
#include <fstream>
#include <string>
using namespace std;

double distance(double x1, double x2, double y1, double y2, double z1, double z2) {

	double new_x = pow(x1 - x2, 2);
	double new_y = pow(y1 - y2, 2);
	double new_z = pow(z1 - z2, 2);

	return sqrt(new_x + new_y + new_z);
}

int main() {

	ifstream fileIn("input.txt");
	ofstream fileOut("output.txt");

	double x1[20];
	double x2[20];
	double y1[20];
	double y2[20];
	double z1[20];
	double z2[20];
	
	/* Read points from input file, assign to appropriate array, then assign 
	calculated distance to output file*/
	while(fileIn.good()) {

		fileIn >> x1[0] >>  x2[0] >> y1[0] >> y2[0] >> z1[0] >> z2[0];
		fileOut << distance(x1[0], x2[0], y1[0], y2[0], z1[0], z2[0]) << endl;
	}

	return 0;
}