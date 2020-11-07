import pandas as pd
import nltk
from nltk.corpus import stopwords
import argparse

# endlish_words = set(nltk.corpus.words.words())
stop_words = set(stopwords.words('english'))

# clean data from stop words and non-english words
def main():

    # upload all data
    all_terms = pd.read_csv('../all_terms.csv')
    all_bigrams = pd.read_csv('../all_bigrams.csv')
    all_trigrams = pd.read_csv('../all_trigrams.csv')
    frequent_terms = pd.read_csv('../frequent_terms.csv')
    frequent_bigrams = pd.read_csv('../frequent_bigrams.csv')
    frequent_trigrams = pd.read_csv('../frequent_trigrams.csv')

    all_terms = all_terms[all_terms['term'].apply(is_correct)]
    all_terms.to_csv('../all_terms.csv', index=False)

    all_bigrams = all_bigrams[all_bigrams['gram'].apply(is_correct)]
    all_bigrams.to_csv('../all_bigrams.csv', index=False)

    all_trigrams = all_trigrams[all_trigrams['gram'].apply(is_correct)]
    all_trigrams.to_csv('../all_trigrams.csv', index=False)

    frequent_terms = frequent_terms[frequent_terms['term'].apply(is_correct)]
    frequent_terms.to_csv('../frequent_terms.csv', index=False)

    frequent_bigrams = frequent_bigrams[frequent_bigrams['bigram'].apply(is_correct)]
    frequent_bigrams.to_csv('../frequent_bigrams.csv', index=False)

    frequent_trigrams = frequent_trigrams[frequent_trigrams['trigram'].apply(is_correct)]
    frequent_trigrams.to_csv('../frequent_trigrams.csv', index=False)



def is_correct(x):
    sent = ''.join(w for w in x.split() if w.isalpha() or
                   not w in stop_words or len(w)<=2)
    if sent == '':
        return False
    else:
        return True





if __name__ == "__main__":
    main()
