// Ethan McFarland
// 10/15/2018
// Lab #9

#ifndef LIBRARYBOOK_H
#define LIBRARYBOOK_H

#include <string>

class LibraryBook
{
private:
	std::string title;
	std::string author;
	std::string ISBN;
	bool checkedOut;

public:
	LibraryBook();
	void setBook(std::string title, std::string author, std::string ISBN);
	std::string getTitle();
	std::string getAuthor();
	std::string getISBN();
	bool getCheckOut();
	void changeCheck();
};
#endif