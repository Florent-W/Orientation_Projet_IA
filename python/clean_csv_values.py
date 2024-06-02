import pandas as pd
import os
import json

# Création des répertoires
os.makedirs('../front/src/data/', exist_ok=True)

# Chargement du fichier CSV
df = pd.read_csv('./datas/data_clean.csv')

def extract_and_save_to_json(df, column_name, file_name, json_key):
    # Extraction des valeurs uniques et tri pour être sûr qu'il n'y a pas de doublons
    unique_values = sorted(df[column_name].unique())
    # Création du dictionnaire avec le préfixe
    data = {json_key: unique_values}
    # Sauvegarde en fichier JSON
    with open(f'../front/src/data/{file_name}.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Les {column_name} ont été trouvés et placés dans le fichier {file_name}.json sous la clé '{json_key}'.")

# Extraction et sauvegarde des équipes à domicile et à l'extérieur et des paramètres
extract_and_save_to_json(df, 'home_team', 'all_teams', 'teams')
extract_and_save_to_json(df, 'away_team', 'all_teams', 'teams')
extract_and_save_to_json(df, 'tournament', 'all_tournaments', 'tournaments')
extract_and_save_to_json(df, 'city', 'all_cities', 'cities')
extract_and_save_to_json(df, 'country', 'all_countries', 'countries')
