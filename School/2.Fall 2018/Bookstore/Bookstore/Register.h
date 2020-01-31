#pragma once
#include "Products.h"

class Register
{
private:
	Products* registery = NULL;
	int numProducts = 0;
public:
	Register();
	void addProduct(Products product);
	void printReceipt();
};

