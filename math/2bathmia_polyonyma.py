# Factory Function for Quadratic Polynomials
# Η συνάρτηση factory δημιουργεί και επιστρέφει μια νέα συνάρτηση που υπολογίζει την τιμή ενός πολυωνύμου δεύτερου βαθμού (quadratic polynomial) με συντελεστές a, b, και c.
# Η συνάρτηση που επιστρέφεται δέχεται μια μεταβλητή x και υπολογίζει την τιμή του πολυωνύμου χρησιμοποιώντας τον τύπο: a*x^2 + b*x + c.
def factory(a,b,c):
    def polynomial(x):
        return a*x**2 + b*x + c

    return polynomial


pol = factory(1,1,1)
print(pol(1))