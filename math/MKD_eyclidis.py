# Υλοποίηση του αλγορίθμου του Ευκλείδη για τον υπολογισμό του μέγιστου κοινού διαιρέτη (ΜΚΔ) δύο αριθμών.
def euclid(a,b):
    if a==b:
        return a
    elif a<b:
        return euclid(a,b-a)
    else: #a>b
        return euclid(a-b,b)


print(euclid(255,155))