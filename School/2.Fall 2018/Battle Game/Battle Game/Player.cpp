#include <iostream>
#include "Player.hpp"
using namespace std;

Player::Player() {

}
void Player::SelectAction() {

	int choice;
	cout << "Enter 1 for offensive or 2 for defensive: ";
	cin >> choice;
	
	while (choice != 1 || choice != 2) {
		cout << "Enter 1 for offensive or 2 for defensive: ";
		cin >> choice;

		if (cin.fail()) {
			cin.clear();
			cin.ignore(numeric_limits<streamsize>::max(), '\n');
			choice = 0;
		}
	}
	if (choice == 1) {
		m_attackType = OFFENSIVE;
	}
	else {
		m_attackType = DEFENSIVE;
}
}
