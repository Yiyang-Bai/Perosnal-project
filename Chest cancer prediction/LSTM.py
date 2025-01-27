import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import accuracy_score
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam


train_url = "https://huggingface.co/datasets/wwydmanski/wisconsin-breast-cancer/resolve/main/train.csv"
test_url = "https://huggingface.co/datasets/wwydmanski/wisconsin-breast-cancer/resolve/main/test.csv"

train_response = requests.get(train_url)
train_response.raise_for_status()
with open('wisconsin_breast_cancer_train.csv', 'wb') as file:
    file.write(train_response.content)

test_response = requests.get(test_url)
test_response.raise_for_status()
with open('wisconsin_breast_cancer_test.csv', 'wb') as file:
    file.write(test_response.content)

train_df = pd.read_csv('wisconsin_breast_cancer_train.csv')
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


train_df['Diagnosis'] = train_df['Diagnosis'].map({'M': 1, 'B': 0})
test_df['Diagnosis'] = test_df['Diagnosis'].map({'M': 1, 'B': 0})


correlation_matrix = train_df.corr()
diag_corr = correlation_matrix['Diagnosis'].drop('Diagnosis').sort_values(ascending=False)
important_feature = diag_corr[diag_corr > 0.67]
print(important_feature)
selected_features = list(important_feature.index) + ['Diagnosis']


filtered_train_df = train_df[selected_features]
filtered_test_df = test_df[selected_features]


X_train = filtered_train_df.drop(columns=['Diagnosis'])
y_train = filtered_train_df['Diagnosis']
X_test = filtered_test_df.drop(columns=['Diagnosis'])
y_test = filtered_test_df['Diagnosis']


X_train = X_train.fillna(0)
X_test = X_test.fillna(0)


scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

#  change to lstm input  (samples, timesteps, features)
X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
print(X_train_lstm)

# built lstm model
model = Sequential()
model.add(LSTM(3000, activation='tanh', return_sequences=True, input_shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(3000, activation='tanh'))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))

optimizer = Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])


stop_epoches = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = model.fit(X_train_lstm, y_train, epochs=200, batch_size=128, validation_data=(X_test_lstm, y_test), callbacks=[stop_epoches])

y_train_pred = (model.predict(X_train_lstm) > 0.5).astype(int)
y_test_pred = (model.predict(X_test_lstm) > 0.5).astype(int) 

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

# Plot training and validation accuracy
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training vs Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

print(f'training set accuracy: {train_accuracy:.4f}')
print(f'test set accuracy: {test_accuracy:.4f}')
