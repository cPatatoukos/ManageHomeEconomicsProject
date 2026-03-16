# This function takes a variable number of positional arguments (*args) and keyword arguments (**kwargs).
# It first prints the keyword arguments (kwargs) as a dictionary.
# Then, it calculates the average of the positional arguments (args) by summing them up and dividing by the number of arguments.
# Finally, it creates a new dictionary where the keys are the unique values from kwargs and the values are lists of keys from kwargs that have the same value, 
# and prints this new dictionary.
def print_details(*args, **kwargs):
    print(kwargs)
    s = 0
    for number in args:
        s += number
    average = s/len(args)
    print(average)

    dictionary = {}
    for key, value in kwargs.items():
        if value in dictionary:
            dictionary[value] += [key]
        else:
            dictionary[value] = [key]

    print(dictionary)



print_details(5,8,13,Banner="Discrete Mathematics", Kane="Discrete Mathematics", Stark="Programming")