# Problem

Write a function (`remove_val(val, lst)`) that removes all occurrences of a specific value (`val`) in a given list (`lst`). Also, print out the indices of the items being removed, if any.

# Thought Process

## STEP 1

-   **Instruction:** Check if the given list is valid (i.e., not None). If it's not, return the list as is without any modification.
-   **Data Types:**
    -   `lst` (list)

## STEP 2

-   **Instruction:** Create a new list to store the elements that are not equal to the value to be removed.
-   **Naming Suggestion:**
    -   `result_list` (list)

## STEP 3

-   **Instruction:** Go through each element of the given list using a loop. Keep track of the index of each element.
-   **Naming Suggestions:**
    -   `index` (Suggested variable name for the loop counter)
    -   `current_element` (Suggested variable name for the current element)
-   **Data Types:**
    -   `index` (integer)
    -   `current_element` (any data type, depending on the list content)

## STEP 4

-   **Instruction:** Check if the current element is equal to the value that needs to be removed.
-   **Data Types:**
    -   `val` (any data type, should be comparable to elements in `lst`)

## STEP 5

-   **Instruction:** If the current element is equal to the value, print the index of the element being removed.

## STEP 6

-   **Instruction:** If the current element is not equal to the value, add it to the `result_list`.

## STEP 7

-   **Instruction:** After processing all the elements, return the `result_list`.

## Function Naming

-   **Instruction:** The function should be named `remove_val` as specified in the problem description.

## Input Sanitization and Test Cases

-   **Input Sanitization:** Ensure that the `lst` input is actually a list. Consider raising a TypeError if it's not. Also, check if `lst` is None, and handle it appropriately.
-   **Test Cases:**
    -   **Empty List:**
        -   Input: `val` = 5, `lst` = []
        -   Expected Output: [], nothing printed
    -   **No matching values:**
        -   Input: `val` = 5, `lst` = [1, 2, 3, 4]
        -   Expected Output: [1, 2, 3, 4], nothing printed
    -   **All matching values:**
        -   Input: `val` = 5, `lst` = [5, 5, 5]
        -   Expected Output: [], printed indices: 0, 1, 2
    -   **Mixed values:**
        -   Input: `val` = 5, `lst` = [1, 5, 2, 5, 3]
        -   Expected Output: [1, 2, 3], printed indices: 1, 3
    -   **None List:**
        -   Input: `val` = 5, `lst` = None
        -   Expected Output: None, nothing printed
    -   **Non-list type for lst**
        -   Input: `val` = 5, `lst` = "hello"
        -   Expected Output: TypeError, nothing printed
    -   **Different Data Types**
        -   Input: `val` = "apple", `lst` = ["banana", "apple", "orange", "apple"]
        -   Expected Output: ["banana", "orange"], printed indices: 1, 3
    -   **Nested Lists**
        -   Input: `val` = [1, 2], `lst` = [[3, 4], [1, 2], [5, 6]]
        -   Expected Output: [[3, 4], [5, 6]], printed indices: 1
    -   **Mixed Data Types**
        -   Input: `val` = 2, `lst` = [1, "two", 2, 3.0, 2]
        -   Expected Output: [1, "two", 3.0], printed indices: 2, 4
    -   **Duplicate Non-Target Values:**
        -   Input: `val` = 10, `lst` = [20, 20, 30, 10, 30, 10]
        -   Expected Output: [20, 20, 30, 30], printed indices: 3, 5
    -   **Target as a List:**
        -   Input: `val` = [1, 2], `lst` = [[1, 2], [3, 4], [1, 2], [5, 6]]
        -   Expected Output: [[3, 4], [5, 6]], printed indices: 0, 2

