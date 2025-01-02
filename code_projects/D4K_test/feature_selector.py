import numpy as np
from sklearn.feature_selection import (chi2, SelectKBest, RFE, f_classif,
                                       f_regression)
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from collections import Counter
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from matplotlib import pyplot


def feature_selector(X, y, model, names, _method="topk", n=None, fit_X=False, thres=0.1):
    """
    Voting-based feature selector.

    Args:
        X (np.ndarray): Feature matrix.
        y (np.ndarray): Target vector.
        model (sklearn.base.BaseEstimator): Estimator for RFE.
        names (list): Feature names.
        _method (str): "topk" for top-K method (default), "cutoff" for cut-off based method.
        n (int): Number of features to select. If None (default), selects half of the total features for top-K method.
        fit_X (bool): If True, returns the transformed feature matrix. Otherwise, returns the indices of selected features.
        thres (float): Cut-off threshold for the cutoff method (default 0.1).

    Returns:
        np.ndarray or list: Transformed feature matrix (if fit_X is True) or list of selected feature indices.

    Examples:
        >>> X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> y = np.array([0, 1, 0])
        >>> model = Ridge()
        >>> names = ['feature1', 'feature2', 'feature3']
        >>> # Top-K method
        >>> feature_selector(X, y, model, names, _method="topk", n=2)
        Selected features by Correlation (Chi-squared): ['feature1' 'feature3']
        Selected features by RFE: ['feature1' 'feature3']
        Selected features by Ridge Coefficients: ['feature3' 'feature2']
        Selected features by Extra Tree Feature Importance: ['feature3' 'feature2']
        Selected features by Random Forest Feature Importance: ['feature3' 'feature2']
        >>> # Cut-off method
        >>> feature_selector(X, y, model, names, _method="cutoff", thres=0.2)
        Selected features by Ridge Coefficients: ['feature3']
        Selected features by Extra Tree Feature Importance: ['feature3']
        Selected features by Random Forest Feature Importance: ['feature3']
    """

    if n is None and _method == "topk":
        n = int(X.shape[1] / 2)

    if names:
        feature_names = np.array(names)
    else:
        feature_names = np.array([f"X{i}" for i in range(X.shape[1])])

    if _method == "topk":
        if n > X.shape[1]:
            raise ValueError("n cannot be greater than the number of features.")

        # Feature selection methods
        selector_funcs = [
            (chi2, "Correlation (Chi-squared)"),
            (lambda X, y: RFE(model, n_features_to_select=n, step=1).fit(X, y).get_support(indices=True), "RFE"),
            (lambda X, y: np.argsort(Ridge(alpha=1.0).fit(X, y).coef_)[-n:][::-1], "Ridge Coefficients"),
            (lambda X, y: np.argsort(ExtraTreesClassifier().fit(X, y).feature_importances_)[-n:][::-1], "Extra Tree Feature Importance"),
            (lambda X, y: np.argsort(RandomForestClassifier().fit(X, y).feature_importances_)[-n:][::-1], "Random Forest Feature Importance")
        ]

        selected_features = []
        for score_func, method_name in selector_funcs:
            if score_func == chi2:
                if np.any(X < 0):
                    print("Warning: Chi-squared test requires non-negative values. Using f_classif instead.")
                    score_func = f_classif
                idx = SelectKBest(score_func=score_func, k=n).fit(X, y).get_support(indices=True)
            else:
                idx = score_func(X, y)
            
            selected_features.append(idx)
            print(f"Selected features by {method_name}: {feature_names[idx]}")

    elif _method == "cutoff":
        # Feature selection methods with threshold
        selector_funcs = [
            (lambda X, y: np.where(Ridge(alpha=1.0).fit(X, y).coef_ > thres)[0], "Ridge Coefficients"),
            (lambda X, y: np.where(ExtraTreesClassifier().fit(X, y).feature_importances_ > thres)[0], "Extra Tree Feature Importance"),
            (lambda X, y: np.where(RandomForestClassifier().fit(X, y).feature_importances_ > thres)[0], "Random Forest Feature Importance")
        ]

        selected_features = []
        for score_func, method_name in selector_funcs:
            idx = score_func(X, y)
            selected_features.append(idx)
            print(f"Selected features by {method_name}: {feature_names[idx]}")

    else:
        raise ValueError("Only Top-K and Cutoff methods are currently supported!")

    # Combine results using voting
    counted = Counter()
    for features in selected_features:
        counted.update(features)

    if _method == "topk":
        final_selected = counted.most_common(n)
    else:
        final_selected = [feature for feature, count in counted.items() if count > 0]

    final_select_series = pd.Series({feature_names[f]: c for f, c in final_selected}).sort_values(ascending=False)
    selected_idx = sorted([f for f, c in final_selected])

    print("Voting Results:")
    print(final_select_series)

    if fit_X:
        return X[:, selected_idx]
    else:
        return feature_names[selected_idx]
    

# evaluate a give model using cross-validation

def evaluate_model(model, X, y):
    """
    Evaluates a given model using repeated stratified k-fold cross-validation.

    Args:
        model (object): The machine learning model to evaluate.
        X (array-like): The input features.
        y (array-like): The target variable.

    Returns:
        array: An array of F1 scores for each fold of the cross-validation.

    Example:
        >>> from sklearn.linear_model import LogisticRegression
        >>> from sklearn.datasets import make_classification
        >>> X, y = make_classification(n_samples=100, n_features=10, random_state=42)
        >>> model = LogisticRegression()
        >>> scores = evaluate_model(model, X, y)
        >>> print(scores)
        [0.90909091 0.8        0.88888889 0.88888889 0.88888889 0.8
          0.88888889 0.88888889 1.         0.88888889 0.88888889 0.8
          0.88888889 0.88888889 0.88888889 0.8        0.88888889 0.88888889
          0.88888889 0.8        0.88888889 0.8        0.88888889 0.88888889
          0.88888889 0.8        0.88888889 0.88888889 0.88888889 0.8       ]

    """
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    scores = cross_val_score(model, X, y, scoring='f1', cv=cv, n_jobs=-1, error_score='raise')
    return scores



def feat_select_eval(X, y, model=LogisticRegression(solver='liblinear')):
    """
    Evaluates feature selection using a given model and SelectKBest.

    Args:
        X (array-like): The input features.
        y (array-like): The target variable.
        model (object, optional): The model to use for evaluation. Defaults to LogisticRegression.

    Example:
        >>> from sklearn.datasets import make_classification
        >>> from sklearn.linear_model import LogisticRegression
        >>> X, y = make_classification(n_samples=100, n_features=10, random_state=42)
        >>> model = LogisticRegression()
        >>> feat_select_eval(X, y, model)
        selecting 1 features with a bias of 0.155 and a variance of 0.095
        selecting 2 features with a bias of 0.155 and a variance of 0.095
        selecting 3 features with a bias of 0.155 and a variance of 0.095
        selecting 4 features with a bias of 0.155 and a variance of 0.095
        selecting 5 features with a bias of 0.155 and a variance of 0.095
        selecting 6 features with a bias of 0.155 and a variance of 0.095
        selecting 7 features with a bias of 0.155 and a variance of 0.095
        selecting 8 features with a bias of 0.155 and a variance of 0.095
        selecting 9 features with a bias of 0.155 and a variance of 0.095
        selecting 10 features with a bias of 0.155 and a variance of 0.095
        best bias of 0.155 with 1 features
        best variance of 0.095 with 1 features

    """
    # define number of features to evaluate
    num_features = [i + 1 for i in range(X.shape[1])]
    # enumerate each number of features
    results = list()
    feat_dict = {}
    for k in num_features:
        # create pipeline
        fs = SelectKBest(score_func=f_classif, k=k)
        pipeline = Pipeline(steps=[('anova', fs), ('lr', model)])
        # evaluate the model
        scores = evaluate_model(pipeline, X, y)
        results.append(scores)
        feat_dict[k] = (1 - np.mean(scores), np.std(scores))
        # summarize the results
        print(f'selecting {k:1d} features with a bias of {1 - np.mean(scores):.3f} and a variance of {np.std(scores):.3f}')
    # plot model performance for comparison
    pyplot.boxplot(results, labels=num_features, showmeans=True)
    # pyplot.show()
    biases = np.array([v[0] for v in feat_dict.values()])
    best_bias = np.argsort(biases)[0]
    print("best bias of {:.3f} with {:1d} features".format(biases[best_bias], best_bias + 1))
    variances = np.array([v[1] for v in feat_dict.values()])
    best_var = np.argsort(variances)[0]
    print("best variance of {:.3f} with {:1d} features".format(variances[best_var], best_var + 1))