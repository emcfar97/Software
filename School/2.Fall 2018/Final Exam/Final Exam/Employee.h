#ifndef EMPLOYEE_H
#define EMPLOYEE_H
#include <string>

class Employee
{
private:
	std::string name;
	double balance;
	double payRate;
	bool employed;
public:
	Employee(std::string myName = "");
	double getPayRate();
	double getBalance();
	std::string getName();
	void giveRaise(int rate);
	void pay();
	void fire();
	bool isEmployed();
};
#endif