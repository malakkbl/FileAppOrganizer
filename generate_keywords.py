import nltk
nltk.download('wordnet')

from nltk.corpus import wordnet

def generate_related_keywords(theme, num_keywords=1000):
    related_keywords = set()
    target_synsets = wordnet.synsets(theme.lower())

    for synset in target_synsets:
        # Ajouter les lemmes du synset cible
        related_keywords.update(lemma.name() for lemma in synset.lemmas())

        # Ajouter les lemmes des hypernyms (termes plus généraux)
        for hypernym in synset.hypernyms():
            related_keywords.update(lemma.name() for lemma in hypernym.lemmas())

        # Ajouter les lemmes des hyponyms (termes plus spécifiques)
        for hyponym in synset.hyponyms():
            related_keywords.update(lemma.name() for lemma in hyponym.lemmas())

    # Tronquer la liste à la taille souhaitée
    related_keywords = list(related_keywords)[:num_keywords]

    return related_keywords

# Exemple d'utilisation
theme_keywords = generate_related_keywords("algebra", num_keywords=10000)
print(theme_keywords)