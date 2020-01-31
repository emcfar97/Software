#include "Enemy.hpp"

Enemy::Enemy() {

}
void Enemy::SelectAction() {

	if (1/*GetRandom(2, 1)*/ == 1) {
		m_attackType = OFFENSIVE;
	}
	else {
		m_attackType = DEFENSIVE;
	}
}
