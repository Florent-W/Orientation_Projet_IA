import pandas as pd

# Chargement du fichier CSV
df = pd.read_csv('./datas/data_clean.csv')

# Extraction des équipes à domicile et à l'extérieur
home_teams = df['home_team'].unique()
away_teams = df['away_team'].unique()

# Utilisation d'un set pour éliminer les doublons
all_teams = set(home_teams) | set(away_teams)

# Conversion en liste et tri (optionnel)
all_teams = sorted(list(all_teams))

# Sauvegarde du résultat dans un nouveau fichier CSV
all_teams_df = pd.DataFrame(all_teams, columns=['team'])
all_teams_df.to_csv('./datas/all_teams.csv', index=False)

print("Done.")
