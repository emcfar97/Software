#include <iostream>
#include <iomanip>
#include "Utils.hpp"
#include "Character.hpp"
#include "Player.hpp"
#include "Enemy.hpp"
using namespace std;

void SetupCharacters(Character& player, Character& enemy) {

	string name;
	int choice;
	bool end = false;

	cout << "Enter name of character: ";
	cin >> name;

	while (end == false) {
		cout << "\nChoose : \n";
		cout << "Option    Attack    Defense\n";
		cout << setw(3) << 1 << setw(11) << 5 << setw(10) << 15 << endl;
		cout << setw(3) << 2 << setw(11) << 15 << setw(10) << 5 << endl;
		cout << setw(3) << 3 << setw(11) << 10 << setw(10) << 10 << endl;
		cin >> choice;

		if (cin.fail()) {
			cin.clear();
			cin.ignore(numeric_limits<streamsize>::max(), '\n');
			choice = 0;
		}
		switch (choice) {
			case 1:
				player.Setup(name, 100, 5, 15);
				enemy.Setup("Enemy", 100, GetRandom(6, 4), GetRandom(14, 16));
				break;
			case 2:
				player.Setup(name, 100, 15, 5);
				enemy.Setup("Enemy", 100, GetRandom(16, 14), GetRandom(6, 4));
				break;
			case 3:
				player.Setup(name, 100, 10, 10);
				enemy.Setup("Enemy", 100, GetRandom(11, 9), GetRandom(11, 9));
				break;
			default:
				cout << "\nWrong input. Try again...\n\n";
				continue;
		}
		end = true;
	}
}
int main() {

	Player player;
	Enemy enemy;

	while (true) {
		char choice;

		SetupCharacters(player, enemy);
		player.DisplayStats();
		cout << endl;
		enemy.DisplayStats();

		cout << "\nIs this okay?\n";
		cout << "Enter 'y' or 'n'\n";
		cin >> choice;

		if (choice == 'y' || choice == 'Y') {
			break;
		}
		else {
			continue;
		}
	}
	while (true) {
		int round = 1;

		cout << "\nRound " << round << endl;

		player.SelectAction();
		enemy.SelectAction();

		player.GetHit(enemy.GetAttack());
		enemy.GetHit(player.GetAttack());

		if (player.GetHP() == 0) {
			cout << "You Lose";
			break;
		}
		else if (enemy.GetHP() == 0) {
			cout << "You Win";
			break;
		}
		round++;
	}
	return 1;
}