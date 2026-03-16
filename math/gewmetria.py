PI = 3.14159265359

#Συναρτηση που υπολογιζει το εμβαδόν τριγώνου

def triangle_area(base, height):
    return base*height/2


#Συναρτηση που υπολογιζει την περίμετρο τετραγώνου

def square_perimeter(edge):
    return 4*edge


#Συναρτηση που υπολογιζει το εμβαδόν τετραγώνου

def square_area(edge):
    return edge ** 2


#Συναρτηση που υπολογιζει την περίμετρο κύκλου

def circle_perimeter(radius):
    return 2*PI*radius


#Συναρτηση που υπολογιζει το εμβαδόν κύκλου

def circle_area(radius):
    return PI * radius ** 2


print(circle_area(1))