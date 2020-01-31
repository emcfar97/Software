// Ethan McFarland
// 10/29/2018
// Lab 11

#include "Fraction.h"
#include <iostream>
#include <string>
using namespace std;

Fraction::Fraction() {
	numerator;
	denominator;
}

int Fraction::getGCD(int num1, int num2) {
	int remainder = num2 % num1;

	if (remainder != 0)
		return getGCD(remainder, num1);
	return num1;
}

void Fraction::reduce() {
    // Alter this function later to adjust for negative values
	int gcd = getGCD(numerator, denominator);
	numerator /= gcd;
	denominator /= gcd;

	if (denominator < 0) {
		numerator *= -1;
		denominator *= -1;
	}
}

int Fraction::getNum() {
	return this->numerator;
}

int Fraction::getDen() {
	return this->denominator;
}

const Fraction Fraction::operator+ (Fraction rhs) {
	Fraction sum;
	reduce();
	rhs.reduce();
	
	sum.numerator = numerator + rhs.numerator;
	sum.denominator = denominator + rhs.denominator;
	sum.reduce();

	return sum;
}

const Fraction Fraction::operator- (Fraction rhs) {
	Fraction diff;
	reduce();
	rhs.reduce();

	diff.numerator = numerator - rhs.numerator;
	diff.denominator = denominator - rhs.denominator;
	diff.reduce();

	return diff;
}

const Fraction Fraction::operator* (Fraction rhs) {
	Fraction prod;

	prod.numerator = numerator * rhs.numerator;
	prod.denominator = denominator * rhs.denominator;
	prod.reduce();

	return prod;
}

const Fraction Fraction::operator/ (Fraction rhs) {
	Fraction quot;

	quot.numerator = numerator * rhs.denominator;
	quot.denominator = denominator * rhs.numerator;
	quot.reduce();

	return quot;
}

bool Fraction::operator== (Fraction rhs) {

	if (rhs.numerator == rhs.denominator) {
		return true;
	}
	return false;
}

ostream& operator<< (ostream& output, const Fraction& fract) {

	output << fract.getNum << '/' << fract.getDen;

	return output;
}

istream& operator>> (istream& input, Fraction& fract) {
	
	char slash;

	input >> fract.numerator >> slash >> fract.denominator;

	return input;
}
