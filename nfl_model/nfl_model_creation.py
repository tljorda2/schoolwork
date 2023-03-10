# -*- coding: utf-8 -*-
"""NFL Model Creation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I4xG6X6bgfHjLjIC60f5jK_xLTWSuqMF
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GridSearchCV 
# %pip install git+https://github.com/hyperopt/hyperopt-sklearn@master

# Setting up path
from google.colab import drive
drive.mount('/content/drive/')

# Checking the intial dataframe we made from the data preparation
# This contains the per game stats
# Need to merge these into the game by game dataframe in order to run the models
Model_DF = pd.read_csv('/content/drive/MyDrive/CIS 450 Team Project/NFL Data/Model_DF.csv')
Model_DF.info()

# Noticed that there are two repeated columns
# List of columns to drop
drop_col = ['Offensive_Sc%', 'O_TO%', 'D_TO%', 'D_Sc%']
Model_DF.drop(columns=drop_col, inplace=True)
Model_DF.info()

# Getting the schedule dataframe
# Using pd.read_html to read the dataframe from the website
Games_df = pd.read_html('https://www.pro-football-reference.com/years/2022/games.htm')
Games_df = Games_df[0]
# Sorting these values to split the df into home and away games
Games_df.sort_values('Unnamed: 5')
away_gamesdf = Games_df[Games_df['Unnamed: 5'] == '@']
home_gamesdf = Games_df[Games_df['Unnamed: 5'] != '@']

# I want to create a dummy variabel for whether or not the home team won
# The current direction I am working towards is to eventually combine the stats and games dataframes
# In order to use team stats to predict matchups
# Since in the original dataframe all of the winners were on the left column titled "Winners/tie" I can create
# dummy variables like this.
home_gamesdf['Home_Win'] = 1
away_gamesdf['Home_Win'] = 0
# Assigning column values to a temporary dataframe to swap the values
#define function to swap columns
def swap_columns(df, col1, col2):
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df

swap_columns(home_gamesdf, 'Winner/tie', 'Loser/tie')

home_gamesdf.rename(columns={'Loser/tie':'Away','Winner/tie': 'Home'}, inplace=True)
away_gamesdf.rename(columns={'Winner/tie':'Away','Loser/tie': 'Home'}, inplace=True)
Games_df = home_gamesdf.append(away_gamesdf)
#Games_df = Games_df.drop(columns=['Unnamed: 5', 'Unnamed: 7', 'PtsW', 
                                  #'PtsL','YdsW','YdsL','TOW', 'TOL'])
# For SQL Server
Games_df = Games_df.drop(columns=['Unnamed: 5', 'Unnamed: 7'])


#print(Games_df[(Games_df['Away'] == 'New England Patriots') | (Games_df['Home'] == 'New England Patriots')])
# %%
# This section merges the individuasl games dataframe with the overall team stats
# This allows me to use the overall stats to predict the outcome of the games
# I am using a left join to keep everything in line with the original games dataframe
Model_DataFrame = pd.merge(left=Games_df, right=Model_DF, how='left', left_on='Away', right_on='Tm')
Model_DataFrame = pd.merge(left=Model_DataFrame, right=Model_DF, how='left', left_on='Home', right_on='Tm')
Model_DataFrame.dropna(axis=0, inplace=True)
Model_DataFrame.info()

# Final Cleaning of the df
drop_col = ['Week', 'Day', 'Date', 'Time', 'PtsW', 'PtsL', 'YdsW', 'TOW', 'YdsL', 'TOL', 'Unnamed: 0_x', 'Tm_x', 'Tm_y', 'Unnamed: 0_y']
Model_DataFrame.drop(columns=drop_col, inplace=True)
Model_DataFrame

# Creating X and Y
X = Model_DataFrame.drop(columns=['Home', 'Away', 'Home_Win'])
y = Model_DataFrame['Home_Win']
X.info()

# ngl this is a mess
# Deleted O_EXP
# Potential Drop columns
'''
drop_col = [
    'DRush_Att_x', 'DRush_Att_y', 'Yds_x', 'Yds_y', 'Off_Att_x', 'Off_Att_y', 'Off_Cmp_x', 'Off_Cmp_y',
    'ORush_Yds_x', 'ORush_Yds_y', 'OPenn_Yds_x', 'OPenn_Yds_y', 'DPass_Att_x', 'DPass_Att_y', 'D_Pen_x', 'D_Pen_y',
    'Offensive_TO%_x', 'Offensive_TO%_y', 'ORush_Att_x', 'ORush_Att_y', 'MoV_x', 'MoV_y'
            ]
'''
drop_col = [
    'DRush_Att_x', 'DRush_Att_y', 'Yds_x', 'Yds_y', 'Off_Att_x', 'Off_Att_y', 'Off_Cmp_x', 'Off_Cmp_y',
    'ORush_Yds_x', 'ORush_Yds_y', 'OPenn_Yds_x', 'OPenn_Yds_y', 'DPass_Att_x', 'DPass_Att_y', 'D_Pen_x', 'D_Pen_y',
    'Offensive_TO%_x', 'Offensive_TO%_y', 'ORush_Att_x', 'ORush_Att_y', 'MoV_x', 'MoV_y', 'FL_x', 'FL_y', 'ORush_Y/A_x', 'ORush_Y/A_y'
            ]
X = X.drop(columns=drop_col)

# This is showing the correlation between each of the inputs
# The cell above are some of the variables I have decided to filter out since they have very high correlation with several other inputs
# The heatmaps are seperated into offensive and defensive stats
temp_df = X.iloc[:, :30]
matrix = temp_df.corr()
plt.figure(figsize=(30,30))
_ = sns.heatmap(matrix, annot=True)

temp_df = X.iloc[:, 30:63]
matrix2 = temp_df.corr()
plt.figure(figsize=(30,30))
_ = sns.heatmap(matrix2, annot=True)

# Creating a bar chart to show the count of wins vs losses for the home team

dt = y.value_counts(0)
x_1 = ['no', 'yes']
y_2 = [dt[0], dt[1]]
plt.bar(x_1, y_2)
plt.show
plt.title('NFL Game Home Wins')
plt.xlabel('Home Win?')
plt.ylabel('Count of Wins')

from sklearn.preprocessing import MinMaxScaler, Normalizer, RobustScaler
from scipy import stats
# Creating an instance of the sklearn.preprocessing.MinMaxScaler()
scaler = MinMaxScaler()
# Checking for outliers since I am scalinbg the data as a test
# If there are any outliers, I do not want to scale that column, but there does not appear to be
X[(np.abs(stats.zscore(X)) < 3).all(axis=1)]
X.info()
# Scaling the data from 0 to 1
# Columns to not scale:
ns_col = ['W-L%_x', 'W-L%_y']
for col in X:
  if col in ns_col:
    pass
  else:
    X[[col]] = scaler.fit_transform(X[[col]])
X.info()

X = X[['O_TotalYds_y', 'O_TotalYds_x', 'W-L%_x', 'W-L%_y', '1stD_y', '1stD_x', 'O_EXP_y', 'O_EXP_x', 'D_PA_y', 'D_PA_x', 'SRS_x', 'SRS_y', 'D_1stD_x', 'D_1stD_y']]
X

# Splitting the data into a train/test set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=100)
#Getting the value counts of each
print(y_train.value_counts(0))
print(y_train.value_counts(1))

"""Creating a function for when I want to use Cross Fold Validation"""

#Importing the metrics we are going to use
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_validate
from sklearn.metrics import classification_report
from sklearn import metrics
target = ['Away Team Won', 'Home Team Won']
# Defining a dictionary of metrics
score_metrics = {'accuracy':make_scorer(accuracy_score),
                 'precision': make_scorer(precision_score),
                 'recall': make_scorer(recall_score),
                 'f1_score': make_scorer(f1_score)}

# Since I will be constantly repeating these lines of codes with few changes, I decided to make a function
# With the inputs being what is mostly going to be changed throughout the file.
def RunModel(model, folds=10):
    if type(folds) == int:
        pass
    else:
        raise TypeError('The number of folds has to be an integer')
    scores = cross_validate(model, X, y, cv=folds, scoring=score_metrics)
    print('Avg Accuracy: '+str(np.mean(scores['test_accuracy'])))
    print('Avg Precision: '+str(np.mean(scores['test_precision'])))
    print('Avg Recall: '+str(np.mean(scores['test_recall'])))
    print('Avg F1-Score: '+str(np.mean(scores['test_f1_score'])))
    return np.mean(scores['test_accuracy'])

from sklearn.ensemble import RandomForestClassifier
# Classifier
random_forest = RandomForestClassifier(bootstrap=False, criterion='entropy', max_depth=3,
                       max_features='sqrt', min_samples_leaf=15,
                       n_estimators=10, n_jobs=1, random_state=0,
                       verbose=False)
random_forest.fit(X_train, y_train)
# Accuracy
y_pred = random_forest.predict(X_test)
# Printing the classification report
print('Random Forest\n----------------')
print(classification_report(y_test, y_pred, target_names=target))
RandomForest_Accuracy = metrics.accuracy_score(y_test, y_pred)


feature_imp = pd.Series(random_forest.feature_importances_, index=X_train.columns).sort_values(ascending=False)
print(feature_imp[:15])

RunModel(random_forest, 10)

from hyperopt import tpe
from hpsklearn import HyperoptEstimator, random_forest_classifier, min_max_scaler, any_preprocessing
# Creating a function that will be used for each iteration through the optimization

# Instantiate a HyperoptEstimator with the search space and number of evaluations
estim = HyperoptEstimator(classifier=random_forest_classifier('my_gbe'),
                          preprocessing=[],
                          algo=tpe.suggest,
                          max_evals=30,
                          trial_timeout=120)

# Search the hyperparameter space based on the data
estim.fit(X_train, y_train)

# Show the results
print(estim.score(X_test, y_test))

print(estim.best_model())

'''Gradient Boost Ensemble'''
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
# This is the method that assigns a higher weighted value to wrong predicitions.
# Learning rate is a range from 0 to 1 that signifiers how much weight the model will put on wrong predicitons

gbe = GradientBoostingClassifier(criterion='squared_error',
                           learning_rate=0.0020624990620836817, max_depth=5,
                           min_samples_leaf=17, n_estimators=451,
                           random_state=3, verbose=False)
gbe.fit(X_train, y_train)
y_pred = gbe.predict(X_test)

print('Gradient Boost Ensemble, Using HyperOpt')
print('\n-------------')
print(classification_report(y_test, y_pred, target_names=target))
GradientBoost_Accuracy = metrics.accuracy_score(y_test, y_pred)

# calculate the fpr and tpr for all thresholds of the classification
probs = gbe.predict_proba(X_test)
preds = probs[:,1]
# fpr is false positive, tpr is true positive
fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
roc_auc = metrics.auc(fpr, tpr)

# Plotting ROC Curve
plt.title('ROC Curve')

plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

RunModel(gbe, 20)

"""Attempting to optimize the Gradient Boost Model"""

# Attempting to optimize the model
# Using the HyperOpt package in order to iterate through various hyperparamters to optimize the model
# Dictionary below represent the parameters that we are wanting to adjust, as well as the ranges we want to look at
# For example, we do not want the max_depth to be so high that model is overfit
# We set the range 3 to 18
# quniform gives whole numbers while uniform will give a float
from hyperopt import tpe
from hpsklearn import HyperoptEstimator, gradient_boosting_classifier, min_max_scaler, any_preprocessing
# Creating a function that will be used for each iteration through the optimization

# Instantiate a HyperoptEstimator with the search space and number of evaluations
estim = HyperoptEstimator(classifier=gradient_boosting_classifier('my_gbe', max_depth=6),
                          preprocessing=[],
                          algo=tpe.suggest,
                          max_evals=50,
                          trial_timeout=120)

# Search the hyperparameter space based on the data
estim.fit(X_train, y_train)

# Show the results
print(estim.score(X_test, y_test))

print(estim.best_model())

'''Neural Network'''
from sklearn.neural_network import MLPClassifier
#Creating a neural net classifier
#nn = MLPClassifier(hidden_layer_sizes=(3,11), random_state=2, max_iter=1000)
nn = MLPClassifier(alpha=0.007401220077585274, beta_1=0.9921401316428486,
              beta_2=0.9739552674041522, epsilon=2.6501746357923418e-06,
              learning_rate='invscaling',
              learning_rate_init=0.05865349829728565, max_fun=11771,
              max_iter=340, momentum=0.869182702330667, n_iter_no_change=20,
              power_t=0.6610992785666377, random_state=4,
              tol=0.00456557391542561, validation_fraction=0.10042542558002383)

#Training the model
nn.fit(X_train, y_train)

#Prediciting the outcomes
y_pred = nn.predict(X_test)

print('Neural Network\nUsing HyperOpt')
print('\n--------------')
print(classification_report(y_test, y_pred, target_names=target))


# calculate the fpr and tpr for all thresholds of the classification
probs = nn.predict_proba(X_test)
preds = probs[:,1]
# fpr is false positive, tpr is true positive
fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
roc_auc = metrics.auc(fpr, tpr)

# Plotting ROC Curve
plt.title('ROC Curve')
plt.plot(fpr, tpr, 'g', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

#Accuracy Variable
NeuralNet_Accuracy = metrics.accuracy_score(y_test, y_pred)

y_actual = pd.Series(y_test, name='Actual')
y_predicted = pd.Series(y_pred, name='Predicted')
print('\nNN Confusion Matrix\n--------------')
print(metrics.confusion_matrix(y_actual, y_predicted))
# Cross Fold for NN
print('\nCross Fold Validation\n--------------')
nn_cf = RunModel(nn, 50)

"""TESTING NN"""

'''Neural Network'''
from sklearn.neural_network import MLPClassifier
#Creating a neural net classifier
#nn = MLPClassifier(hidden_layer_sizes=(3,11), random_state=2, max_iter=1000)
nn = MLPClassifier(activation='identity', alpha=0.008750287451038829,
              beta_1=0.9199802415174151, beta_2=0.9886762688271048,
              epsilon=4.101497923367939e-06, hidden_layer_sizes=(114,),
              learning_rate='adaptive', learning_rate_init=0.03772345045694946,
              max_fun=14266, max_iter=1000, momentum=0.9931107364386774,
              power_t=0.30126480085530155, random_state=2,
              tol=0.0037296117695852665,
              validation_fraction=0.11153234640017175)
#Training the model
nn.fit(X_train, y_train)

#Prediciting the outcomes
y_pred = nn.predict(X_test)

print('Neural Network\nUsing HyperOpt')
print('\n--------------')
print(classification_report(y_test, y_pred, target_names=target))


# calculate the fpr and tpr for all thresholds of the classification
probs = nn.predict_proba(X_test)
preds = probs[:,1]
# fpr is false positive, tpr is true positive
fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
roc_auc = metrics.auc(fpr, tpr)

# Plotting ROC Curve
plt.title('ROC Curve')
plt.plot(fpr, tpr, 'g', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()

#Accuracy Variable
NeuralNet_Accuracy = metrics.accuracy_score(y_test, y_pred)

y_actual = pd.Series(y_test, name='Actual')
y_predicted = pd.Series(y_pred, name='Predicted')
print('\nNN Confusion Matrix\n--------------')
print(metrics.confusion_matrix(y_actual, y_predicted))
# Cross Fold for NN
print('\nCross Fold Validation\n--------------')
nn_cf = RunModel(nn, 20)

from hpsklearn import HyperoptEstimator, mlp_classifier, min_max_scaler, any_preprocessing
from hyperopt import tpe, hp

# Creating a function that will be used for each iteration through the optimization
# Instantiate a HyperoptEstimator with the search space and number of evaluations
estim = HyperoptEstimator(classifier=mlp_classifier('my_clf', max_iter=100000, hidden_layer_sizes=(114,)
              #activation='identity', alpha=0.008750287451038829, max_iter=10000
              #beta_1=0.9199802415174151, beta_2=0.9884729555030717,
              #epsilon=4.101497923367939e-06, learning_rate_init=0.039,
              #max_fun=14266, max_iter=1000, momentum=0.9931107364386774,
              #power_t=0.30126480085530155, random_state=2,
              #tol=0.0037296117695852665, validation_fraction=0.07630164245114593
              ),
                          preprocessing=any_preprocessing('my_pre'),
                          algo=tpe.suggest,
                          max_evals=1500,
                          trial_timeout=150)

# Search the hyperparameter space based on the data
estim.fit(X_train, y_train)

# Show the results
print(estim.score(X_test, y_test))
# 1.0

print(estim.best_model())

'''Logistic Regression'''
# Comparison between the re sampled data and the original data
from sklearn.linear_model import LogisticRegression
# Fitting and running the model for the resampled data
model = LogisticRegression(max_iter=10000)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print('Logistic Regression')
print(classification_report(y_test, y_pred, target_names=target))
# Storing the accuracy score as a variable to use in a plot
Logistic_Accuracy = metrics.accuracy_score(y_test, y_pred)

# calculate the fpr and tpr for all thresholds of the classification
probs = model.predict_proba(X_test)
preds = probs[:,1]
# fpr is false positive, tpr is true positive
fpr, tpr, threshold = metrics.roc_curve(y_test, preds)
roc_auc = metrics.auc(fpr, tpr)

# Plotting ROC Curve
plt.title('ROC Curve')

plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()
RunModel(model, 20)

# Actual Classification Tree code below
from sklearn import tree
from sklearn import metrics
from sklearn.metrics import classification_report
# Currently running with a depth of 5
cif = tree.DecisionTreeClassifier(criterion='entropy', max_depth=3,
                       max_features=0.4924978859010125, random_state=4,
                       splitter='random')

cif = cif.fit(X_train,y_train)
### This predicts the response
y_pred = cif.predict(X_test)

### This gives you the accuracy of your predictions
print(metrics.accuracy_score(y_test, y_pred))

print(classification_report(y_test, y_pred, target_names=target))

RunModel(cif, 50)

, decision_tree_classifier
from hpsklearn import HyperoptEstimator, decision_tree_classifier, min_max_scaler
from hyperopt import tpe, hp

# Creating a function that will be used for each iteration through the optimization
# Instantiate a HyperoptEstimator with the search space and number of evaluations
estim = HyperoptEstimator(classifier=decision_tree_classifier('my_clf'),
                          preprocessing=[],
                          algo=tpe.suggest,
                          max_evals=100,
                          trial_timeout=150)

# Search the hyperparameter space based on the data
estim.fit(X_train, y_train)

# Show the results
print(estim.score(X_test, y_test))
# 1.0

print(estim.best_model())

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif



#feature selection using f_classif
fs = SelectKBest(score_func=f_classif, k=5)
fit = fs.fit(X_train,y_train)
#create df for scores
dfscores = pd.DataFrame(fit.scores_)
#create df for column names
dfcolumns = pd.DataFrame(X_train.columns)

#concat two dataframes for better visualization 
featureScores = pd.concat([dfcolumns,dfscores],axis=1)
#naming the dataframe columns
featureScores.columns = ['Selected_columns','Score_ANOVA'] 
#print 10 best features
print(featureScores.nsmallest(15,'Score_ANOVA'))

