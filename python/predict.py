import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionParams(BaseModel):
    team1: str
    team2: str
    tournament: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

@app.post("/predict")
async def predict_match(params: PredictionParams):
    # Charger les données d'entraînement pour vérifier les valeurs valides
    data_teams = pd.read_csv('./datas/all_teams.csv')
    data_tournaments = pd.read_csv('./datas/all_tournaments.csv')
    data_cities = pd.read_csv('./datas/all_cities.csv')
    data_countries = pd.read_csv('./datas/all_countries.csv')

    # Identifier les colonnes dans les fichiers chargés
    print("Colonnes disponibles dans all_teams.csv:", data_teams.columns)
    print("Colonnes disponibles dans all_tournaments.csv:", data_tournaments.columns)
    print("Colonnes disponibles dans all_cities.csv:", data_cities.columns)
    print("Colonnes disponibles dans all_countries.csv:", data_countries.columns)

    # Vérification des équipes présentes
    available_teams = data_teams.iloc[:, 0].unique()
    available_tournaments = data_tournaments.iloc[:, 0].unique()
    available_cities = data_cities.iloc[:, 0].unique()
    available_countries = data_countries.iloc[:, 0].unique()

    if params.team1 not in available_teams or params.team2 not in available_teams:
        raise HTTPException(status_code=400, detail="L'une des équipes n'existe pas dans les données d'entraînement.")

    if params.tournament and params.tournament not in available_tournaments:
        raise HTTPException(status_code=400, detail="Le tournoi n'existe pas dans les données d'entraînement.")
    if params.city and params.city not in available_cities:
        raise HTTPException(status_code=400, detail="La ville n'existe pas dans les données d'entraînement.")
    if params.country and params.country not in available_countries:
        raise HTTPException(status_code=400, detail="Le pays n'existe pas dans les données d'entraînement.")

    # Chargement des modèles
    result_model = joblib.load("result_model.pkl")
    home_score_model = joblib.load("home_score_model.pkl")
    away_score_model = joblib.load("away_score_model.pkl")
    scaler_cls = joblib.load("scaler_cls.pkl")
    scaler_reg_home = joblib.load("scaler_reg_home.pkl")
    scaler_reg_away = joblib.load("scaler_reg_away.pkl")
    features = joblib.load("features.pkl")

    # Préparation des nouvelles données
    new_match = pd.DataFrame({
        'home_team': [params.team1],
        'away_team': [params.team2],
        'tournament': [params.tournament] if params.tournament else ['Unknown'],
        'city': [params.city] if params.city else ['Unknown'],
        'country': [params.country] if params.country else ['Unknown']
    })

    new_match_encoded = pd.get_dummies(new_match)
    new_match_encoded = new_match_encoded.reindex(columns=features, fill_value=0)
    new_match_normalized_cls = scaler_cls.transform(new_match_encoded)
    new_match_normalized_home = scaler_reg_home.transform(new_match_encoded)
    new_match_normalized_away = scaler_reg_away.transform(new_match_encoded)

    # Prédiction de l'issue du match
    prediction = result_model.predict(new_match_normalized_cls)
    prediction_proba = result_model.predict_proba(new_match_normalized_cls)

    # Vérifier l'ordre des probabilités
    print(f"Probabilités prédictives : {prediction_proba}")

    # Prédiction des scores
    home_score = home_score_model.predict(new_match_normalized_home)[0]
    away_score = away_score_model.predict(new_match_normalized_away)[0]

    # Conversion en types natifs Python et éviter les scores négatifs
    home_score = max(0, int(round(home_score)))
    away_score = max(0, int(round(away_score)))

    # Identifier les indices des probabilités
    proba_home_win = prediction_proba[0][2]
    proba_away_win = prediction_proba[0][0]
    proba_draw = prediction_proba[0][1]

    # Ajustement des probabilités pour éviter des valeurs incohérentes
    total_probability = proba_home_win + proba_away_win + proba_draw
    if total_probability > 0:
        proba_home_win = (proba_home_win / total_probability) * 100
        proba_away_win = (proba_away_win / total_probability) * 100
        proba_draw = (proba_draw / total_probability) * 100

    # Déterminer le résultat du match basé sur les scores prédits
    if home_score > away_score:
        return {
            "winner": params.team1,
            "prediction_score": round(proba_home_win, 2),
            "home_score": home_score,
            "away_score": away_score
        }
    elif away_score > home_score:
        return {
            "winner": params.team2,
            "prediction_score": round(proba_away_win, 2),
            "home_score": home_score,
            "away_score": away_score
        }
    else:
        return {
            "winner": "draw",
            "prediction_score": round(proba_draw, 2),
            "home_score": home_score,
            "away_score": away_score
        }
