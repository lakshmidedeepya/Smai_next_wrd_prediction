import re
import random
from collections import defaultdict, Counter

class NgramCharacterModel:
    def __init__(self, corpus, n=3):
        """
        Initializes the n-gram model and trains it on the given corpus.

        Args:
            corpus (str): The input training text.
            n (int): The size of the n-grams. Default is 3 (trigram).
        """
        self.n = n  # Order of the n-gram model
        self.ngram_counts = defaultdict(Counter)  # Stores n-gram character counts
        self.context_counts = Counter()  # Stores total counts for each (n-1)-gram
        self.vocab = set()  # Unique characters in corpus
        self.word_list = set()  # Unique words in corpus

        self._train(corpus)  # Train the model

    def _preprocess(self, text):
        """
        Cleans and prepares the text corpus.
        - Converts text to lowercase
        - Removes non-alphabetic characters (except spaces and apostrophes)
        """
        text = text.lower()
        text = re.sub(r"[^a-z\s']", " ", text)  # Retain only letters, spaces, and apostrophes
        text = " ".join(text.split())  # Normalize spaces
        return text

    def _train(self, corpus):
        """
        Trains the language model by extracting n-grams from the corpus.
        """
        corpus = self._preprocess(corpus)
        words = corpus.split()  # Tokenize into words
        self.word_list.update(words)  # Store unique words

        for word in words:
            for i in range(len(word) - self.n + 1):
                context = word[i:i + self.n - 1]  # (N-1)-gram prefix
                next_char = word[i + self.n - 1]  # Next character

                self.ngram_counts[context][next_char] += 1
                self.context_counts[context] += 1
                self.vocab.add(next_char)

    def _generate_word(self, prefix):
        """
        Generates a word by iteratively predicting characters.

        Args:
            prefix (str): The starting sequence.

        Returns:
            str: The generated word.
        """
        prefix = prefix.lower()

        while True:
            context = prefix[-(self.n - 1):]  # Use last (N-1) characters as context
            # Backoff strategy: Reduce n-gram size if no match found
            while context not in self.ngram_counts and len(context) > 1:
                context = context[1:]  # Reduce context length
            if context not in self.ngram_counts or not self.ngram_counts[context]:
                break  # Stop if no valid prediction

            # Pick the most frequent next character
            next_char = max(self.ngram_counts[context], key=self.ngram_counts[context].get)

            if next_char == " "or next_char is None:  # Stop at space (word boundary)
                break

            prefix += next_char

        return prefix.strip()

    def predict_top_words(self, prefix, top_k=10):
        """
        Predicts the most probable words starting with the given prefix.

        Args:
            prefix (str): The input prefix.
            top_k (int): Number of top words to return.

        Returns:
            list: The top K words by probability.
        """
        prefix = prefix.lower()
        candidates = {word: self._word_probability(word) for word in self.word_list if word.startswith(prefix)}
        # If no exact matches, find words that contain the prefix somewhere
        if not candidates:
            candidates = {word: self._word_probability(word) for word in self.word_list if prefix in word}


        return sorted(candidates, key=candidates.get, reverse=True)[:top_k]

    def _word_probability(self, word):
        """
        Computes the probability of a word based on n-gram probabilities.

        Args:
            word (str): The input word.

        Returns:
            float: Computed probability (returns 0 if any probability is 0).
        """
        prob = 1.0
        alpha = 0.0001  # Small smoothing factor for unseen cases

        for i in range(len(word) - self.n + 1):
            context = word[i:i + self.n - 1]
            char = word[i + self.n - 1]

            context_count = self.context_counts.get(context, 0)
            char_count = self.ngram_counts[context].get(char, 0)

            # Apply additive smoothing for unseen cases
            prob *= (char_count + alpha) / (context_count + alpha * len(self.vocab)) 

        return prob
