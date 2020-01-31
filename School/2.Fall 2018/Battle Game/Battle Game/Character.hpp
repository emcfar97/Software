#pragma once
#include <string>
using namespace std;

class Character
{
protected:
	string m_name = " ";
	int m_hp = -1;
	int m_atk = -1;
	int m_def = -1;
	enum AttackType {
		OFFENSIVE = 1,
		DEFENSIVE = 2
	} m_attackType;

public:
	Character();
	void Setup(const string& name, int hp, int atk, int def);
	void DisplayStats();
	void SelectAction();
	int GetAttack();
	void GetHit(int attack);
	int GetHP();
};

