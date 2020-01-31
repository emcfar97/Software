#include <iostream>
#include <fstream>
#include <string>
using namespace std;

void main()
{
	string STRING;
	ifstream infile;
	infile.open("input.txt");
	while (!infile.eof) // To get you all the lines.
	{
		getline(infile, STRING); // Saves the line in STRING.
		cout << STRING; // Prints our STRING.
	}
	infile.close();
	system("pause");
}