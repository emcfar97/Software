// Ethan McFarland
// 9/10/2018
// CS201L Lab #4

#include <iostream>
#include <cmath>
using namespace std;

float cash = 10000;

float withdraw() {

	// Retrieves withdrawal amount and returns cash minus withdrawal
	::cash;
	float withdrawal;
	char check;

	while(true) {

		cout << "Enter withdrawal amount: ";
		cin >> withdrawal;

		if (withdrawal > cash) {

			cout << "That amount is greater than your current balance.\n";
			continue;
		}
		
		else {
			
			cout << "Are you sure you want to withdraw that amount?\nY or N\n";
			cin >> check;

			if (check == 'Y') {

				cout << cash << " - " << withdrawal << " = " << cash - withdrawal << endl;
				cash -= withdrawal;

			}
			break;
		}

	return cash;
	}
}

float deposit() {

	// Retrieves deposit amount and returns cass plus deposit
	:: cash;
	float deposit;
	char check;

	cout << "Enter deposit amount: ";
	cin >> deposit;

	cout << "Are you sure you want to deposit that amount?\nY or N\n";
	cin >> check;

	if (check == 'Y') {

		cash += deposit;
	
	}


	return cash;
}

double score(int &credit_score, double &interest_rate) {
	
	/* Calculates interest rate, retrieves period, then 
	returns resulting interest*/
	float loan;
	int months;
	double A;

	if (501 < credit_score && credit_score < 700) {
		interest_rate = .02;
	}
	
	else if (credit_score <= 500) {
		interest_rate = .05;
	}

	else {
		interest_rate = .01;
	}

	cout << "Enter the loan amount: ";
	cin >> loan;

	cout << "How long is the time period? (Enter in months): ";
	cin >> months;

	A = (loan * (1 + pow(interest_rate, (months / 12)) )) / months;
	return A;

}

int main() {

	double interest_rate;
	int credit_score;
	int menuOp;
	
	// Displays menu options to user
	while (true) {

		cout << "1. Withdraw amount\n";
		cout << "2. Deposit amount\n";
		cout << "3. Credit score\n";
		cout << "4. Exit\n";
		cin >> menuOp;

		// Withdraws user-specified amount from balance
		if (menuOp == 1) {

			cout << "You now have $" << withdraw() << ".\n\n";
			continue;
		}

		// Deposits user-specified amount to balance
		else if (menuOp == 2) {

			cout << "You now have $" << deposit() << ".\n\n";
			continue;
		}

		// Returns user's amount of interest
		else if (menuOp == 3) {

			cout << "Enter credit score: ";
			cin >> credit_score;

			cout << "Interest is $" << score(credit_score, interest_rate)<< ".\n\n";
			continue;
		}

		// Terminates program
		else if (menuOp == 4) {

			break;
		}

		// Reports an error and returns to menu options
		else {
			cout << "There was an error.\n\n";
			continue;
		}
	}

	return 0;
}