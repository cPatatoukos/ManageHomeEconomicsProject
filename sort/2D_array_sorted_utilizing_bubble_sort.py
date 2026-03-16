ar = [
    [1,4,7,2,5],
    [5,8,5,3,1],
    [2,4,7,8,1],
    [1,3,4,2,6],
    [1,7,4,2,1]
]


# Bubble Sort
def bubble_sort(array):
    n = len(array)
    for i in range(n):
        for j in range(n-1,i,-1):
            if array[j] < array[j-1]:
                array[j], array[j-1] = array[j-1], array[j]


# Sort by rows
# Η συνάρτηση sort_by_rows ταξινομεί κάθε γραμμή του πίνακα χρησιμοποιώντας τη συνάρτηση bubble_sort. 
# Για κάθε γραμμή στον πίνακα, καλεί τη συνάρτηση bubble_sort για να την ταξινομήσει.
def sort_by_rows(array):
    for row in array:
        bubble_sort(row)


# Sort by columns
# Η συνάρτηση sort_by_cols ταξινομεί κάθε στήλη του πίνακα χρησιμοποιώντας τη συνάρτηση bubble_sort.
# Για κάθε στήλη, δημιουργεί μια λίστα με τα στοιχεία της στήλης, την ταξινομεί με τη συνάρτηση bubble_sort 
# και στη συνέχεια ενημερώνει τα στοιχεία της στήλης στον αρχικό πίνακα με τα ταξινομημένα στοιχεία.
def sort_by_cols(array):
    for j in range(len(array)):
        col = [row[j] for row in array]
        bubble_sort(col)
        i = 0
        for row in array:
            row[j] = col[i]
            i += 1



sort_by_rows(ar)
sort_by_cols(ar)
print(ar)