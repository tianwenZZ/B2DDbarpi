double find4Min(Double_t x1, Double_t x2, Double_t x3, Double_t x4)
{
    return x1*(x1<x2 && x1<x3 && x1<x4) + x2*(x2<x1 && x2<x3 && x2<x4) + x3*(x3<x1 && x3<x2 && x3<x4) + x4*(x4<x1 && x4<x2 && x4<x3);
}