# Selection Sort with Reverse Option
# Ο αλγόριθμος ταξινόμησης επιλογής (Selection Sort) αλλά με την προσθήκη της δυνατότητας ταξινόμησης σε φθίνουσα σειρά. 
# Αν η παράμετρος reverse είναι True, ο αλγόριθμος θα ταξινομήσει τα στοιχεία σε φθίνουσα σειρά, διαφορετικά θα τα ταξινομήσει σε αύξουσα σειρά.
def selection_sort(array, reverse=False):
    if reverse:
        for i in range(0, len(array)):
            pos = i
            for j in range(i+1, len(array)):
                if array[j] > array[pos]:
                    pos = j
            array[i], array[pos] = array[pos], array[i]
    else:
        for i in range(0, len(array)):
            pos = i
            for j in range(i + 1, len(array)):
                if array[j] < array[pos]:
                    pos = j
            array[i], array[pos] = array[pos], array[i]


array = [1, 5, 2 , 8, 4, 7, 3, 9, 6]
selection_sort(array, reverse=True)
print(array)