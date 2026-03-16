# Υπολογισμός παραγοντικού ενός αριθμού με αναδρομή

def factorial_recursive(n):
    if n == 0:
        return 1
    else:
        return n * factorial_recursive(n-1)


# Υπολογισμός παραγοντικού ενός αριθμού με επανάληψη

def factorial(n):
    p = 1
    for i in range(2, n+1):
        p = p * i

    return p

for i in range(2, 50):
    print(factorial(i))
    print(factorial_recursive(i))
