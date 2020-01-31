// Ethan McFarland
// 10/22/2018
// Lab 10

#include "Account.h"
#include "CertificateOfDeposit.h"
#include "CheckingAccount.h"
#include "SavingsAccount.h"
#include <fstream>
#include <string>
using namespace std;

int main() {
	// File I/O
	ifstream fin("input.txt");
	ofstream fout("output.txt");

	// Stores up to 30 accounts & Number of accounts that have been opened
	Account* accounts[120];
	int numAccounts = 0;
	int accountNums[8] = {100,101,102,103,104,105,106,107};

	// For file input processing
	string command, acctType;
	int acctNum1, acctNum2;
	double amount;

	// Do the input and math
	while(fin >> command) 	{
		if (command == "NEW") {
			Account *newAccount;
			fin >> acctType ;

			if (acctType == "CHECKING") {
				fin >> acctNum1;
				newAccount = new SavingsAccount(0.0);
				accounts[acctNum1] = newAccount;
			}
			else if (acctType == "SAVINGS") {
				fin >> acctNum1;
				newAccount = new CheckingAccount(0.0);
				accounts[acctNum1] = newAccount;
			}
			else if (acctType == "CERTIFICATE") {
				fin >> acctNum1;
				newAccount = new CertificateOfDeposit(0.0);
				accounts[acctNum1] = newAccount;
			}
			numAccounts++;
        }
		else if (command == "WITHDRAWAL") {
			fin >> acctNum1 >> amount;
			accounts[acctNum1]->withdrawal(amount);
        }
		else if (command == "DEPOSIT") {
			fin >> acctNum1 >> amount;
			accounts[acctNum1]->deposit(amount);
		}
		else if (command == "TRANSFER") {
			fin >> acctNum1 >> acctNum2 >> amount;
			accounts[acctNum1]->withdrawal(amount);
			accounts[acctNum2]->deposit(amount);
        }
		else if (command == "INTEREST") {
			for (int i = 100; i < numAccounts; i++) {
				accounts[accountNums[i]]->accrueInterest();
			}
        }
    }	
	// Print output
	fout << "BANK STATEMENT" << endl << endl;
	for(int i = 0; i < numAccounts; i++) {
		fout << "Account number: " << accounts[i]->getAccountNum() << endl;
		fout << "Type of account: " << accounts[i]->getAccountType() << endl;
		fout << "Balance: $" << accounts[i]->getBalance() << endl;
		fout << endl;
	}     
	// Delete accounts
	for (int i = 0; i < numAccounts; i++)
		delete accounts[i];

    // Close files
    fin.close();
    fout.close();
    return 0;
}