# Insertion Sort (Max to Min)
# Insertion Sort is a simple sorting algorithm that builds the final sorted array one item at a time. 
# It is much less efficient on large lists than more advanced algorithms such as quicksort, heapsort, or merge sort. 
# However, it has several advantages, such as simple implementation, efficient for small data sets, and stable (does not change the relative order of equal elements).
# The algorithm works by dividing the array into a sorted and an unsorted part.
# It iteratively takes an element from the unsorted part and inserts it into the correct position in the sorted part.
# The time complexity of Insertion Sort is O(n^2) in the worst and average cases, and O(n) in the best case (when the array is already sorted).
def insertion_sort(array):
    for i in range(1, len(array)):                              # Start from the second element (index 1) and iterate through the array
        for j in range(i,0,-1):                                 # For each element, compare it with the elements in the sorted part (from index i down to 1)
            if array[j] > array[j-1]:                           # If the current element is greater than the previous element, swap them
                array[j], array[j-1] = array[j-1], array[j]     #swap the elements
            else:
                break


array = [9, 2, 4, 7, 1, 8, 6, 3]
print(array)
insertion_sort(array)
print(array)