#include <iostream>
#include "Products.h"
#include "Shirt.h"

Shirt::Shirt() {

}
void Shirt::setSize(string inSize) {
	size = inSize;
}
std::ostream& operator<<(std::ostream& out, const Shirt& shirt) {
	out << shirt.size << ' ' << shirt.description;
}
void Shirt::calculateTotal() {

}