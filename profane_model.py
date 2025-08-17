import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

df = pd.read_csv('profane_dataset.csv')

X = df['tweet']
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

vectorizer = TfidfVectorizer(
    max_features=5000,   
    ngram_range=(1,2),   
    stop_words="english" 
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=500, class_weight="balanced")
model.fit(X_train_tfidf, y_train)

y_pred = model.predict(X_test_tfidf)

# print("Accuracy:", accuracy_score(y_test, y_pred))
# print("\nClassification Report:\n", classification_report(y_test, y_pred))
# print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))


# import joblib

# joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
# joblib.dump(model, "logreg_model.pkl")
