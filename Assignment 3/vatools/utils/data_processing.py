import pandas as pd
from pandas import get_dummies
import pandas_profiling
from pandas import read_sql_query
import numpy as np
import seaborn as sns
from datetime import datetime
from sklearn.model_selection import train_test_split


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
    if type(method) == list:
        method, value = 'custom', method[0]
    assert method in ['mean', 'median', 'zeros', 'mode', 'missing', 'custom'], ('Use mean, median,\
                                                        # mode or zeros.')

    methods = {'mean': lambda x: x.mean(),
                  'median': lambda x: x.median(),
                  'zeros': lambda x: 0,
                  'mode': lambda x: x.mode(),
                  'missing': lambda x: 'missing',
                  'custom': lambda x: value}
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
    if not col_meth:
        col_meth = dict(zip(df.columns,[method]*len(df.columns)))

    for col, op in col_meth.items():
        if df[col].dtype not in ['int64','float64'] and op in ['mean','median']:
            print('WARNING: You selected',op,
                 'for your method on a string type column. Using mode instead.')
            op = 'mode'
        df[col] = df[col].fillna(calc_impute_value(df[col], op))

    return df


def discretize(df_col, bins = 5, labels = None, qcut = False):
    '''
    Discretizes a column with a chosen number of bins and labels.
    If no labels are provided, integer labels from 1 to number of
    bins are returned. By default, equal interval bins are used.
    To get bins of equal size, set qcut to True.
    Inputs:
        - df_col (pandas Series): data column to be discretized
        - bins (int): number of bins to discretize data
        - labels (list): labels to use for the data. By default,
        integers ranging from 1 to the number of bins are used
        - qcut (boolean): Set to true to return equal sized bins.
        By default, equal size intervals will be used.
    Outputs:
        - prints bin ranges
        - new_col (pandas Series): new discretized column
    '''
    if not labels:
        labels = list(range(1,bins+1))
    if qcut:
        new_col, retbins = pd.qcut(df_col, bins,labels = labels,
                                   retbins = True)
    else:
        new_col, retbins = pd.cut(df_col, bins, labels = labels,
                                  retbins = True)
    print(retbins)
    print(new_col.value_counts())
    return new_col


def discretize_many(df, col_bins):
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
    for col, vals in col_bins.items():
        print(col, vals)
        if type(vals) == list:
            bins, qcut = vals[0], vals[1]
        else:
            bins, qcut = vals, False
        df[col+'_descr'] = discretize(df[col], bins=bins, qcut=qcut)
        df.drop(columns=col)

    return df


def dummies(df, columns, drop_first = False, dummy_na = False):
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
    for col in columns:
        df[col] = df[col].apply(lambda x: x.lower().replace(' ','_').replace('&','and').replace('-','_'))
    df = pd.get_dummies(df, columns=columns, drop_first = drop_first, dummy_na = dummy_na)

    return df


def dullify(df, col_val):
    ''' Decrease cardinality of feature and create dummies. '''
    for col, vals in col_val.items():
        df[col] = df[col].apply(lambda x: x if x in vals else 'other')
        df = dummies(df, columns = [col])
    return df


def fix_bool(df, columns):
    ''' Will fix booleans if represented as t/f, T/F or string True/False. '''
    for col in columns:
        if 't' in df[col].unique():
            df[col] = df[col].apply(lambda x: 1 if x == 't' else 0 if x == 'f' else -1)
        elif 'T' in df[col].unique():
            df[col] = df[col].apply(lambda x: 1 if x == 'T' else 0 if x == 'F' else -1)
        elif 'True' in df[col].unique():
            df[col] = df[col].apply(lambda x: 1 if x == 'True' else 0 if x == 'False' else -1)

def current_time_str():
    current_time_list = []
    current_time_list.append(str(datetime.now().month))
    current_time_list.append(str(datetime.now().day))
    current_time_list.append(str(datetime.now().hour))
    current_time_list.append(str(datetime.now().minute))
    current_time = '_'.join(current_time_list)
    return current_time
