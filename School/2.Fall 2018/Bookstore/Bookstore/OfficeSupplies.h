#pragma once
#include "Products.h"

class OfficeSupplies :
	public Products
{
private:
	int count;
public:
	OfficeSupplies();
	void setCount(int inCount);
	friend std::ostream& operator<<(std::ostream& out, const OfficeSupplies& supplies);
};

