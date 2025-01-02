# D4K_test/input_data.py
import pandas as pd
import numpy as np
import os
import torch
# import argparse  # Removed argparse import {{ edit_1 }}

class InputData:
    """
    A class to handle various input data types and convert them into a pandas DataFrame
    or a PyTorch Tensor.
    """

    def __init__(self, input_path, input_type=None, encoding='utf-8'):
        """
        Initializes the InputData object.
        """
        self.input_path = input_path
        self.input_type = input_type
        self.encoding = encoding
        self.df = None  # Initialize DataFrame attribute

    # ... (Other methods to load and process data)

    def get_tensor(self, batched=False, batch_size=1):
        """
        Converts the loaded data into a PyTorch Tensor.
        """
        

        if self.df is None:
            raise RuntimeError("No data loaded. Call get_dataframe() or load_data() first.")

        if batched:
            if not isinstance(batch_size, int) or batch_size <= 0:
                raise ValueError("batch_size must be a positive integer.")

            values = torch.tensor(self.df.values)
            num_samples = values.shape[0]
            num_batches = (num_samples + batch_size - 1) // batch_size  # Calculate number of batches

            return [values[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]
        else:
            return torch.tensor(self.df.values)

    """
    A class to handle various input data types and convert them into a pandas DataFrame.
    """

    def __init__(self, input_path, input_type=None, encoding='utf-8'):
        """
        Initializes the InputData object.
        """
        self.input_path = input_path
        self.input_type = input_type
        self.encoding = encoding
        self.df = self._load_data()

    def _load_data(self):
        """
        Loads the data based on the specified input type and handles encoding issues.
        """
        try:
            if self.input_type == 'csv' or self.input_path.endswith('.csv'):
                return pd.read_csv(self.input_path, encoding=self.encoding)
            elif self.input_type == 'xlsx' or self.input_path.endswith('.xlsx'):
                return pd.read_excel(self.input_path)
            elif self.input_type == 'gsheet' or self.input_path.endswith('.gsheet'):  # Placeholder for gsheet functionality
                raise NotImplementedError("Google Sheet integration is not yet implemented.")
            elif self.input_type == 'txt' or self.input_path.endswith('.txt'):
                return pd.read_csv(self.input_path, delimiter="\t", encoding=self.encoding) # Assumes tab-separated for .txt
            elif self.input_type == 'tsv' or self.input_path.endswith('.tsv'):
                return pd.read_csv(self.input_path, delimiter="\t", encoding=self.encoding)
            else:
                if self.input_type is not None:
                    raise ValueError(f"Unsupported input type: {self.input_type}")
                else:  # Attempt to infer from file extension
                    raise ValueError(f"Could not infer input type from file extension: {self.input_path}")

        except UnicodeDecodeError as e:
            # Attempt to decode with 'latin-1' if 'utf-8' fails
            if self.encoding == 'utf-8':
                return self._load_data(encoding='latin-1')  # Retry with different encoding
            else:
                raise UnicodeDecodeError(f"Failed to decode file with both 'utf-8' and 'latin-1': {e}")
        except Exception as e:
            print(f"An error occurred while loading the data: {e}")
            return None

    def get_dataframe(self):
        """
        Returns the loaded pandas DataFrame.
        """
        return self.df
    
    def get_features(self):
        """
        Returns the features (column names) of the loaded DataFrame as a NumPy array.
        """
        if self.df is not None and not self.df.empty:
            features = self.df.columns.values
            if not np.array_equal(features, self.df.columns.values):  # Verify feature names
                raise ValueError("Error: Feature names array does not match DataFrame columns.")
            return features
        return None

    def get_values(self):
        """
        Returns the values of the loaded DataFrame.
        """
        if self.df is not None:
            values = self.df.values
            if values.shape != self.df.shape:  # Verify shape of values array
                raise ValueError("Error: Values array shape does not match DataFrame shape.")
            return values
        return None



class DirectoryDataLoader:
    """
    Loads data from all supported file types within a directory recursively.
    """

    def __init__(self, directory_path, supported_types=None, encoding='utf-8'):
        """
        Initializes DirectoryDataLoader with a directory path, supported file types, and encoding.
        """
        self.directory_path = directory_path
        self.supported_types = supported_types if supported_types is not None else ['csv', 'xlsx', 'txt', 'tsv', 'gsheet']
        self.encoding = encoding
        self.dataframes = {}  # Dictionary to store loaded DataFrames

    def load_data(self):
        """
        Loads data from all supported files in the specified directory and its subdirectories.
        """
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = file.split('.')[-1].lower()
                if file_ext in self.supported_types:
                    try:
                        input_data = InputData(file_path, input_type=file_ext, encoding=self.encoding)
                        self.dataframes[file_path] = input_data.get_dataframe()
                    except Exception as e:
                        print(f"Error loading file {file_path}: {e}")
        return self.dataframes

    def merge_dataframes(self):
        """
        Merges compatible DataFrames loaded by `load_data`.
        """
        if not self.dataframes:
            return None, []

        compatible_dfs = []
        incompatible_dfs = []

        first_df = list(self.dataframes.values())[0]
        first_shape = first_df.shape

        for file_path, df in self.dataframes.items():
            if df.shape[1] == first_shape[1]:  # Check if number of columns match
                compatible_dfs.append(df)
            else:
                incompatible_dfs.append((file_path, df.shape))

        if not compatible_dfs:
            return None, incompatible_dfs

        try:
            merged_df = pd.concat(compatible_dfs, ignore_index=True)
            return merged_df, incompatible_dfs
        except Exception as e:
            print(f"Error merging DataFrames: {e}")
            return None, incompatible_dfs

# Removed main function and if __name__ == "__main__" block {{ edit_2 }}