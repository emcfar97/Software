// Ethan McFarland
// 10/15/2018
// Lab #9

#include "LibraryBook.h"
#include <string>

void LibraryBook::setBook(std::string title, std::string author, std::string ISBN) {
	title = title;
	author = author;
	ISBN = ISBN;
	checkedOut = false;
}

std::string LibraryBook::getTitle() {
	return title;
}

std::string LibraryBook::getAuthor() {
	return author;
}

std::string LibraryBook::getISBN() {
	return ISBN;
}

bool LibraryBook::getCheckOut() {
	return checkedOut;
}

void LibraryBook::changeCheck() {
	checkedOut = !checkedOut;
}