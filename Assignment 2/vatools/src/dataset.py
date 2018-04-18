'''
DataSet contains the data set to be used in machine learning model
implementations.

@author: Vidal Anguiano Jr.
'''
from vatools.src.db_conn import DB_Connection
from vatools.src.util import *
from sklearn.model_selection import train_test_split
import pandas as pd
import json


class DataSet(object):
    '''
    Class for representing a data set.
    '''

    def __init__(self, source, parameters_file = None, query = None):
        '''
        Constructor

        Inputs:
            dir_path: (string) path to the directory that contains the
              file
        '''
        if '.csv' in source:
            data = pd.read_csv(source)
        elif parameters_file:
            db = DB_Connection('credentials.json')
            if query:
                data = db.query(query)
            else:
                data = db.query('select * from {};'.format(source))
        parameters = json.load(open("data/" + parameters_file))
        self.data = data
        self.name = parameters["name"]
        self.features = parameters["features"]
        self.outcome = parameters["outcome"]
        self.seed = parameters["seed"]
        self.training_fraction = parameters["training_fraction"]
        self.column_names = list(data.columns)
        train_set, test_set = train_test_split(self.data,
                                train_size=self.training_fraction,
                                test_size=None, random_state=self.seed)
        self.train_set = train_set.reset_index(drop=True)
        self.test_set = test_set.reset_index(drop=True)


    def impute(self, df, method = 'mean', col_meth = None, supress = False):
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
            - the input df is replaced with the new, extended dataset
            - df.head() preview of the first 5 records to show creation of new
            columns.
        '''
        if not col_meth:
            col_meth = dict(zip(df.columns,[method]*len(df.columns)))

        for col, op in col_meth.items():
            if True not in df[col].isnull().values:
                continue
            if df[col].dtype not in ['int64','float64'] and op in ['mean','median']:
                print('WARNING: You selected',op,
                     'for your method on a string type column. Using mode instead.')
                op = 'mode'
            df[col+'_imputed'] = df[col].fillna(calc_impute_value(df[col],op)).astype(int)
        if supress:
            return None
        return df.head()


    def discretize(self, df, column, bins = 5, labels = None, qcut = False,
                   supress = False):
        '''
        Discretizes a column with a chosen number of bins and labels.
        If no labels are provided, integer labels from 1 to number of
        bins are returned. By default, equal interval bins are used.
        To get bins of equal size, set qcut to True.
        Inputs:
            - df (pandas DataFrame): DataFrame with desired column to discretize
            - column (string): column to discretize
            - bins (int): number of bins to discretize data
            - labels (list): labels to use for the data. By default,
            integers ranging from 1 to the number of bins are used
            - qcut (boolean): Set to true to return equal sized bins.
            By default, equal size intervals will be used.
        Outputs:
            - the input df is replaced with the new, extended dataset
            - prints bin ranges
            - df.head() preview of the first 5 records to show creation of new
            columns.
        '''
        if not labels:
            labels = list(range(1,bins+1))
        if qcut:
            df[column + '_discr'], retbins = pd.qcut(df[column], bins,
                                            labels = labels,
                                            retbins = True)
        else:
            df[column + '_discr'], retbins = pd.cut(df[column], bins, labels = labels,
                                      retbins = True)
        print(retbins)
        print(df[column + '_discr'].value_counts())
        if supress:
            return None
        return df.head()


    def dummies(self, df, columns, drop_first = False, supress = False):
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

        if supress:
            return None
        return df.head()


    def reset(self):
        '''
        Reset dataset to state before processing.
        '''
        train_set, test_set = train_test_split(self.data,
                                train_size=self.training_fraction,
                                test_size=None, random_state=self.seed)
        self.train_set = train_set.reset_index(drop=True)
        self.test_set = test_set.reset_index(drop=True)


    def feature_key(self):
        '''
        Prints a key that relates features to the integers that are to be used
        when selecting features to train a model on.
        '''
        for i, feature in enumerate(self.train_set.columns[1:]):
            print("{} = {}".format(i+1, feature))
