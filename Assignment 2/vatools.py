import pandas as pd
from pandas import get_dummies
import numpy as np
import psycopg2
import csv
import csv, ast, psycopg2
import pandas_profiling
from pandas import read_sql_query
import os
import numpy as np

profile_data = lambda df: pandas_profiling.ProfileReport(df)


class db_connection(object):
    def __init__(self, hostname, username, password, database):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database

    def q(self, query, pandas = True):
        conn = psycopg2.connect( host=self.hostname, user=self.username, password=self.password, dbname=self.database )
        if pandas:
            result = read_sql_query(query, conn)
            conn.close()
            return result

        cur = conn.cursor()
        cur.execute(query)
        if 'create ' in query.lower() or 'drop ' in query.lower():
            conn.commit()
            conn.close()
            return None
        print(cur.fetchall())
        conn.close()
        

    def create_table(self, csv_file, table_name, insert = False, sep = ','):
        try:
            conn = psycopg2.connect( host=self.hostname, user=self.username, password=self.password, dbname=self.database )
        except Exception as e:
            print(e, "Couldn't connect to database.")
        cur = conn.cursor()
        try:
            statement = create_ddl(csv_file, table_name)
            cur.execute(statement) # use your column names here

            if insert:
                with open(csv_file,'r') as f:
                    next(f)
                    cur.copy_from(f, table_name, sep, null = '')
                    conn.commit()
        
            print(self.q("select * from " + table_name + " limit 10;"))
            conn.close()

        except:
            conn.close()

    def create_table_from_df(self, df, table_name):
        df.to_csv('./temp.csv', index=False)
        self.create_table('temp.csv', table_name, insert=True)
        os.remove('./temp.csv')




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
    assert method in ['mean','median','zeros', 'mode'], 'Use mean, median, mode or zeros.'
    
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

def discretize_mult(df, col_bins, qcut = False):
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
        columns
    '''
    df = df.copy()
    for col, bins in col_bins.items():
        df[col] = discretize(df[col], bins=bins, qcut=qcut)

    return df













































































def dataType(val, current_type):
    try:
        # Evaluates numbers to an appropriate type, and strings an error
        t = ast.literal_eval(val)
    except ValueError:
        return 'VARCHAR'
    except SyntaxError:
        return 'VARCHAR'

    if type(t) in [int, float]:
        if (type(t) in [int]) and current_type not in ['float', 'varchar']:
           # Use smallest possible int type
            if (-32768 < t < 32767) and current_type not in ['int', 'bigint']:
                return 'SMALLINT'
            elif (-2147483648 < t < 2147483647) and current_type not in ['bigint']:
                return 'INT'
            else:
                return 'BIGINT'
        if type(t) is float and current_type not in ['varchar']:
            return 'FLOAT'
    else:
        return 'VARCHAR'


def create_ddl(file_path, table_name):
    f = open(file_path, 'r')
    reader = csv.reader(f)
    longest, headers, type_list = [], [] ,[]
    for row in reader:
        if len(headers) == 0:
            headers = row
            for col in row:
                longest.append(0)
                type_list.append('')
        else:
            for i in range(len(row)):
                # NA is the csv null value
                if type_list[i] == 'varchar' or row[i] == 'NA':
                    pass
                else:
                    var_type = dataType(row[i], type_list[i])
                    type_list[i] = var_type
                if len(row[i]) > longest[i]:
                    longest[i] = len(row[i])
    f.close()

    statement = 'CREATE TABLE ' + table_name + ' ('
    
    for i in range(len(headers)):
        if type_list[i] == 'VARCHAR':
            statement = (statement + '\n{} VARCHAR({}),').format(headers[i].
    lower(), str(longest[i]))
        else:
            statement = (statement + '\n' + '{} {}' + ',').format(headers[i]
    .lower(), type_list[i])
        if '-' in statement:
            statement = statement.replace('-','_')
    
    statement = statement[:-1] + ');'

    print(statement)
    edit = ''
    while edit not in ['Y', 'N']:
        edit = input('Do you want to make any changes? Y/N ').upper()
        edit = edit.upper()

    statement = make_edits(statement, edit)

    return statement



def make_edits(statement, edit):
    statement = statement.split('\n')
    last = len(statement)
    if edit == 'Y':
        for i, line in enumerate(statement[1:]):
            attribute, type_ = line.split(' ')[0], line.split(' ')[1] 
            s = attribute + " of type " + type_[:-1] + '? '
            fix = ''
            if fix not in ['s','varchar','int','real','smallint','text','char']:
                fix = input(s)
                fix_check = fix.split('(')[0].lower()
            if fix_check in ['y','s','']:
                continue
            else:
                type_ = ' ' + fix.upper() + ','
                statement[i+1] = str(line.split(' ')[0]) + type_
        if ');' not in statement[last-1]:
            statement[last-1] = statement[last-1][:-1] + ');'
        return '\n'.join(statement)
    else:
        return '\n'.join(statement)





