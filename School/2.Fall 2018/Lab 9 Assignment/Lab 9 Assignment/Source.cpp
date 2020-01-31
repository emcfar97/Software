// Ethan McFarland
// 10/15/2018
// Lab #9

#include "LibraryBook.h"
#include <fstream>
#include <iostream>
#include <string>

int main() {
	// File stream variables
	std::ifstream finBooks("books.txt");
	std::ifstream finISBN("isbns.txt");
	std::ofstream fout("checkedout.txt");

	std::string title;
	std::string author;
	std::string ISBN;
	LibraryBook library[30];
	int num = 0;

	// Check for file errors first
	if (!finBooks || !finISBN)
	{
		std::cout << "Error opening input files!\n";
		system("pause");
		return 1;
	}
	// Input data from file into ilbrary of books
	while (!finBooks.eof()) {

		getline(finBooks, title);
		getline(finBooks, author);
		getline(finBooks, ISBN);
		library[num].setBook(title, author, ISBN);
		num++;
	}
	// Determine checkout status of books in library
	while (!finISBN.eof()) {

		getline(finISBN, ISBN);
		for (int i = 0; i < 30; i++) {
			if (ISBN == library[i].getISBN()) {
				library[i].changeCheck();
			}
		}
	}
	// Output boks that are cheked out to file
	fout << "Books checked out:\n";
	fout << "------------------\n";
	fout << "Title		Author     ISBN\n";

	for (int i = 0; i < 30; i++) {

		LibraryBook book = library[i];
		if (book.getCheckOut() == true) {
			fout << book.getTitle() << '	' << book.getAuthor() << '	' << book.getISBN() << std::endl;
		}
	}
	// Close the files at the end
	finBooks.close();
	finISBN.close();
	fout.close();

	// End program
	return 0;
}
