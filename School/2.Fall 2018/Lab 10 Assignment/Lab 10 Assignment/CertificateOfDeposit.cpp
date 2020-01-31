//#include "Account.h"
#include "CertificateOfDeposit.h"

// Constructor
CertificateOfDeposit::CertificateOfDeposit(int newAccountNum) {
	hasWithdrawn = false;
}

// Applies an interest rate to the balance
void CertificateOfDeposit::accrueInterest() {
	if (hasWithdrawn == false) {
		balance *= 1.1;
	}
	else {
		balance *= 1.01;
	}
}
// Removes money from the bank account
void CertificateOfDeposit::withdrawal(float amount) {
	balance -= amount;
	hasWithdrawn = true;
}
