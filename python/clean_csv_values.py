import pandas as pd
import json

# Chargement du fichier CSV
df = pd.read_csv('./datas/data_clean.csv')

def extract(df, column_name, file_name):
    # Extraction des valeurs uniques et tri pour être sur que qu'il n'y a pas de doublons
    unique_values = sorted(df[column_name].unique())
    # Conversion en DataFrame
    unique_values_df = pd.DataFrame(unique_values, columns=[column_name])
    # Sauvegarde dans le fichier CSV
    unique_values_df.to_csv(f'./datas/{file_name}.csv', index=False)
    print(f"Les {column_name} ont étés trouvés et placés dans le fichier {file_name}.csv.")

def convert_csv_to_json(csv_file, json_file, json_key):
    # Lecture du fichier CSV
    df = pd.read_csv(csv_file)
    # Conversion en dictionnaire avec la clé spécifiée
    data = {json_key: df.iloc[:, 0].tolist()}
    # Sauvegarde en fichier JSON
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Le fichier {csv_file} a été converti en {json_file} avec la clé '{json_key}'.")  

# Extraction et sauvegarde des équipes à domicile et à l'extérieur et des paramètres
extract(df, 'home_team', 'all_teams')
extract(df, 'away_team', 'all_teams')
extract(df, 'tournament', 'all_tournaments')
extract(df, 'city', 'all_cities')
extract(df, 'country', 'all_countries')

# Conversion des fichiers CSV en fichiers JSON
convert_csv_to_json('./datas/all_teams.csv', '../front/src/data/all_teams.json', 'teams')
convert_csv_to_json('./datas/all_tournaments.csv', '../front/src/data/all_tournaments.json', 'tournaments')
convert_csv_to_json('./datas/all_cities.csv', '../front/src/data/all_cities.json', 'cities')
convert_csv_to_json('./datas/all_countries.csv', '../front/src/data/all_countries.json', 'countries')