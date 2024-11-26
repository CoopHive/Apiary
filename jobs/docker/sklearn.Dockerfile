FROM python:3
RUN pip install --no-cache-dir scikit-learn pandas

RUN echo "\
from sklearn.datasets import load_iris\n\
from sklearn.model_selection import train_test_split\n\
from sklearn.ensemble import RandomForestClassifier\n\
from sklearn.metrics import accuracy_score\n\
import pandas as pd\n\
\n\
# Load the Iris dataset\n\
data = load_iris()\n\
X = pd.DataFrame(data['data'], columns=data['feature_names'])\n\
y = pd.Series(data['target'])\n\
\n\
# Split the data into training and test sets\n\
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)\n\
\n\
# Train a random forest classifier\n\
clf = RandomForestClassifier(n_estimators=100, random_state=42)\n\
clf.fit(X_train, y_train)\n\
\n\
# Predict on the test set\n\
y_pred = clf.predict(X_test)\n\
\n\
# Calculate accuracy\n\
accuracy = accuracy_score(y_test, y_pred)\n\
print(f'Accuracy: {accuracy * 100:.2f}%')\n" > classify.py

CMD ["python", "classify.py"]
