"""
Model is a generic machine learning model pipeline with basic functions
for loading data, cleaning the data, building and evaluating a model.

@author: Vidal Anguiano Jr.
"""
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals.six import StringIO
from subprocess import call
from IPython.core.display import Image
import os
from sklearn.metrics import confusion_matrix


class Model(object):
    """
    Model is a generic machine learning model pipeline with basic functions
    for loading data, cleaning the data, building and evaluating a model.
    """

    def __init__(self, dataset, model_features):
        self.dataset_name = dataset.name
        self.features_train = dataset.train_set.iloc[:, model_features]
        self.features_test = dataset.test_set.iloc[:, model_features]
        self.feature_names = dataset.column_names[1:]
        self.outcome_train = dataset.train_set.iloc[:,0]
        self.outcome_test = dataset.test_set.iloc[:, 0]
        self.outcome_name = dataset.column_names[0]

    def __repr__(self):
        return '''Trained on {} data.\nTraining set has {} records.\
        \nTest set has {} records.'''.format(self.dataset_name,
                                                     len(self.features_train),
                                                     len(self.features_test))

class Tree(Model):
    def __init__(self, dataset, model_features, max_depth = 2,
                 min_samples_split = 2,min_samples_leaf = 10,
                 max_features = 'auto'):
        super().__init__(dataset, model_features)
        model = DecisionTreeClassifier(max_depth=max_depth,
                                       min_samples_split=min_samples_split,
                                       min_samples_leaf=min_samples_leaf,
                                       max_features=max_features)
        self.fitted_model = model.fit(self.features_train, self.outcome_train)
        self.class_probabilities = model.predict_proba(self.features_test)
        self.predictions = model.predict(self.features_test)
        self.model_features = model_features

    def visualize(self, notebook = True):
        '''
        Visualize fitted model in JupyterNotebook or with default image viewer.
        Inputs:
            - notebook (bool): default, True. If True, tree image will show in
            JupyterNotebook. Otherwise, it will open with the users' default
            image viewing software.
        Outputs:
            'tree.png' will be generated and displayed in JupyterNotebook
        '''
        with open("tree.dot", 'w') as f:
            f = tree.export_graphviz(self.fitted_model, out_file = f)
        call("dot -Tpng tree.dot -o tree.png", shell=True)
        if not notebook:
            call("xdg-open tree.png",shell=True)
        else:
            tree_features(self.feature_names, self.model_features)
            return Image('tree.png')


    def predict(self, threshold):
        predictions = (self.class_probabilities[:,1] > threshold).astype(int)
        return confusion_matrix(self.outcome_test.values, predictions)





def tree_features(columns, model_features):
    '''
    Helper function for relating the X[_] label format of the decision tree
    image output to the features used in training the model.
    '''
    string = ''
    for i, col in enumerate(model_features):
        string += "X[{}] is {}\n".format(i,columns[col-1])
    print(string)
