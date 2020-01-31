#pragma once
class Utils
{
public:
	Utils();
	int GetUserInput(int max, int min);
	int GetRandom(int max, int min);
};

#include <iostream>
#include <cstdlib>
#include <ctime>
#include "Utils.hpp"
using namespace std;

Utils::Utils() {

}
int Utils::GetUserInput(int max, int min) {

	int integer;
	cout << "Enter integer";
	cin >> integer;

	while (min > integer || integer > max) {
		cout << "Integer must be between " << min << " and " << max << endl;
		cout << "Enter integer:  ";
		cin >> integer;
	}
	return integer;
}
int GetRandom(int max, int min) {

	srand(static_cast<unsigned int>(time(NULL)));

	return rand() % (max - min + 1) + min;
}