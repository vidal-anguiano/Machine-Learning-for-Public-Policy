import pandas as pd
import csv, ast, psycopg2
import os
import json
from vatools.src.util import *



class db_connection(object):
    def __init__(self, credentials_file):
        creds = json.load(open(credentials_file))
        self.hostname = creds["hostname"]
        self.username = creds["username"]
        self.password = creds["password"]
        self.database = creds["database"]

    def query(self, query, pandas = True):
        conn = psycopg2.connect( host=self.hostname, user=self.username,
                          password=self.password, dbname=self.database )
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
            conn = psycopg2.connect( host=self.hostname, user=self.username,
                              password=self.password, dbname=self.database )
        except Exception as e:
            print(e, "Couldn't connect to database.")
        cur = conn.cursor()
        try:
            statement = create_ddl(csv_file, table_name)
            cur.execute(statement) # use your column names here

            if insert:
                print('Gets HERE')
                with open(csv_file,'r') as f:
                    next(f)
                    print('GETS HERE TOO')
                    cur.copy_from(f, table_name, sep, null = '')
                    conn.commit()

            print(self.query("select * from " + table_name + " limit 10;"))
            conn.close()

        except Exception as e:
            print(e)
            conn.close()

    def create_table_from_df(self, df, table_name):
        df.to_csv('./temp.csv', index=False)
        self.create_table('temp.csv', table_name, insert=True)
        os.remove('./temp.csv')



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
