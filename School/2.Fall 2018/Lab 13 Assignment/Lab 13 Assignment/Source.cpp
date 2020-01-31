#include <iostream>
#include <fstream>
#include <string>
 
template <class myType>
myType swap(myType arr[100], int a, int b) {

	myType temp = arr[a];
	arr[a] = arr[b];
	arr[b] = temp;
}

template <class myType>
myType myMin(myType arr[100]) {

	myType min = arr[0];

	for (int i = 0; i < 100; i++) {
		if (min > arr[i]) {
			min = arr[i];
		}
	}

	return min;
}

template <class myType>
myType myMax(myType arr[100]) {

	myType max = arr[0];

	for (int i = 0; i < 100; i++) {
		if (max < arr[i]) {
			max = arr[i];
		}
	}

	return max;
}

template <class myType>
myType mySearch(myType arr[100], myType item, int start, int end) {

	if (end >= start) {
		int mid = start + (end - start) / 2;

		if (arr[mid] == item)
			if (typeid(myType) == typeid(int)) {
				return mid;
			}
			if (typeid(myType) == typeid(double)) {
				mid = (double) mid;
				return mid;
			}
			if (typeid(myType) == typeid(std::string)) {
				return mid;
			}

		if (arr[mid] > item)
			return mySearch(arr, item, start, mid--);

		return mySearch(arr, item, mid+start, end);
	}

	if (typeid(myType) == typeid(int)) {
		int NA = -1;
		return NA;
	}
	if (typeid(myType) == typeid(double)) {
		double NA = -1.0;
		return NA;
	}
	if (typeid(myType) == typeid(std::string)) {
		std::string NA = "-1";
		return NA;
	}
}

int main() {

	std::ifstream finInt("integers.txt");
	std::ifstream finDou("doubles.txt");
	std::ifstream finStr("strings.txt");
	std::ofstream fout("output.txt");

	int arrayInt[100];
	double arrayDou[100];
	std::string arrayStr[100];

	for (int i = 0; i < 100; i++) {
		finInt >> arrayInt[i];
		finDou >> arrayDou[i];
		finStr >> arrayStr[i];
	}
	
	// Get ouptut for integer input
	fout << "Integers:/nSwapped items at positions 10 and 20" << std::endl;
	fout << "Before: [10] " << arrayInt[10] << " [20] " << arrayInt[20] << swap<int>(arrayInt, 10, 20) << std::endl;
	fout << "After: [10] " << arrayInt[10] << " [20] " << arrayInt[20] << std::endl;
	fout << "Minimum: " << myMin<int>(arrayInt) << std::endl;
	fout << "Maximum: " << myMax<int>(arrayInt) << std::endl;
	fout << "The number 1 is at position " << mySearch<int>(arrayInt, 1, 0, 100) << std::endl;
	fout << "The number 5 is at position " << mySearch<int>(arrayInt, 5, 0, 100) << std::endl;

	// Get ouptut for double input
	fout << "Doubles:/nSwapped items at positions 10 and 20" << std::endl;
	fout << "Before: [10] " << arrayDou[10] << " [20] " << arrayDou[20] << swap<double>(arrayDou, 10, 20) << std::endl;
	fout << "After: [10] " << arrayDou[10] << " [20] " << arrayDou[20] << std::endl;
	fout << "Minimum: " << myMin<double>(arrayDou) << std::endl;
	fout << "Maximum: " << myMax<double>(arrayDou) << std::endl;
	fout << "The number 4.62557 is at position " << mySearch<double>(arrayDou, 4.62557, 0, 100) << std::endl;
	fout << "The number 1.23456 is at position " << mySearch<double>(arrayDou, 1.23456, 0, 100) << std::endl;

	// Get ouptut for string input
	fout << "Strings:/nSwapped items at positions 10 and 20" << std::endl;
	fout << "Before: [10] " << arrayStr[10] << " [20] " << arrayStr[20] << swap<std::string>(arrayStr, 10, 20) << std::endl;
	fout << "After: [10] " << arrayStr[10] << " [20] " << arrayStr[20] << std::endl;
	fout << "Minimum: " << myMin<std::string>(arrayStr) << std::endl;
	fout << "Maximum: " << myMax<std::string>(arrayStr) << std::endl;
	fout << "The word Shoes is at position " << mySearch<std::string>(arrayStr, "Shoes", 0, 100) << std::endl;
	fout << "The word Pumpkin is at position " << mySearch<std::string>(arrayStr, "Pumpkin", 0, 100) << std::endl;
	
	finInt.close();
	finDou.close();
	finStr.close();
	fout.close();

	return 0;
}