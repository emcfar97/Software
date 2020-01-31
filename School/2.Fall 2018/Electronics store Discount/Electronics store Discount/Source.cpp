#include <iostream>
#include <string>
#include <fstream>
#include <iomanip>
using namespace std;

void printCustomersData(const int id[], const string first[], const string last[], const double beforeDiscount[], int size) {
	
	cout << "Trans_ID  First     Last      Before Discount\n";
	for (int i=0; i<size; i++) {
		cout << left << setw(10) << id[i] << setw(10) << first[i] << setw(10) << last[i] << beforeDiscount[i] << endl;
	}
}

void printNames(const int id[], const string first[], const string last[], int size) {
		
	cout << "Trans_ID   First      Last\n";
	for (int i=0; i<size; i++) {
		cout << left << setw(11) << id[i] << setw(11) << first[i] << last[i] << endl;
	}
}

void printTotal(const int id[], const double beforeDiscount[], int size) {

	cout << "Trans_ID  Before Discount  After Discount\n";
	for (int i=0; i< size; i++) {
		cout << left << setw(10) << id[i] << setw(17) << beforeDiscount[i] << beforeDiscount[i] * 0.4 << endl;
	}
}

int main() {
	
	bool end = false;
	const int arraySize = 10;
	int ID[arraySize];
	string firstName[arraySize];
	string lastName[arraySize];
	double total[arraySize];
	int menuOp;
	
	ifstream fileIn;
	fileIn.open("input.txt");

	// Checks if file was opened correctly and sends input to appropriate arrays
	if (fileIn.fail() == false) {
		for (int i = 0; i < arraySize; i++) {
			fileIn >> ID[i] >> firstName[i] >> lastName[i] >> total[i];
		}
	}
	else {
		cout << "File did not open\n";
	}

	// Runs main loop, printing user menu, and takes user input
	while (end == false) {

		cout << "1. Print all customers data\n";
		cout << "2. Print names and Transaction ID\n";
		cout << "3. Print total before and after discount applied\n";
		cout << "4. Enter 4 to quit\n\n";
		cout << "Enter your choice or quit:  ";
		cin >> menuOp;
		
		if (cin.fail())	{
			cin.clear();
			cin.ignore(numeric_limits<streamsize>::max(), '\n');
			menuOp = 0;
		}

		switch (menuOp) {
			case 1:
				cout << endl;
				printCustomersData(ID, firstName, lastName, total, arraySize);
				cout << endl;
				continue;
			
			case 2:
				cout << endl;
				printNames(ID, firstName, lastName, arraySize);
				cout << endl;
				continue;
			
			case 3:
				cout << endl;
				printTotal(ID, total, arraySize);
				cout << endl;
				continue;
			
			case 4:
				cout << "Thanks for using my program. Goodbye!!";
				end = true;

			default:
				cout << endl;
				cout << "Wrong input. Try again...\n\n";
				continue;
		}
	}
	return 0;
}