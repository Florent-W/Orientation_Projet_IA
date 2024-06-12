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

# Charger les modèles et les scalers
result_model = joblib.load('models/result_model.pkl')
home_score_model = joblib.load('models/home_score_model.pkl')
away_score_model = joblib.load('models/away_score_model.pkl')
scaler_cls = joblib.load('scalers/scaler_cls.pkl')
scaler_reg_home = joblib.load('scalers/scaler_reg_home.pkl')
scaler_reg_away = joblib.load('scalers/scaler_reg_away.pkl')
features = joblib.load('models/features.pkl')

def prepare_encoded_data(data, features):
    encoded_data = pd.get_dummies(data)
    missing_cols = list(set(features) - set(encoded_data.columns))
    missing_data = pd.DataFrame(0, index=encoded_data.index, columns=missing_cols)
    encoded_data = pd.concat([encoded_data, missing_data], axis=1)
    encoded_data = encoded_data[features]
    return encoded_data

def predict_match_data(home_team, away_team, tournament=None, city=None, country=None):
    new_match = pd.DataFrame({
        'home_team': [home_team],
        'away_team': [away_team],
        'tournament': [tournament] if tournament else ['Unknown'],
        'city': [city] if city else ['Unknown'],
        'country': [country] if country else ['Unknown']
    })

    new_match_encoded = prepare_encoded_data(new_match, features)
    new_match_normalized_cls = scaler_cls.transform(new_match_encoded)
    new_match_normalized_home = scaler_reg_home.transform(new_match_encoded)
    new_match_normalized_away = scaler_reg_away.transform(new_match_encoded)

    # Prédiction de l'issue du match
    prediction = result_model.predict(new_match_normalized_cls)
    prediction_proba = result_model.predict_proba(new_match_normalized_cls)

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
            "home_team": home_team,
            "away_team": away_team,
            "winner": home_team,
            "prediction_score": round(proba_home_win, 2),
            "home_score": home_score,
            "away_score": away_score
        }
    elif away_score > home_score:
        return {
            "home_team": home_team,
            "away_team": away_team,
            "winner": away_team,
            "prediction_score": round(proba_away_win, 2),
            "home_score": home_score,
            "away_score": away_score
        }
    else:
        return {
            "home_team": home_team,
            "away_team": away_team,
            "winner": "draw",
            "prediction_score": round(proba_draw, 2),
            "home_score": home_score,
            "away_score": away_score
        }

@app.post("/predict")
async def predict_match(params: PredictionParams):
    data_teams = pd.read_csv('./datas/all_teams.csv')
    data_tournaments = pd.read_csv('./datas/all_tournaments.csv')
    data_cities = pd.read_csv('./datas/all_cities.csv')
    data_countries = pd.read_csv('./datas/all_countries.csv')

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

    return predict_match_data(params.team1, params.team2, params.tournament, params.city, params.country)

def run_predictions():
    data_path = 'datas/data_import.csv'
    matches_data = pd.read_csv(data_path, sep=';')
    predictions = matches_data.apply(lambda row: predict_match_data(
        row['home_team'], 
        row['away_team'], 
        row['tournament'] if 'tournament' in row else None, 
        row['city'] if 'city' in row else None, 
        row['country'] if 'country' in row else None
    ), axis=1)
    predictions_df = pd.DataFrame(predictions.tolist())
    predictions_df['group'] = matches_data['group']
    predictions_df['home_team'] = matches_data['home_team']
    predictions_df['away_team'] = matches_data['away_team']
    predictions_df['tournament'] = matches_data['tournament']
    predictions_df['city'] = matches_data['city']
    predictions_df['country'] = matches_data['country']
    predictions_df.to_csv('datas/euro_predicted_results.csv', index=False)

@app.on_event("startup")
async def startup_event():
    run_predictions()

@app.get("/predictions")
async def get_predictions():
    euro_results_path = 'datas/euro_predicted_results.csv'
    predictions_df = pd.read_csv(euro_results_path)
    return predictions_df.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
