# This function calculates the average of a list of floating point numbers.
# The function takes a variable number of arguments (using *numbers) and sums them up.
# Finally, it divides the sum by the number of arguments to get the average and returns it.
def float_average(*numbers):
    s = 0
    for number in numbers:
        s += number
    return s/len(numbers)


print(float_average(2.1,4.2,5.9,7.8))