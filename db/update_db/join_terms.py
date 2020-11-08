import pandas as pd

all_terms = pd.read_csv('../all_terms.csv', index_col=[0])
all_bigrams = pd.read_csv('../all_bigrams.csv', index_col=[0])
all_trigrams = pd.read_csv('../all_trigrams.csv', index_col=[0])

df = pd.concat([all_terms,all_bigrams,all_trigrams], axis=0, ignore_index=True)
df.reset_index(inplace=True, drop=True)
df.drop_duplicates(inplace=True)

df.to_csv('../daily_terms.csv')