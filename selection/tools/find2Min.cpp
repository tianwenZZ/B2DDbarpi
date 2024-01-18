double find2Min(Double_t x1, Double_t x2)
{
    return x1*(x1<x2)+x2*(x2<x1);
}