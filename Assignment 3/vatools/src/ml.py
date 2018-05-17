
import pandas as pd
from math import ceil
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import BaggingClassifier

from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score, recall_score, roc_auc_score, accuracy_score



def decision_trees(X_train, y_train, X_test, y_test, max_depths = None, pred_thresh = .5):
    '''
    INSERT DOCSTRING.
    '''
    max_depths = [2, 3, 4, 5, 6, 7]
    for md in max_depths:
        d_tree = DecisionTreeClassifier(max_depth=md)
        d_tree.fit(X_train, y_train)
        pred_probs = d_tree.predict_proba(X_test)[:,1]

        # evaluate accuracy
        train_acc = accuracy(train_pred, y_train)
        precision, recall, roc_auc, accuracy = evaluate(y_test, test_pred, top)

        print("Depth: {} | Train Acc: {:.2f} | ".format(d, train_acc) +
              "Test Acc: {:.2f} | Prec: {:.2f} | ".format(acc, pre) +
              "Recall: {:.2f} | ROC AUC {:.2f}".format(recall, roc_auc))


def evaluate(test_outcomes, pred_probs, pred_tresh, top = None):
    '''
    INSERT DOCSTRING.
    '''
    predictions = (pred_probs > pred_thresh).astype(int)
    df = pd.DataFrame({'test_outcomes': test_coutcomes,
                       'predictions': predictions,
                       'pred_probs': pred_probs}).sort_values(by = 'pred_probs',
                                                              ascending = False)
    if top:
        cutoff = ceil(len(df)*top)
        df = df[df['pred_probs'] >= cutoff]

    test_outcomes = df['test_outcomes'].tolist()
    predictions = df['predictions'].tolist()
    pred_probs = df['pred_probs']

    precision = precision_score(test_outcomes, predictions)
    recall = recall_score(test_outcomes, predictions)
    roc_auc = roc_auc_score(test_outcomes, predictions)
    accuracy = accuracy_score(test_outcomes, pred_probs)

    return precision, recall, roc_auc, accuracy
