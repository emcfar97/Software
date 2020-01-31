#include <cmath>
#include "Point.h"

Point::Point() 
{
	x = 0.0;
	y = 0.0;
	z = 0.0;
}

void Point::setCoordinates(double inputX, double inputY, double inputZ)
{
	x = inputX;
	y = inputY;
	z = inputZ;
}

double Point::calcDistance() 
{
	return sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
}

double Point::calcDistance(Point other)
{
	return sqrt(pow(x - other.x, 2) + pow(y - other.y, 2) + pow(z - other.z, 2));
}
