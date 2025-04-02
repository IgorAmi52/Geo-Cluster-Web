import re
import concurrent.futures
import numpy as np
from scipy import sparse
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))


class TfIdfService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def preprocess_text(self, text):
        """ Lowercase, remove punctuation, and filter out stopwords """
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
        words = text.split()
        words = [word for word in words if word not in stop_words]
        return " ".join(words)

    def generate_ds_description(self, ds_entry):
        """ Convert a dataset entry into a TF-IDF compatible description """
        fields = [str(entry) for entry in ds_entry.values()
                  if entry]  # Ensure all values are strings
        description = " ".join(fields)
        return self.preprocess_text(description)

    def compute_vectors(self, ds_data):
        """ Compute TF-IDF vectors for all datasets in parallel """
        dataset_ids = list(ds_data.keys())
        with concurrent.futures.ThreadPoolExecutor() as executor:
            dataset_descriptions = list(executor.map(
                self.generate_ds_description, ds_data.values()))

        # Convert preprocessed text into TF-IDF vectors
        vectors = self.vectorizer.fit_transform(dataset_descriptions)

        # Map dataset IDs to vectors
        return {ds_id: vectors[i] for i, ds_id in enumerate(dataset_ids)}

    def reduce_dimensions(self, vectors):
        # Ensure vectors are in sparse matrix format
        if not all(sparse.issparse(vec) for vec in vectors):
            vectors = [sparse.csr_matrix(vec) for vec in vectors]
        # Convert sparse matrix to dense for PCA
        # Use toarray() to convert to dense numpy array
        dense_vectors = np.array([vec.toarray()[0] for vec in vectors])
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(dense_vectors)
        return reduced_data
