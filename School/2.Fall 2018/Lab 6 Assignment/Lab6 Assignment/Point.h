#ifndef POINT_H
#define POINT_H

class Point
{
private:
	double x;
	double y;
	double z;

public:
	Point();
	Point(double inputX, double inputY, double inputZ);
	void setCoordinates(double x, double y, double z);
	double calcDistance();
	double calcDistance(Point other);
};

#endif