#include <fstream>
#include <iostream>
#include <iomanip>
#include <string>
#include "Products.h"
#include "OfficeSupplies.h"
#include "Shirt.h"
#include "Register.h"
using namespace std;

int main() {

	ifstream fin("products.txt");
	ofstream fout("output.txt");

	Register store();
	string type;
	string descript;
	string size;
	int count;
	int quantity;
	double price;
	string next;

	while (!fin.eof()) {
		getline(fin, type);
		getline(fin, descript);
		if (type == "SHIRT") {
			Shirt* shirt;
			shirt = new Shirt();
			fin >> size >> quantity >> price;
			shirt->setDescrip(descript);
			shirt->setSize(size);
			shirt->setQuant(quantity);
			shirt->setPrice(price);
		}
		else {
			OfficeSupplies* supply;
			supply = new OfficeSupplies();
			fin >> count >> quantity >> price;
			supply->setDescrip(descript);
			supply->setCount(count);
			supply->setQuant(quantity);
			supply->setPrice(price);
		}		
		getline(fin, next);
		getline(fin, next);
	}

	fout << setfill('*') << setw(40) << '*' << endl;
	fout << "*            UMKC Bookstore            *\n";
	fout << setfill('*') << setw(40) << '*' << endl;
	fout << "\nQty Description                 Total\n";
	fout << "--- --------------------------- --------";
	/*
	for (int i = 0; i<=4 ; i++) {
		fout << "  " << i+1 << store[i];
	}
	*/
	fout << "Grand total: $" << endl;
	fout << "Items sold: " << endl;
	fout << "* Thank you for shopping at our store! *";

	fin.close();
	fout.close();
	system("pause");
	return 0;
}