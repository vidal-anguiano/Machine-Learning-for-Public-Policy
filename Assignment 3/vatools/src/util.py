import pandas as pd
from pandas import get_dummies
import pandas_profiling
from pandas import read_sql_query
import numpy as np
from sklearn.model_selection import train_test_split

def tt_split(X, Y, test_split = .5):
    '''
    Takes as inputs the features and the outcome var and creates train test
    split with a default test_split of .5.
    '''
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.4)

    return X_train, X_test, y_train, y_test

def calc_impute_value(df_col, method):
    '''
    Calculates the value to impute by taking the dataframe column and an
    method, and returns the mean, median, mode, or zeros based on the
    method chosen.
    Inputs:
        - df_col (pandas Series):
        - method ('string'):
    Outputs:
        - func(df_col) (integer, string, or boolean): Depending on the
        column type and the method performed, the value returned is
        the result of a mean, median, or mode method on a column
    '''
    assert method in ['mean','median','zeros', 'mode'], ('Use mean, median,\
                                                        mode or zeros.')

    methods = {'mean': lambda x: x.mean(),
                  'median': lambda x: x.median(),
                  'zeros': lambda x: 0,
                  'mode': lambda x: x.mode()}
    func = methods[method]

    return func(df_col)


def impute(df, method = 'mean', col_meth = None):
    '''
    By default, this function will impute the mean for all numeric
    columns and the mode for character and boolean columns. To impute
    median, mode, zeros, or mean for specific columns, provide parameter
    col_meth with a dictionary of column name as the key and the method
    as the value (ex. {'column1':'mean','column5':'zeros','column10':'mode'})
    Inputs:
        - df (pandas DataFrame): DataFrame to impute values into
        - method (string): To apply one imputation method on all null values,
        provide an method parameter. By default, mean values will be imputed
        for numeric columns and mode for non-numeric columns
        - col_meth (dict): dictionary of column name as the key and the
        method as the value
    Outputs:
        - df (pandas DataFrame): new pandas DataFrame with imputed values
    '''
    df = df.copy()
    if not col_meth:
        col_meth = dict(zip(df.columns,[method]*len(df.columns)))

    for col, op in col_meth.items():
        if df[col].dtype not in ['int64','float64'] and op in ['mean','median']:
            print('WARNING: You selected',op,
                 'for your method on a string type column. Using mode instead.')
            op = 'mode'
        df[col] = df[col].fillna(calc_impute_value(df[col],op))

    return df


# def discretize(df_col, bins = 5, labels = None, qcut = False):
#     '''
#     Discretizes a column with a chosen number of bins and labels.
#     If no labels are provided, integer labels from 1 to number of
#     bins are returned. By default, equal interval bins are used.
#     To get bins of equal size, set qcut to True.
#     Inputs:
#         - df_col (pandas Series): data column to be discretized
#         - bins (int): number of bins to discretize data
#         - labels (list): labels to use for the data. By default,
#         integers ranging from 1 to the number of bins are used
#         - qcut (boolean): Set to true to return equal sized bins.
#         By default, equal size intervals will be used.
#     Outputs:
#         - prints bin ranges
#         - new_col (pandas Series): new discretized column
#     '''
#     if not labels:
#         labels = list(range(1,bins+1))
#     if qcut:
#         new_col, retbins = pd.qcut(df_col, bins,labels = labels,
#                                    retbins = True)
#     else:
#         new_col, retbins = pd.cut(df_col, bins, labels = labels,
#                                   retbins = True)
#     print(retbins)
#     print(new_col.value_counts())
#     return new_col


def discretize(df, col_bins, qcut = False):
    '''
    Discretize multiple columns at once by providing a
    dictionary of column names and bins as keys and values,
    respectively.
    Inputs:
        - df (pandas DataFrame): dataframe to transform
        - col_bins (dict): dictionary containing column and
        number of bins pairs
        - qcut (boolean): Set to true to return equal sized bins.
        By default, equal size intervals will be used.
    Outputs:
        - df (pandas DataFrame): new pandas DataFrame with discretized
        columns added to the end of the dataframe
    '''
    df = df.copy()
    for col, bins in col_bins.items():
        df[col+'_descr'] = discretize(df[col], bins=bins, qcut=qcut)

    return df


def dummies(df, columns, drop_first = False):
    '''
    Create and append dummy variables to data set.
    Inputs:
        - df (pandas DataFrame): input dataframe from which to create
        dummies
        - columns (list of strings): columns for which to create dummies
        - drop_first (bool): default, False. If true, the first dummy will
        be dropped to prevent perfect coolinearity in some models
    Outputs:
        - the input df is replaced with the new, extended dataset
        - df.head() preview of the first 5 records to show creation of new
        columns.
    '''
    df = pd.get_dummies(df, columns=columns, drop_first=drop_first)

    return df
