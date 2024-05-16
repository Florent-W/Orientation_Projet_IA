import pandas as pd
import joblib 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Charger les données (utilisez le bon chemin)
data = pd.read_csv('./datas/data_clean.csv')

# Vérifier les équipes présentes
available_home_teams = data['home_team'].unique()
available_away_teams = data['away_team'].unique()

# Nom des équipes pour la prédiction 
home_team = 'Italy'
away_team = 'Japan'

# Vérifier si les équipes sont présentes dans les données d'entraînement
if home_team not in available_home_teams or away_team not in available_away_teams:
    print(f"L'une des équipes '{home_team}' ou '{away_team}' n'existe pas dans les données d'entraînement.")
else:
    # Chargement du modèle
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    features = joblib.load("features.pkl")

    # Préparation de la nouvelle donnée pour le match France vs Congo
    new_match = pd.DataFrame({'home_team': [home_team], 'away_team': [away_team]})

    # Encodage des caractéristiques catégorielles
    new_match_encoded = pd.get_dummies(new_match)
    new_match_encoded = new_match_encoded.reindex(columns=features.columns, fill_value=0)

    # Normalisation des nouvelles données
    new_match_normalized = scaler.transform(new_match_encoded)

    # Prédiction de l'issue du match
    prediction = model.predict(new_match_normalized)
    prediction_proba = model.predict_proba(new_match_normalized)

    # Interprétation du résultat
    if prediction[0] == 1:
        print(f"{home_team} va probablement gagner.")
    else:
        print(f"{away_team} va probablement gagner.")

    # Affichage des probabilités
    print(f"Probabilités : {prediction_proba}")