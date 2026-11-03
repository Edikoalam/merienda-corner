def insertionSort(arr, key):
    n = len(arr)
    for i in range(1, n):
        insert_index = i
        current_value = arr[i]
        for j in range(i-1, -1, -1):
            if arr[j][key] < current_value[key]:
                arr[j+1] = arr[j]
                insert_index = j
            else:
                break
        arr[insert_index] = current_value

    return arr
