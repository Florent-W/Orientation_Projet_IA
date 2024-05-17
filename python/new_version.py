import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.neighbors import KernelDensity
import numpy as np

# On charge les données d'entrainement des matchs des pays depuis 2000 pour avoir des données cohérentes
data = pd.read_csv('data_clean.csv') 

# On charge un fichier CSV contenant les matchs de l'Euro 2024
euro_matches = pd.read_csv('data_import.csv', sep=';')

# Vérifier les équipes présentes dans les données d'entraînement
available_home_teams = data['home_team'].unique()
available_away_teams = data['away_team'].unique()

# Sélection des caractéristiques pertinentes pour l'entraînement
features = data[['home_team', 'away_team']]
target_result = data['home_win']
target_home_score = data['home_score']
target_away_score = data['away_score']

# Modifier la colonne cible pour inclure les matchs nuls
def get_match_result(row):
    if row['home_score'] > row['away_score']:
        return 2  # Victoire de l'équipe à domicile
    elif row['home_score'] < row['away_score']:
        return 0  # Victoire de l'équipe à l'extérieur
    else:
        return 1  # Match nul

data['match_result'] = data.apply(get_match_result, axis=1)
target_result = data['match_result']

# Encodage des caractéristiques catégorielles
features = pd.get_dummies(features)

# Afficher les colonnes de features
print("Colonnes de features:")
print(features.columns)

# Séparation des ensembles de formation et de test pour la classification
X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(features, target_result, test_size=0.22)

# Séparation des ensembles de formation et de test pour la régression
X_train_reg_home, X_test_reg_home, y_train_home, y_test_home = train_test_split(features, target_home_score, test_size=0.22)
X_train_reg_away, X_test_reg_away, y_train_away, y_test_away = train_test_split(features, target_away_score, test_size=0.22)

scaler_cls = StandardScaler()
scaler_reg_home = StandardScaler()
scaler_reg_away = StandardScaler()
X_train_cls = scaler_cls.fit_transform(X_train_cls)
X_test_cls = scaler_cls.transform(X_test_cls)
X_train_reg_home = scaler_reg_home.fit_transform(X_train_reg_home)
X_test_reg_home = scaler_reg_home.transform(X_test_reg_home)
X_train_reg_away = scaler_reg_away.fit_transform(X_train_reg_away)
X_test_reg_away = scaler_reg_away.transform(X_test_reg_away)

# Création du modèle de classification
model_cls = LogisticRegression(max_iter=1000, multi_class='multinomial')

# Entraînement
model_cls.fit(X_train_cls, y_train_cls)

# Prédictions
y_pred_cls = model_cls.predict(X_test_cls)

test_accuracy = accuracy_score(y_test_cls, y_pred_cls)
print(f"\nTest Accuracy (Classification): {test_accuracy*100:.2f}%")

# Création des modèles de régression pour prédire les scores
model_home_score = LinearRegression()
model_away_score = LinearRegression()

# Entraînement des modèles de régression
model_home_score.fit(X_train_reg_home, y_train_home)
model_away_score.fit(X_train_reg_away, y_train_away)

# Fonction pour calculer la probabilité des scores
def calculate_score_probability(predicted_score, y_train, bandwidth=1.0):
    kde = KernelDensity(bandwidth=bandwidth).fit(y_train.reshape(-1, 1))
    log_density = kde.score_samples(np.array([[predicted_score]]))
    return np.exp(log_density)[0]

# Préparation d'une liste pour stocker les prédictions
predictions = []

# Boucle sur tous les matchs de l'Euro 2024
for index, match in euro_matches.iterrows():
    home_team = match['home_team']
    away_team = match['away_team']
    
    # Vérifier si les équipes sont présentes dans les données d'entraînement
    if home_team not in available_home_teams or away_team not in available_away_teams:
        result = f"L'une des équipes '{home_team}' ou '{away_team}' n'existe pas dans les données d'entraînement."
        predicted_home_score = None
        predicted_away_score = None
        probability_home_score = None
        probability_away_score = None
        probability_home_win = None
        probability_away_win = None
        probability_draw = None
    else:
        # Préparation de la nouvelle donnée pour le match
        new_match = pd.DataFrame({'home_team': [home_team], 'away_team': [away_team]})

        new_match_encoded = pd.get_dummies(new_match)
        new_match_encoded = new_match_encoded.reindex(columns=features.columns, fill_value=0)

        # Normalisation des nouvelles données
        new_match_normalized_cls = scaler_cls.transform(new_match_encoded)
        new_match_normalized_home = scaler_reg_home.transform(new_match_encoded)
        new_match_normalized_away = scaler_reg_away.transform(new_match_encoded)

        # Prédiction de l'issue du match
        prediction = model_cls.predict(new_match_normalized_cls)
        prediction_proba = model_cls.predict_proba(new_match_normalized_cls)

        # Prédiction des scores du match
        predicted_home_score = round(model_home_score.predict(new_match_normalized_home)[0])
        predicted_away_score = round(model_away_score.predict(new_match_normalized_away)[0])

        # Calcul des probabilités des scores
        probability_home_score = calculate_score_probability(predicted_home_score, y_train_home.values)
        probability_away_score = calculate_score_probability(predicted_away_score, y_train_away.values)

        result = ""
        if prediction[0] == 2:
            result = f"{home_team} va probablement gagner."
        elif prediction[0] == 0:
            result = f"{away_team} va probablement gagner."
        else:
            result = "Le match va probablement se terminer par un match nul."

        probability_home_win = prediction_proba[0][2] * 100
        probability_away_win = prediction_proba[0][0] * 100
        probability_draw = prediction_proba[0][1] * 100

    predictions.append({
        'home_team': home_team,
        'away_team': away_team,
        'result': result,
        'predicted_home_score': predicted_home_score,
        'predicted_away_score': predicted_away_score,
        'probability_home_win': probability_home_win,
        'probability_away_win': probability_away_win,
        'probability_draw': probability_draw,
        'probability_home_score': probability_home_score * 100 if probability_home_score is not None else None,
        'probability_away_score': probability_away_score * 100 if probability_away_score is not None else None,
        'test_accuracy': test_accuracy * 100
    })

# Convertir les prédictions en DataFrame
df_predictions = pd.DataFrame(predictions)

# Affichage des prédictions
print(df_predictions.head())

# Enregistrement dans un fichier CSV avec point-virgule comme séparateur
predictions_file_path = 'euro_2024_predictions.csv'
df_predictions.to_csv(predictions_file_path, index=False, sep=';')

predictions_file_path
