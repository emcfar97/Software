// Ethan McFarland
// 10/29/2018
// Lab 11

#include <iostream>
using namespace std;

class Fraction {
private:
	int getGCD(int num1, int num2);
	int numerator;
	int denominator;

public:
	Fraction();
	void reduce();
	int getNum();
	int getDen();
	const Fraction operator+ (Fraction rhs);
	const Fraction operator- (Fraction rhs);
	const Fraction operator* (Fraction rhs);
	const Fraction operator/ (Fraction rhs);
	bool operator== (Fraction rhs);
	friend ostream& operator<< (ostream output, const Fraction& fract);
	friend istream& operator>> (istream input, const Fraction& fract);
};

/*
1/2 + 3/4	1/2 - 3/4	1/2 * 3/4	1/2 / 3/4
4/8 + 6/8	4/8 - 6/8	3/8			4/6
10/8		-2/8		3/8			4/6
*/