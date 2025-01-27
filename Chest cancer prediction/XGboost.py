import requests
import pandas as pd
from matplotlib import pyplot as plt
from pandas.core.common import random_state
from sklearn.pipeline import Pipeline
from category_encoders.target_encoder import TargetEncoder
from xgboost import XGBClassifier, plot_importance
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer


train_url = "https://huggingface.co/datasets/wwydmanski/wisconsin-breast-cancer/resolve/main/train.csv"
test_url = "https://huggingface.co/datasets/wwydmanski/wisconsin-breast-cancer/resolve/main/test.csv"

train_response = requests.get(train_url)
train_response.raise_for_status()

with open('wisconsin_breast_cancer_train.csv', 'wb') as file:
    file.write(train_response.content)

train_df = pd.read_csv('wisconsin_breast_cancer_train.csv')

test_response = requests.get(test_url)
test_response.raise_for_status()

with open('wisconsin_breast_cancer_test.csv', 'wb') as file:
    file.write(test_response.content)

test_df = pd.read_csv('wisconsin_breast_cancer_test.csv')

column_names = [
    'Index', 'Radius Mean', 'Texture Mean', 'Perimeter Mean', 'Area Mean', 'Smoothness Mean',
    'Compactness Mean', 'Concavity Mean', 'Concave Points Mean', 'Symmetry Mean', 'Fractal Dimension Mean',
    'Radius SE', 'Texture SE', 'Perimeter SE', 'Area SE', 'Smoothness SE',
    'Compactness SE', 'Concavity SE', 'Concave Points SE', 'Symmetry SE', 'Fractal Dimension SE',
    'Radius Worst', 'Texture Worst', 'Perimeter Worst', 'Area Worst', 'Smoothness Worst',
    'Compactness Worst', 'Concavity Worst', 'Concave Points Worst', 'Symmetry Worst', 'Fractal Dimension Worst',
    'Diagnosis'
]

train_df.columns = column_names
test_df.columns = column_names

train_df = train_df.drop(columns=['Index'])
test_df = test_df.drop(columns=['Index'])

#train_df.to_csv('cleaned_wisconsin_breast_cancer_train.csv', index=False)
#test_df.to_csv('cleaned_wisconsin_breast_cancer_test.csv', index=False)

train_df['Diagnosis'] = train_df['Diagnosis'].map({'M': 1, 'B': 0})
test_df['Diagnosis'] = test_df['Diagnosis'].map({'M': 1, 'B': 0})


correlation_matrix = train_df.corr()
diag_corr = correlation_matrix['Diagnosis'].drop('Diagnosis').sort_values(ascending=False)
important_feature = diag_corr[diag_corr > 0.67]
selected_features = list(important_feature.index) + ['Diagnosis']


filtered_train_df = train_df[selected_features]
filtered_test_df = test_df[selected_features]


X_train = filtered_train_df.drop(columns=['Diagnosis'])
y_train = filtered_train_df['Diagnosis']
X_test = filtered_test_df.drop(columns=['Diagnosis'])
y_test = filtered_test_df['Diagnosis']

estimators = [
    ('encoder', TargetEncoder()),
    ('clf', XGBClassifier(random_state=8))
]
pipe = Pipeline(steps=estimators)

search_space = {
    'clf__max_depth' : Integer(2,8),
    'clf__learning_rate' : Real(0.001, 1.0,prior='log-uniform'),
    'clf__subsample' : Real(0.5, 1.0),
    'clf__colsample_bytree' : Real(0.5, 1.0),
    'clf__colsample_bylevel' : Real(0.5, 1.0),
    'clf__colsample_bynode' : Real(0.5, 1.0),
    'clf__reg_alpha' : Real(0.0, 10.0),
    'clf__reg_lambda' : Real(0.0, 10.0),
    'clf__gamma': Real(0.0, 10.0)



}

opt = BayesSearchCV(pipe, search_space, cv=5, n_iter=10, scoring='roc_auc', random_state=8)
opt.fit(X_train, y_train)

print(f"the best estimator is {opt.best_estimator_}")

print(f"the best score{opt.best_score_}")

print(f"the accurate is{opt.score(X_test, y_test)}")


#print(opt.predict_proba(X_test))

###
opt.best_estimator_.steps

xgboost_step = opt.best_estimator_.steps[1]
xgboost_model = xgboost_step[1]

#print(plot_importance(xgboost_model))




plt.figure(figsize=(10, 8))
plot_importance(xgboost_model, importance_type='weight')
plt.title("Feature Importance")
plt.show()