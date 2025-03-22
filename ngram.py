from collections import defaultdict, Counter
import re
import sys


class NgramCharacterModel:
    def __init__(self, corpus, n=2):
        # TODO: Initialize the class variables
        self.n = n
        self.model = defaultdict(Counter)
        self._train(corpus)
        pass
    
    def _train(self, corpus):
        # TODO: Train the language model on the given corpus input
        """Train the N-gram model on the given corpus."""
        corpus = re.sub(r'[^a-zA-Z ]', '', corpus.lower())  # Clean text
        corpus = corpus.replace(" ", "_")  # Use underscores to denote word boundaries
        
        for i in range(len(corpus) - self.n + 1):
            prefix = tuple(corpus[i:i + self.n - 1])
            next_char = corpus[i + self.n - 1]
            self.model[prefix][next_char] += 1
    
        pass

    def _generate_word(self, prefix):
        # TODO: Given a prefix, generate the most probable word that it completes to
        """Generate the most probable word given a prefix."""
        word = prefix
        for _ in range(10):  # Limit word length to avoid infinite loops
            next_char = self._generate_char(word)
            if next_char == "_" or next_char == "":  # Stop at word boundary
                break
            word += next_char
        return word.replace("_", " ")  # Convert back to spaces
        pass

    def predict_top_words(self, prefix, top_k=10):
        # TODO: Given a prefix, return the top_k most probable words from the corpus it completes to 
        """Return the top_k most probable words given a prefix."""
        
        words = set()
        for _ in range(top_k * 2):  # Generate multiple attempts to find unique words
            word = self._generate_word(prefix)
            if word and word not in words:
                words.add(word)
            if len(words) >= top_k:
                break
        return list(words)
        pass
    
    def _word_probability(self, word):
        # TODO: Calculates the probability of the word, based on the trigram probabilities
        """Calculates the probability of the word based on trigram probabilities."""
        sequence = word.replace(" ", "_")  # Convert spaces to underscores
        return self._char_probability(sequence)
        pass
    def _char_probability(self, sequence: str) -> float:
        """Calculates the probability of a sequence based on the n-gram model."""
        if len(sequence) < self.n:
            return 0.0  # Not enough context for n-gram model
        
        prob = 1.0
        for i in range(len(sequence) - self.n + 1):
            prefix = tuple(sequence[i:i + self.n - 1])
            next_char = sequence[i + self.n - 1]
            
            if prefix in self.model and next_char in self.model[prefix]:
                total_count = sum(self.model[prefix].values())
                prob *= self.model[prefix][next_char] / total_count
            else:
                return 0.0
        return prob