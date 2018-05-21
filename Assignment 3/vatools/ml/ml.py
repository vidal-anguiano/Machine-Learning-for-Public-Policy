
import pandas as pd
import numpy as np
import json
from vatools.utils import data_processing as dp
from math import ceil
from datetime import datetime, date, timedelta
import csv

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.cross_validation import KFold

from sklearn.model_selection import ParameterGrid
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score, roc_auc_score, accuracy_score

all_methods = {'logit': LogisticRegression(),
               'dt': DecisionTreeClassifier(),
               'knn': KNeighborsClassifier(),
               'svm': SVC(probability=True),
               'rf': RandomForestClassifier(),
               'gbc': GradientBoostingClassifier(),
               'bag': BaggingClassifier(),
               'bnb': BernoulliNB(),
               'mnb': MultinomialNB()}


''' *** PIPELINE *** '''

def mlpipeline(data, features, outcome, test_size = .5, methods = None,
                        param_file = '../mlparams.json', temporal = None,
                        date_col = None, n_folds):
    '''
    Creates train test splits (temporal optional) and trains machine learning
    learning models using methods and parameters of choice.
    '''
    if temporal:
        for dates in date_intervals(**temporal):
            print(dates)
            (X_train, y_train,
            X_test, y_test) = temporal_split(data, date_col, features, outcome, **dates)
            classify(X_train, y_train, X_test, y_test, methods=methods, param_file=param_file)
    else:
        # kf = KFold(n_splits=n_folds, shuffle=True)
        # X = data[features]
        # y = data[outcome]
        #
        # for train_index, test_index in kf.split(X[features]):
        #     train_test = (X[train_index], y[train_index],
        #                   X[test_index],  y[test_index])
        #     classify(*train_test, methods, param_file)
        return "Currently being developed, come back soon."

def classify(X_train, y_train, X_test, y_test, param_file = '../mlparams.json'
                                                             ,methods = None):
    ''' Build multiple models using serveral methods and parameters. '''
    if not methods:
        methods = list(all_methods)

    params = json.load(open(param_file))
    models = []
    for method in methods:
        m_id = 0
        for param_set in ParameterGrid(params[method]):
            m_id += 1
            model = all_methods[method].set_params(**param_set).fit(X_train, y_train)
            pred_proba = model.predict_proba(X_test)[:,1]
            for pred_thresh in range(5,10):
                metrics = evaluate(y_test, pred_proba, pred_thresh*.1)
                print('Method: {} | Parameters: {} | Pred_Threshold: {:.1f}'.format(
                                                 method, param_set, pred_thresh*.1))
                models.append([m_id, method, param_set, pred_thresh*.1,
                               metrics['precision'], metrics['precision'][1],
                               metrics['recall'], metrics['recall'][1],
                               metrics['roc_auc'], metrics['accuracy']])

    results = create_results_df(models, '../results/results_run_on_{}.csv'.format(
                                                            dp.current_time_str()))

    return results

# def classify_kfold(X, Y, param_file = '../mlparams.json',methods = None):
#     if not methods:
#         methods = list(all_methods)
#     kf = KFold(n_splits=n_folds, shuffle=True)
#     params = json.load(open(param_file))
#     models = []
#     for method in methods:
#         m_id = 0
#         for param_set in ParameterGrid(params[method]):
#             m_id += 1
#             columns=['threshold','percision','recall','auc_roc','accuracy']
#             metrics = pd.DataFrame(columns=['threshold','percision','recall','auc_roc','accuracy'])
#             for train_index, test_index in kf.split(X):
#                 train_test = (X[train_index], y[train_index],
#                               X[test_index],  y[test_index])
#                 model = all_methods[method].set_params(**param_set).fit(X_train, y_train)
#                 pred_proba = model.predict_proba(X_test)[:,1]
#                 for pred_thresh in range(5,10):
#                     metrics = evaluate(y_test, pred_proba, pred_thresh*.1)
#                     print('Method: {} | Parameters: {} | Pred_Threshold: {:.1f}'.format(
#                                                  method, param_set, pred_thresh*.1))
#                 models.append([m_id, method, param_set, pred_thresh*.1,
#                                metrics['precision'], metrics['precision'][1],
#                                metrics['recall'], metrics['recall'][1],
#                                metrics['roc_auc'], metrics['accuracy']])
#
#     results = create_results_df(models, '../results/results_run_on_{}.csv'.format(
#                                                             dp.current_time_str()))
#
#     return results


''' *** EVALUATION *** '''

def evaluate(y_test, pred_proba, pred_thresh):
    '''
    Returns precision, recall, roc_auc, and accuracy evaluation metrics.
    '''
    pred = (pred_proba > pred_thresh).astype(int)
    df = pd.DataFrame({'y_test': y_test,
                       'pred': pred,
                       'pred_proba': pred_proba}).sort_values(by = 'pred_proba',
                                                              ascending = False)

    precision, recall = precision_recall_at_intervention_levels(df)
    y_test, pred, pred_proba  = df['y_test'], df['pred'], df['pred_proba']

    metrics = {}
    metrics['precision'] = precision
    metrics['recall'] = recall
    metrics['roc_auc'] = roc_auc_score(y_test, pred_proba)
    metrics['accuracy'] = accuracy_score(y_test, pred)

    return metrics


''' HELPER FUNCTIONS '''

def precision_recall_at_intervention_levels(df):
    ''' Helper function for calculating precision at different levels. '''
    precision, recall = {}, {}
    for pr_at in [.01, .02, .05, .1, .2, .3, .5, 1]:
        cutoff = ceil(len(df)*pr_at)
        sdf = df.iloc[:cutoff]
        y_test, pred = sdf['y_test'], sdf['pred']
        TP = len(sdf[(sdf['pred'] == 1) & (sdf['y_test'] == 1)])
        P = len(df[df['y_test'] == 1])
        recall[pr_at] = round(TP/(P if P != 0 else 1), 2)
        precision[pr_at] = round(precision_score(y_test, pred), 2)

    return precision, recall

def date_intervals(start_date, train_months, test_months, gap_months = 0,
                                     periods = 1, increment_months = 12):
    ''' Helper function for creating date intervals to split data on. '''
    start_date = datetime.strptime(start_date,'%m/%d/%Y').date()
    dates = []
    for i in range(0,periods):
        train_end = ymddelta(start_date, d_months = train_months)
        test_start = ymddelta(train_end, d_months = gap_months)
        test_end = ymddelta(test_start, d_months = test_months)
        dates.append({'train_start':start_date,
                      'train_end':train_end,
                      'test_start':test_start,
                      'test_end':test_end})
        start_date = ymddelta(start_date, d_months = increment_months)
    return dates


def temporal_split(data, date_col, features, outcome, train_start, train_end,
                                                      test_start, test_end):
    ''' Create temporal train test splits. '''
    data[date_col] = data[date_col].astype('datetime64[ns]')
    train = data[(data[date_col] >= train_start) & (data[date_col] <= train_end)]
    test = data[(data[date_col] >= test_start) & (data[date_col] <= test_end)]

    X_train, y_train = train[features], train[outcome]
    X_test, y_test = test[features], test[outcome]

    return X_train, y_train, X_test, y_test


def ymddelta(dt, d_years=0, d_months=0, first=False):
    '''
        d_years, d_months are "deltas" to apply to dt
        still need to implement d_days
    '''
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    if first:
        return date(y+a, m+1, 1)
    try:
        return date(y+a, m+1, 1)
    except:
        if m+1 == 2:
            return date(y+a, m+1, 28)
        else:
            return date(y+a, m+1, 30)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)


def create_results_df(models, filename):
    ''' Helper function for exporting results dataframe. '''
    df = pd.DataFrame(models, columns=['m_id','method','parameters','pred_threshold',
                                       'all_precicion','precision','all_recall',
                                       'recall','roc_auc','accuracy'])
    df.to_csv(filename)
    return df
