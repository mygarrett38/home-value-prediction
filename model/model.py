#################################################################
#   This file was used to create the .pkl files that contain    #
#   the models. Use this file as a reference, but DO NOT RUN    #
#   IT! The models have already been generated!                 #
#################################################################

import pandas as pd
import os.path
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_log_error as msle
from xgboost import XGBRegressor, XGBRFRegressor

import warnings
warnings.filterwarnings('ignore')

def main():
    # Open Zillow.csv file
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "../data/Zillow.csv"))

    # Data Cleaning Step
    to_remove = []
    for col in df.columns:

        # Removing columns having only one value.
        if df[col].nunique() == 1:
            to_remove.append(col)

        # Removing columns with more than 80% of the
        # rows as null values.
        elif (df[col].isnull()).mean() > 0.80:
            to_remove.append(col)

    df.drop(to_remove,
        axis=1,
        inplace=True)
    
    # Remove NaNs
    for col in df.columns:
        if df[col].dtype == 'object' or col.endswith("typeid"):
            df[col] = df[col].fillna(df[col].mode()[0])
        elif df[col].dtype in ("int64", "float64"):
            df[col] = df[col].fillna(df[col].mean())
    
    ints, floats, objects = [], [], []

    for col in df.columns:
        if df[col].dtype == float:
            floats.append(col)
        elif df[col].dtype == int:
            ints.append(col)
        else:
            objects.append(col)

    # Skip the analysis steps, they're already done
    # Remove highly correlated columns
    to_remove = ['calculatedbathnbr', 'fullbathcnt', 'fips',
             'rawcensustractandblock', 'taxvaluedollarcnt',
             'finishedsquarefeet12', 'landtaxvaluedollarcnt']

    df.drop(to_remove, axis=1, inplace=True)

    df = df[(df['target'] > -1) & (df['target'] < 1)]

    for col in objects:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col]) # type: ignore

    # Model Training Step
    features = df.drop(['parcelid', 'target'], axis=1)
    target = df['target'].values

    X_train, X_val, Y_train, Y_val = train_test_split(features, target)
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)

    # Model Evaluation Step
    model = XGBRegressor()
    model.fit(X_train, Y_train)

    train_preds = model.predict(X_train)
    print('  Training Error:', end=" ")
    print(f"{np.sqrt(msle(Y_train, train_preds)):.6%}")

    val_preds = model.predict(X_val)
    print('Validation Error:', end=" ")
    print(f"{np.sqrt(msle(Y_val, val_preds)):.6%}")
    print()

if __name__ == "__main__":
    main()