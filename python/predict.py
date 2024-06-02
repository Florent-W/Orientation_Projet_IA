import pandas as pd
import joblib 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict_match(params: dict):
    # On charge les données d'entrainement des matchs des pays depuis 2000 pour récupérer la liste des pays présent
    data = pd.read_csv('./datas/all_teams.csv')
    data_tournaments = pd.read_csv('./datas/all_tournaments.csv')
    data_cities = pd.read_csv('./datas/all_cities.csv')
    data_countries = pd.read_csv('./datas/all_countries.csv')

    # Vérification des équipes présentes
    available_teams = data['away_team'].unique()
    available_tournaments = data_tournaments['tournament'].unique()
    available_cities = data_cities['city'].unique()
    available_countries = data_countries['country'].unique()

    if 'team1' not in params or 'team2' not in params:
        print("Les noms des équipes 'team1' et 'team2' sont requis.")
        return {"error": "Les noms des équipes 'team1' et 'team2' sont requis."}

    # Nom des équipes pour la prédiction 
    home_team = params['team1']
    away_team = params['team2']
    tournament = params.get('tournament', None)
    city = params.get('city', None)
    country = params.get('country', None)

    if home_team not in available_teams or away_team not in available_teams:
        print(f"L'une des équipes '{home_team}' ou '{away_team}' n'existe pas dans les données d'entraînement.")
        return {"error": "L'une des équipes n'existe pas dans les données d'entraînement."}
    
     # Vérification de la validité des autres paramètres
    if tournament and tournament not in available_tournaments:
        print(f"Le tournoi '{tournament}' n'existe pas dans les données d'entraînement.")
        return {"error": "Le tournoi n'existe pas dans les données d'entraînement."}
    if city and city not in available_cities:
        print(f"La ville '{city}' n'existe pas dans les données d'entraînement.")
        return {"error": "La ville n'existe pas dans les données d'entraînement."}
    if country and country not in available_countries:
        print(f"Le pays '{country}' n'existe pas dans les données d'entraînement.")
        return {"error": "Le pays n'existe pas dans les données d'entraînement."}

    # Chargement du modèle
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    features = joblib.load("features.pkl")

    new_match = pd.DataFrame({'home_team': [home_team], 'away_team': [away_team]})

    if tournament:
        new_match['tournament'] = tournament
    if city:
        new_match['city'] = city
    if country:
        new_match['country'] = country

    
    new_match_encoded = pd.get_dummies(new_match)
    new_match_encoded = new_match_encoded.reindex(columns=features.columns, fill_value=0)

    new_match_normalized = scaler.transform(new_match_encoded)

    # Prédiction de l'issue du match
    prediction = model.predict(new_match_normalized)
    prediction_proba = model.predict_proba(new_match_normalized)

    if prediction[0] == 1:
        print(f"{home_team} va probablement gagner.")
        return {"winner": home_team, "prediction_score": prediction_proba[0][1]}
    else:
        print(f"{away_team} va probablement gagner.")
        return {"winner": away_team, "prediction_score": prediction_proba[0][0]}
