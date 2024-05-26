import pandas as pd
import joblib 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


# Données d'entrainement
data = pd.read_csv('./datas/data_clean.csv')

# Vérifier les équipes présentes
available_home_teams = data['home_team'].unique()
available_away_teams = data['away_team'].unique()

features = data[['home_team', 'away_team']]
target = data['home_win']

# Encodage des données en variables numériques
features = pd.get_dummies(features)

# Séparation des ensembles de formation et de test
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.22)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LogisticRegression(max_iter=1000)

# Entraînement du modèle
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# Évaluation du modèle
accuracy = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {accuracy*100:.2f}%")

joblib.dump(model, "model.pkl") 
joblib.dump(scaler, "scaler.pkl")
joblib.dump(features, "features.pkl")

