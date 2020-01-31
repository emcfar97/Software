#include <iostream>
#include <iomanip>
#include "Utils.hpp"
#include "Character.hpp"
using namespace std;

Character::Character(){

}
void Character::Setup(const string& name, int hp, int atk, int def) {
	
	m_name = name;
	m_hp = hp;
	m_atk = atk;
	m_def = def;
}
void Character::DisplayStats() {

	cout << right << "Name: " << m_name << endl;
	cout << "Hp: " << setw(3) << m_hp << " pts\n";
	cout << "Atk: " << setw(3) << m_atk << " pts\n";
	cout << "Def: " << setw(3) << m_def << " pts\n";
}
void Character::SelectAction() {

}
int Character::GetAttack() {

	if (m_attackType == OFFENSIVE) {
		return m_atk + GetRandom(3, 1);
	}
	return m_atk;
	cout << m_name << endl;
}
void Character::GetHit(int attack) {
	
	if (m_attackType == 1) {
		m_hp -= attack - m_def;
	}
	else {
		if (attack >= 0) {
			m_hp -= attack - m_def - GetRandom(3, 1);
		}
	}
}
int Character::GetHP() {

	return m_hp;
}