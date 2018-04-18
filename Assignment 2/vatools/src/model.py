"""
Model is a generic machine learning model pipeline with basic functions
for loading data, cleaning the data, building and evaluating a model.

@author: Vidal Anguiano Jr.
"""
import pandas as pd
import itertools
import matplotlib.pyplot as plt
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
        '''
        Initializes a Model class with training and test set features and
        outcomes.
        Inputs:
            - dataset (DataSet class): preprocessed DataSet
            - model_features(list of integers): input a list of integers
            corresponding to the features to use in the model
        '''
        self.dataset_name = dataset.name
        self.features_train = dataset.train_set.iloc[:, model_features]
        self.features_test = dataset.test_set.iloc[:, model_features]
        self.feature_names = dataset.train_set.columns
        self.outcome_train = dataset.train_set.iloc[:, 0]
        self.outcome_test = dataset.test_set.iloc[:, 0]
        self.outcome_name = dataset.column_names[0]


    def __repr__(self):
        '''
        Function to represent model class.
        '''
        return '''Trained on {} data.\nTraining set has {} records.\
        \nTest set has {} records.'''.format(self.dataset_name,
                                                     len(self.features_train),
                                                     len(self.features_test))


class Tree(Model):
    '''
    Subclass of the Model class. Model functionality is extended to be used
    specifically for decision tree models.
    '''
    def __init__(self, dataset, model_features, max_depth = 2,
                 min_samples_split = 2,min_samples_leaf = 10,
                 max_features = 'auto'):
        '''
        Initializes a Tree model using the Model class as a parent class.
        Inputs:
            - dataset (DataSet class): preprocessed DataSet
            - model_features(list of integers): input a list of integers
            corresponding to the features to use in the model
            - max_depth (int or None): The maximum depth of the tree
            - min_samples_split (int, float): The minimum number of samples
            required to split an internal node
            - min_samples_leaf (int, float): The minimum number of samples
            required to be at a leaf node
            - max_features (int, float, string, or None): The number of features
            to consider when looking for the best split

        '''
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


    def confusion_matrix(self, threshold):
        '''
        For a given probability threshold, predictions are made and plotted on a
        confusion matrix.
        Inputs:
            - threshold (float): threshold for probability that a given case is
            positive, which is used to produce predictions
        Outputs:
            - prints two confusion matrices, one based on the counts and the
            second is normalized
        '''
        predictions = (self.class_probabilities[:,1] > threshold).astype(int)
        cm = confusion_matrix(self.outcome_test.values, predictions)
        plt.figure()
        plot_confusion_matrix(cm, classes=[0,1], title='Confusion Matrix')
        plt.figure()
        plot_confusion_matrix(cm, classes=[0,1], normalize=True,title='Confusion Matrix, Normalized')
        plt.show()


def tree_features(columns, model_features):
    '''
    Helper function for relating the X[_] label format of the decision tree
    image output to the features used in training the model.
    '''
    string = ''
    for i, col in enumerate(model_features):
        string += "X[{}] is {}\n".format(i,columns[col])
    print(string)


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    Source: http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
