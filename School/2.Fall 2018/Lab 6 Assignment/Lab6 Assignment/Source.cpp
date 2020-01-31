// Ethan McFarland
// 10/1/2018
// CS201L Lab #6

#include <iostream>
#include <fstream>
#include "Point.h"
using namespace std;

int main()
{
	// File input/output variables
	ifstream fin("input.txt");
	ofstream fout("output.txt");

	Point points1[20];
	Point points2[20];
	int x1, y1, z1;
	int numPoints = 0;
	
	// If input file not found, quit with error message.
	if (!fin)
	{
		cout << "Input file not opened!" << endl;
		exit(1);
	}
	
	while (!fin.eof()) {

		fin >> x1 >> y1 >> z1;
		points1[numPoints].setCoordinates(x1, y1, z1);

		fin >> x1 >> y1 >> z1;
		points2[numPoints].setCoordinates(x1, y1, z1);
		numPoints++;
	}

	// Retrieve points from input file, then insert them into points array
	fout << "Distances from origin :\n";
	for (int i = 0; i<numPoints; i++) {
		fout << points1[i].calcDistance() << ' ' << points2[i].calcDistance() << endl;		
	}

	// Calculate distances between points and insert them in output file
	fout << "\nDistances from each other :\n";
	for (int i=0; i<numPoints; i++) {
		
		fout << points1[i].calcDistance(points2[i]) << endl;
	}

	// Close our files to ensure we save our data
	fin.close();
	fout.close();

	return 0;
}