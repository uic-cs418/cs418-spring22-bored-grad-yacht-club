import numpy as np
import pandas as pd
from sklearn.ensemble import AdaBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt

def adaboost_hyperparameter_tuning(X, y):
    """
        Finding the best depth and # of estimators 
        for AdaBoost algorithm
    """
    names = []
    errors = {}
    parameters = {}
    kf = KFold(n_splits=5)
    # find best depth
    depths = range(1,11)
    for n in depths:
        # split data into k-folds and train the models
        fold_errors = []
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            r1 = AdaBoostRegressor(base_estimator=DecisionTreeRegressor(max_depth=n), random_state=0)
            r1.fit(X_train, y_train)
            fold_errors.append(np.mean(abs(r1.predict(X_test) - y_test)))
        # record the mean error of k-folds
        errors[n] = np.mean(fold_errors)
    parameters['max_depth'] = min(errors, key=errors.get)
#     plt.subplot(1,2,1)
#     plt.plot(errors.keys(), errors.values())
#     plt.title("Absolute error on various maximum depths of decision tree")
#     plt.xlabel("Depth")
#     plt.ylabel("Absolute error")
    
    names = []
    errors = {}
    # find best # of estimators
    n_estimators = range(1,101,10)
    for n in n_estimators:
        fold_errors = []
        # split data into k-folds and train the models
        for train_index, test_index in kf.split(X):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            r1 = AdaBoostRegressor(base_estimator=DecisionTreeRegressor(max_depth=parameters['max_depth']), random_state=0,n_estimators=n)
            r1.fit(X_train, y_train)
            fold_errors.append(np.mean(abs(r1.predict(X_test) - y_test)))
        # record the mean error of k-folds
        errors[n] = np.mean(fold_errors)
    parameters['n_estimators'] = min(errors, key=errors.get)
#     plt.subplot(1,2,2)
#     plt.plot(errors.keys(), errors.values())
#     plt.title("Absolute error on various number of estimators")
#     plt.xlabel("Number of estimators")
#     plt.ylabel("Absolute error")
#     plt.tight_layout()
#     plt.show()
    return parameters
    
def adaboost_analysis():
    df = pd.read_csv('AllData-Covid-SocioDemographics-Cases-Deaths.csv')
    df = df.drop(df[df['Death Counts(Per 1000)'] == 0].index)
    y = df.pop('Death Counts(Per 1000)').to_numpy()
    df.pop('Zipcode')
    X = df[['Some College(%)', 'Asian(%)', 'Same House Prev Year(%)', 'Moved Since Prev Year(%)', 
            'High School(%)', 'Median housing value', 'No Degree(%)', 'Below poverty line(%)',
           'Married (%)', 'Single (%)', 'Number of housing units', 'Number of households', 'Population',
           'Owner Occupied (%)', 'Renter Occupied (%)', 'White(%)', 'Hispanic(%)', 'Mean travel time to work (Minutes)',
           'Other (%)', 'Drove Alone (%)', 'Foriegn Born Population(%)', 'Public Transit (%)']].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    # baseline model
    median_deaths = np.median(y_train)
    baseline_pred = np.repeat(median_deaths, len(y_test))
    print("Average absolute baseline error (deaths per 1000) = ", round(np.mean(abs(baseline_pred - y_test)), 2))
    
    # AdaBoost model
    params = adaboost_hyperparameter_tuning(X, y)
    mdl = AdaBoostRegressor(base_estimator=DecisionTreeRegressor(max_depth=params['max_depth']), 
                           random_state=0,
                           n_estimators=params['n_estimators'])
    mdl.fit(X_train, y_train)
    print("Average absolute model error (deaths per 1000) = ", round(np.mean(abs(mdl.predict(X_test) - y_test)),2))