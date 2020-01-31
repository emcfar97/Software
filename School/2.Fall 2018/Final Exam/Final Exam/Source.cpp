// Ethan McFarland
// 12/03/2018
// Final Exam

#include "Employee.h"
#include <fstream>
#include <string>
#include <map>

int main() {
	// File I/O
	std::ifstream fin("input.txt");
	std::ofstream fout("output.txt");

	std::map<int, Employee> company;

	// Do the input and math
	std::string command, name;
	int ID, raise;

	while (fin >> command) {
		if (command == "NEW") {
			fin >> ID;
			fin.get();
			std::getline(fin, name);
			company[ID] = Employee(name);
		}
		else if (command == "RAISE") {
			fin >> ID >> raise;
			company[ID].giveRaise(raise);
		}
		else if (command == "PAY") {
			for (std::pair<int, Employee> ID : company) {
				company[ID.first].pay();
			}
		}
		else if (command == "FIRE") {
			fin >> ID;
			company[ID].fire();
		}
	}

	// Print output
	for (std::pair<int, Employee> ID : company) {
		fout << company[ID.first].getName() << ", ID Number " << ID.first << std::endl;
		if (company[ID.first].isEmployed() == true) {
			fout << "Current pay rate: $" << company[ID.first].getPayRate() << std::endl;
		}
		else {
			fout << "Not employed with the company." << std::endl;
		}
		fout << "Pay earned to date: $" << company[ID.first].getBalance() << std::endl;
		fout << std::endl;
	}

	// Close files
	fin.close();
	fout.close();
	return 0;
}
