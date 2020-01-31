#include <iostream>
#include "Products.h"
#include "OfficeSupplies.h"

OfficeSupplies::OfficeSupplies() {

}
void OfficeSupplies::setCount(int inCount) {
	count = inCount;
}
std::ostream& operator<<(std::ostream& out, const OfficeSupplies& supplies) {
	out << description << " (" << supplies.count << " count)";
}