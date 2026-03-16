# Quick Sort
# Quick Sort is a divide-and-conquer algorithm. 
# It works by selecting a 'pivot' element from the array and partitioning the other elements into two sub-arrays, according to whether they are less than or greater than the pivot. 
# The sub-arrays are then sorted recursively.
# ο χρονος εκτέλεσης του Quick Sort είναι O(n log n) κατά μέσο όρο, αλλά μπορεί να φτάσει O(n^2) στην χειρότερη περίπτωση, 
# όταν το pivot επιλέγεται με κακό τρόπο (π.χ. όταν το array είναι ήδη ταξινομημένο).
from random import randrange

def quick_sort(array):
    def partition(array, start, finish):                                                # The partition function takes the last element as pivot,
        pivot = array[start]                                                            # places the pivot element at its correct position in sorted array,
                                                                                        # and places all smaller (smaller than pivot) to left of pivot and all greater elements to right of pivot
        less = [elem for elem in array[start+1:finish+1] if elem < pivot]
        greaterequal = [elem for elem in array[start+1:finish + 1] if elem >= pivot]
        new_array = less + [pivot] + greaterequal

        for i in range(start, finish+1):
            array[i]=new_array.pop(0)                                                   # Update the original array with the new order after partitioning

        return start + len(less)

    def quick_sort_rec(array, start, finish):                                           # The quick_sort_rec function is a recursive function that implements the quick sort algorithm.
        if start < finish:
            pos = partition(array,start,finish)                                         # The partition function is called to partition the array and return the index of the pivot element after partitioning.
            quick_sort_rec(array,start,pos-1)                                           # The quick_sort_rec function is then called recursively on the left and right sub-arrays to sort them.  
            quick_sort_rec(array,pos+1,finish)

    quick_sort_rec(array,0,len(array)-1)

ar = [randrange(100) for _ in range(20)]
print(ar)
quick_sort(ar)
print(ar)