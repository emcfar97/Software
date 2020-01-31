#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
using namespace std;

void PrintOneMonth(int MonthNumber, int Year, int& StartDayNumber) {

    vector<string> months = {
        "JANUARY", "FEBRUARY", "MARCH",
        "APRIL", "MAY", "JUNE",
        "JULY", "AUGUST", "SEPTEMBER",
        "OCTOBER", "NOVEMBER", "DECEMBER"
        };
    
    string month = months.at(MonthNumber);
    vector<int> monthDays = DaysPerMonth(Year);
    int spacing = StartDayNumber%7 * 8 + 1;
    int end;
    
    if (StartDayNumber%7 < 3) {
        end = 2-StartDayNumber%7;
        }
    else {
        end = 9-StartDayNumber%7;
        }
    
    //Prints month and week headings
    cout << setw(23 + month.size()/2) << month << ' ' << Year << endl;
    cout << "Sun     Mon     Tue     Wed     Thu     Fri     Sat";

    for (int i=1; i<=monthDays.at(MonthNumber); i++) {
        StartDayNumber++;
        
        if (i == 1) {// Determines where first line starts
            cout << endl << setw(spacing) << i;
        }
        else if ((i+StartDayNumber) % 7 == end) {// Determines where first line ends
            cout << setw(0) << endl;
            cout << i << setw(8);
        }
        else {// Fills out rest of month's days
            cout << setw(8) << i;
        }
    }
    cout << endl << endl;
}

vector<int> DaysPerMonth(int Year) {

    vector<int> monthDays = {31,28,31,30,31,30,31,31,30,31,30,31};

    if (Year%4 == 0) {
        
        monthDays.at(1) = 29;
    }
    return monthDays;
}

int GetStartDayNumber() {
    
    int day;

	cout << "What day of the week does Jan 1 fall on this year? (Sun = 0) ";
	cin >> day;

    while (0 > day || day >= 7) {        
        cout << "What day of the week does Jan 1 fall on this year? (Sun = 0) ";
        cin >> day;
    }
    return day;
}

int GetYear() {

    int year;
    
    cout << "Enter year (must be in range 1000 <= Year <= 9999): ";
    cin >> year;
    
    while (1000 > year || year > 9999) {
        cout << "Enter year (must be in range 1000 <= Year <= 9999): ";
        cin >> year;
    }
    return year;
}

int main() {

    int year = GetYear();
    int startDay = GetStartDayNumber();

    for (int month=0; month<12; month++) {
        PrintOneMonth(month, year, startDay);
    }

	return 0;
}
