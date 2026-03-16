# Συναρτηση που ζηταει απο τον χρηστη να δωσει ενα ακεραιο αριθμο και επαναλαμβανει το αιτημα μεχρι να δωθει ενας ακεραιος αριθμος

def input_integer():
    while True:
        data = input("Give an integer: ").strip()
        if data.isdigit():
            return int(data)
        else:
            print("Only digits please. ")

print(input_integer())

# Συναρτηση που ζηταει απο τον χρηστη να δωσει ενα πραγματικο αριθμο και επαναλαμβανει το αιτημα μεχρι να δωθει ενας πραγματικος αριθμος

def input_float():
    while True:
        data = input("Give an float: ").strip()
        if "." in data:
            parts = data.split(".")
            if len(parts) > 2:
                print("Only one dot at most please.")
            elif parts[0].isdigit() and parts[1].isdigit():
                return float(data)
            else:
                print("Only digits please.")
        else: # . not in data
            if data.isdigit():
                return float(data)
            else:
                print("Only digits please. ")


print(input_float())

#Συναρτηση που ελεγχει αν ενας αριθμος ειναι περιττος

def is_odd(number):
    return number % 2 == 1

#Συναρτηση που ελεγχει αν ενας αριθμος ειναι ζυγος

def is_even(number):
    return number % 2 == 0

#Συναρτηση που ελεγχει αν ενας αριθμος ειναι πρωτος

def is_prime(number):
    if number == 0 or number == 1:
        return False
    for i in range(2, int(number / 2) + 1):
        if number % i == 0:
            return False
    return True

#Συναρτηση που ελεγχει αν ενας αριθμος ειναι τετραγωνο ή κύβος άλλου αριθμού

def is_square(number):
    i = 0
    sq = 0
    while sq < number:
        i += 1
        sq = i * i

    return sq == number


def is_cube(number):
    i = 0
    cub = 0
    while cub < number:
        i += 1
        cub = i ** 3

    return cub == number


for i in range(1, 100 + 1):
    print(f"{i}: ", end="")
    if is_odd(i):
        print("odd", end=" ")
    if is_even(i):
        print("even", end=" ")
    if is_prime(i):
        print("prime", end=" ")
    if is_square(i):
        print("square", end=" ")
    if is_cube(i):
        print("cube", end=" ")
    print("")