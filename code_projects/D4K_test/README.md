# D4K_test Data Loading Package

This package provides classes for loading and processing data from various file types, including CSV, Excel, TXT, and TSV files. It also supports loading data from directories recursively.

## Classes

### `InputData`

The `InputData` class is used to load data from a single file and convert it into a pandas DataFrame or a PyTorch Tensor.

#### Initialization

```python
input_data = InputData(input_path, input_type=None, encoding='utf-8')
```

*   `input_path` (str): The path to the input file.
*   `input_type` (str, optional): The type of input data (e.g., 'csv', 'xlsx', 'txt', 'tsv'). If not provided, the type will be inferred from the file extension.
*   `encoding` (str, optional): The encoding of the input data (default is 'utf-8').

#### Methods

*   `get_dataframe()`: Returns the loaded pandas DataFrame.
*   `get_features()`: Returns the features (column names) of the DataFrame as a NumPy array.
*   `get_values()`: Returns the values of the DataFrame as a NumPy array.
*   `get_tensor(batched=False, batch_size=1)`: Converts the loaded data into a PyTorch Tensor.
    *   `batched` (bool, optional): If True, returns a list of batched tensors. Default is False.
    *   `batch_size` (int, optional): The batch size for tensor conversion. Default is 1.

#### Example Usage

```python
from D4K_test.input_data import InputData


## Load data from a CSV file
input_data = InputData("data.csv")
df = input_data.get_dataframe()
if df is not None:
    print("DataFrame:")
    print(df)
features = input_data.get_features()
if features is not None:
    print("Features:")
    print(features)
values = input_data.get_values()
if values is not None:
    print("Values:")
    print(values)
tensor = input_data.get_tensor()
    print("Tensor:")
    print(tensor)
else:
    print("Failed to load data.")
```
### `DirectoryDataLoader`

The `DirectoryDataLoader` class is used to load data from all supported file types within a directory recursively.

#### Initialization

```python
directory_loader = DirectoryDataLoader(directory_path, supported_types=None, encoding='utf-8')
```

*   `directory_path` (str): The path to the directory containing the data files.
*   `supported_types` (list, optional): A list of supported file types (e.g., ['csv', 'xlsx', 'txt', 'tsv']). If not provided, the default is ['csv', 'xlsx', 'txt', 'tsv', 'gsheet'].
*   `encoding` (str, optional): The encoding of the input data (default is 'utf-8').

#### Methods

*   `load_data()`: Loads data from all supported files in the specified directory and its subdirectories. Returns a dictionary where keys are file paths and values are pandas DataFrames.
*   `merge_dataframes()`: Merges compatible DataFrames loaded by `load_data`. Returns a tuple containing the merged DataFrame and a list of incompatible DataFrames (file path and shape).

#### Example Usage
```python
from D4K_test.input_data import DirectoryDataLoader
## Load data from a directory
directory_loader = DirectoryDataLoader("data_directory")
dataframes = directory_loader.load_data()
if dataframes:
    for file_path, df in dataframes.items():
    print(f"DataFrame from {file_path}:")
    print(df)
merged_df, incompatible_dfs = directory_loader.merge_dataframes()
if merged_df is not None:
    print("Merged DataFrame:")
    print(merged_df)
if incompatible_dfs:
    print("Incompatible DataFrames:")
    for file_path, shape in incompatible_dfs:
        print(f" {file_path}: {shape}")
```


## Installation

1.  Make sure you have Python 3.7 or higher installed.
2.  Place the `input_data.py` file in a directory named `D4K_test`.
3.  You can then import the classes in your Python scripts using:

    ```python
    from D4K_test.input_data import InputData, DirectoryDataLoader
    ```

## Dependencies

*   pandas
*   numpy
*   torch

You can install these dependencies using pip:

```bash
pip install -r requirements.txt
```


## Notes

*   The `gsheet` input type is a placeholder and is not yet implemented.
*   The `DirectoryDataLoader` will only merge dataframes that have the same number of columns.
*   Error handling is included for common issues such as file not found, unsupported file types, and encoding errors.


### `feature_selector`

The `feature_selector` module provides functions for feature selection using various methods.

#### Functions

*   `feature_selector(X, y, model, names, _method="topk", n=None, fit_X=False, thres=0.1)`: Performs voting-based feature selection.
    *   `X` (np.ndarray): Feature matrix.
    *   `y` (np.ndarray): Target vector.
    *   `model` (sklearn.base.BaseEstimator): Estimator for RFE.
    *   `names` (list): Feature names.
    *   `_method` (str, optional): "topk" for top-K method (default), "cutoff" for cut-off based method.
    *   `n` (int, optional): Number of features to select. If None (default), selects half of the total features for top-K method.
    *   `fit_X` (bool, optional): If True, returns the transformed feature matrix. Otherwise, returns the indices of selected features.
    *   `thres` (float, optional): Cut-off threshold for the cutoff method (default 0.1).
*   `evaluate_model(model, X, y)`: Evaluates a given model using repeated stratified k-fold cross-validation.
    *   `model` (object): The machine learning model to evaluate.
    *   `X` (array-like): The input features.
    *   `y` (array-like): The target variable.
*   `feat_select_eval(X, y, model=LogisticRegression(solver='liblinear'))`: Evaluates feature selection using a given model and SelectKBest.
    *   `X` (array-like): The input features.
    *   `y` (array-like): The target variable.
    *   `model` (object, optional): The model to use for evaluation. Defaults to LogisticRegression.

#### Example Usage

```python
from D4K_test.feature_selector import feature_selector
import numpy as np
from sklearn.linear_model import Ridge
## Sample data
X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y = np.array([0, 1, 0])
model = Ridge()
names = ['feature1', 'feature2', 'feature3']
##Top-K method
selected_features = feature_selector(X, y, model, names, method="topk", n=2)
print("Selected Features (Top-K):", selected_features)
##Cut-off method
selected_features = feature_selector(X, y, model, names, method="cutoff", thres=0.2)
print("Selected Features (Cutoff):", selected_features)
```

## Installation

1.  Make sure you have Python 3.7 or higher installed.
2.  Place the `input_data.py` and `feature_selector.py` files in a directory named `D4K_test`.
3.  You can then import the classes and functions in your Python scripts using:

    ```python
    from D4K_test.input_data import InputData, DirectoryDataLoader
    from D4K_test.feature_selector import feature_selector, evaluate_model, feat_select_eval
    ```

## Dependencies

*   pandas
*   numpy
*   torch
*   scikit-learn
*   matplotlib

You can install these dependencies using pip:
```bash
pip install -r requirements.txt
```
