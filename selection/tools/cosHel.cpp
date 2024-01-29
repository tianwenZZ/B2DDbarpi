double cosHel(TLorentzVector v1, TLorentzVector v2, TLorentzVector vBachelor) {
    // v1 is the direction which the helicity angle is with respect to
    TVector3 bst_CM12 = -(v1+v2).BoostVector();
    v1.Boost(bst_CM12);
    v2.Boost(bst_CM12);
    vBachelor.Boost(bst_CM12);
    TVector3 unit_vBachelor = vBachelor.Vect().Unit();
    TVector3 unit_v1 = v1.Vect().Unit();
    double coshel12 = unit_vBachelor.Dot(unit_v1);
    return coshel12;

}
