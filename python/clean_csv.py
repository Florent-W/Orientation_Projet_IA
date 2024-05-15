import pandas as pd

# Chargement du fichier CSV
df = pd.read_csv('./datas/results.csv')

# Conversion de la colonne 'date' en datetime pour faciliter le filtrage
df['date'] = pd.to_datetime(df['date'])

# Filtrage pour ne garder que les matchs depuis l'année 2000
df = df[df['date'].dt.year >= 2000]

# Filtrage des matchs où l'équipe à domicile est bien dans son pays d'origine
filtered_df = df[df.apply(lambda x: x['country'] in x['home_team'], axis=1)]

# Création d'une nouvelle colonne 'home_win' pour indiquer si l'équipe à domicile a gagné
filtered_df['home_win'] = (filtered_df['home_score'] > filtered_df['away_score']).astype(bool)

# Suppression des colonnes 'home_score' et 'away_score'
filtered_df = filtered_df.drop(columns=['home_score', 'away_score'])

# Sauvegarde du résultat dans un nouveau fichier CSV
filtered_df.to_csv('./datas/data_clean.csv', index=False)

print("Filtrage et transformation terminés. Les données sont sauvegardées dans '/datas/data_clean.csv'.")
