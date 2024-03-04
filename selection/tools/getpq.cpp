double getpq(Double_t mm, Double_t m1, Double_t m2)
{
	return sqrt((mm*mm-(m1+m2)*(m1+m2))*(mm*mm-(m1-m2)*(m1-m2))/(4*mm*mm));
}
