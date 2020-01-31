#pragma once
#include <string>
using namespace std;

class Products
{
private:
	double price;
	int quantity;
	string description;
public:
	Products();
	Products(int inPrice, int inQuantity);
	void setPrice(double inPrice);
	void setQuant(int inQuant);
	void setDescrip(string inDescr);
	virtual friend std::ostream& operator<<(std::ostream& out, const Products& products) = 0;
	virtual void calculateTotal();
};

