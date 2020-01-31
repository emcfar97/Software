#include "Employee.h"

Employee::Employee(std::string myName)
{
	name = myName;
	balance = 0.0;
	payRate = 10.0;
	employed = true;
}

double Employee::getPayRate()
{
	return payRate;
}

double Employee::getBalance()
{
	return balance;
}

std::string Employee::getName()
{
	return name;
}

void Employee::giveRaise(int rate)
{
	payRate += payRate * (rate * .01);
}

void Employee::pay()
{
	balance += payRate;
}

void Employee::fire()
{
	employed = false;
	payRate = 0.0;
}

bool Employee::isEmployed()
{
	return employed;
}