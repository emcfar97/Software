#include <iostream>

int RHS(int n) {

	if (n == 1)
		return 1;

	else
		return RHS(n - 1) + n * n;
}

int LHS(int n) {

	int sum = 0;
	while (n != 0) {
		sum += n * n;
		n -= 1;
	}
	return sum;
}

void reverse(int arr[], int start, int end) {

	if (start >= end) {
		int temp = arr[start];
		arr[start] = arr[end];
		arr[end] = temp;
	}
	reverse(arr, start++, end--);
}

int main() {
	char choice = 'y';
	int num;
		
	std::cout << "a.";
	while (choice != 'n') {
		
		std::cout << "\nEnter number: ";
		std::cin >> num;
		std::cout << "Non-recursive Q(" << num << ") == Recursive Q(" << num << ")?\n";

		if (LHS(num) == RHS(num) == true) {
			std::cout << "True\n";
		}
		else {
			std::cout << "False\n";
		}
		
		std::cout << "Continue?" << std::endl << "Enter 'n' if no, else any key.\n";
		std::cin >> choice;

		if (choice == 'n')
			break;
	}
	
	const int size = 5; 
	int a[size];
	
	std::cout << "b.";
	for (int i = 0; i < size;i++) {
		std::cout << "\nEnter 5 numbers: ";
		std::cin >> a[i];
	}

	for (int i = 0; i < size; i++) {
		std::cout << a[i];
	}

	reverse(a, 0, sizeof(a));
	
	for (int i = 0; i < size; i++) {
		std::cout << a[i];
	}

	return 0;
}