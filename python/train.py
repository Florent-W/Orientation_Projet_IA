import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib

# Charger les données d'entraînement
data_path = 'datas/data_clean.csv'
data = pd.read_csv(data_path)

# Préparer les caractéristiques et les cibles
data['match_result'] = data.apply(lambda row: 1 if row['home_score'] > row['away_score'] else (-1 if row['home_score'] < row['away_score'] else 0), axis=1)
features = data[['home_team', 'away_team', 'tournament', 'city', 'country']]
target_result = data['match_result']
target_home_score = data['home_score']
target_away_score = data['away_score']

# Encodage des caractéristiques catégorielles
features_encoded = pd.get_dummies(features)

# Séparation des ensembles de formation et de test pour la classification
X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(features_encoded, target_result, test_size=0.2, random_state=42)

# Séparation des ensembles de formation et de test pour la régression
X_train_reg_home, X_test_reg_home, y_train_home, y_test_home = train_test_split(features_encoded, target_home_score, test_size=0.2, random_state=42)
X_train_reg_away, X_test_reg_away, y_train_away, y_test_away = train_test_split(features_encoded, target_away_score, test_size=0.2, random_state=42)

# Normalisation des données
scaler_cls = StandardScaler()
scaler_reg_home = StandardScaler()
scaler_reg_away = StandardScaler()

X_train_cls = scaler_cls.fit_transform(X_train_cls)
X_test_cls = scaler_cls.transform(X_test_cls)
X_train_reg_home = scaler_reg_home.fit_transform(X_train_reg_home)
X_test_reg_home = scaler_reg_home.transform(X_test_reg_home)
X_train_reg_away = scaler_reg_away.fit_transform(X_train_reg_away)
X_test_reg_away = scaler_reg_away.transform(X_test_reg_away)

# Entraînement du modèle de régression logistique pour le résultat du match
model_cls = LogisticRegression(max_iter=1000)
model_cls.fit(X_train_cls, y_train_cls)

# Prédictions et évaluation du modèle de classification
y_pred_cls = model_cls.predict(X_test_cls)
test_accuracy = accuracy_score(y_test_cls, y_pred_cls)
print(f"\nTest Accuracy (Classification): {test_accuracy*100:.2f}%")

# Entraînement des modèles de régression pour les scores
model_home_score = Ridge()
model_away_score = Ridge()

model_home_score.fit(X_train_reg_home, y_train_home)
model_away_score.fit(X_train_reg_away, y_train_away)

# Prédictions et évaluation des modèles de régression
home_score_train_pred = model_home_score.predict(X_train_reg_home)
away_score_train_pred = model_away_score.predict(X_train_reg_away)

home_score_test_pred = model_home_score.predict(X_test_reg_home)
away_score_test_pred = model_away_score.predict(X_test_reg_away)

home_score_train_error = mean_squared_error(y_train_home, home_score_train_pred)
away_score_train_error = mean_squared_error(y_train_away, away_score_train_pred)

home_score_test_error = mean_squared_error(y_test_home, home_score_test_pred)
away_score_test_error = mean_squared_error(y_test_away, away_score_test_pred)

print(f'Home score model train error: {home_score_train_error}')
print(f'Away score model train error: {away_score_train_error}')
print(f'Home score model test error: {home_score_test_error}')
print(f'Away score model test error: {away_score_test_error}')

# Sauvegarde des modèles, du scaler et des caractéristiques
joblib.dump(model_cls, 'result_model.pkl')
joblib.dump(model_home_score, 'home_score_model.pkl')
joblib.dump(model_away_score, 'away_score_model.pkl')
joblib.dump(scaler_cls, 'scaler_cls.pkl')
joblib.dump(scaler_reg_home, 'scaler_reg_home.pkl')
joblib.dump(scaler_reg_away, 'scaler_reg_away.pkl')
joblib.dump(features_encoded.columns, 'features.pkl')
