#pragma once
#include "Products.h"

class Shirt :
	public Products
{
private:
	string size;
public:
	Shirt();
	void setSize(string inSize);
	friend std::ostream& operator<<(std::ostream& out, const Shirt& shirt);
	void calculateTotal();
};

