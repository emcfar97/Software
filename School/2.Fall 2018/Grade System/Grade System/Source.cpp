/*
COMP-SCI 201R
Program #1
Ethan McFarland
*/

#include <iostream>
using namespace std;

int main() {
	int menuOp;
	int assign;
	int exam1;
	int exam2;
	int final;
	int dividend = 0;
	int divisor = 0;
	int total;
	char grade;

	while (true)
	{// Main loop body
		cout << "Welcome to Grade system:\n";
		cout << "How can we help you today?\n";
		cout << "1. Grade Scale.\n";
		cout << "2. Calculate your total % and Grade.\n";
		cout << "3. Exit\n";
		cin >> menuOp;

		if (menuOp == 1)
		{// Displays grade scale
			cout << "A: 90-100\n";
			cout << "B: 80-89\n";
			cout << "C: 69-79\n";
			cout << "D: 60-68\n";
			cout << "F: 0-59\n\n";
			continue;
		}

		else if (menuOp == 2)
		{// Retrieves input from user, the calculates total score and grade 
			cout << "Please let us know your points in assignments, Exam1, Exam2, and Final Exam\n";

			cout << "Assignments out of 80:\n";
			cin >> assign;
			cout << "Exam1 out of 80:\n";
			cin >> exam1;			
			cout << "Exam2 out of 80:\n";
			cin >> exam2;			
			cout << "Final Exam out of 100:\n";
			cin >> final;
			
			dividend += 80 * assign;
			divisor += 80;
			dividend += 80 * exam1;
			divisor += 80;
			dividend += 80 * exam2;
			divisor += 80;
			dividend += 100 * final;
			divisor += 100;

			total = dividend/divisor;

			if (90 <= total && total <= 100) {
				grade = 'A';
			}
			else if (80 <= total && total <= 89) {
				grade = 'B';
			}
			else if (69 <= total && total <= 79) {
				grade = 'C';
			}
			else if (60 <= total && total <= 68) {
				grade = 'D';
			}
			else {
				grade = 'F';
			}

			cout << "Your total grade percentage is " << total << endl;
			cout << "Depending on Grade scale, your Grade is \n";
			cout << grade << endl << endl;

			continue;
		}

		else if (menuOp == 3)
		{// Terminates program
			break;
		}

		else
		{// Validates user input
			cout << "Please enter a number from 1 to 3\n\n";
			continue;
		}
	}
	return 0;
}
