double find3Min(Double_t x1, Double_t x2, Double_t x3)
{
    return x1*(x1<x2 && x1<x3) + x2*(x2<x1 && x2<x3) + x3*(x3<x1 && x3<x2);
}