#include "Register.h"


Register::Register() {

}
void Register::addProduct(Products product) {
	register[numProducts] = product;
	numProducts++;
}
void Register::printReceipt() {
	
	for (int i = 0; i <= numProducts; i++) {

		fout << "  " << i + 1 << registery[i];
	}
}