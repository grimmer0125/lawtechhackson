import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity
from typing import List


def get_similiar_lawyers(cosine_sim: np.ndarray,
                         input_lawyer: int = 3) -> List[int]:
    # Get the similarity scores
    sim_scores = list(enumerate(cosine_sim))

    # Sort the layers based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the top-k most similar articles
    sim_scores = sim_scores[1:input_lawyer]

    # Get the laywer indices
    lawyer_indices = [i[0] for i in sim_scores]

    # Return the top-k most similar article ID
    return lawyer_indices


def lawyer_query(user_input: List, model, lawyer_emd) -> List[str]:
    query_emd = model.encode(user_input)
    search_emd = np.array(list(lawyer_emd.values()))
    cosine_sim = cosine_similarity(
        search_emd,
        query_emd)  # using cosine_sim in scikit learn for quick access
    lawer_indces = get_similiar_lawyers(cosine_sim, 3)
    lawyer = np.array(list(lawyer_emd.keys()))

    return lawyer[lawer_indces]


def main():
    model = SentenceTransformer('ckiplab/albert-base-chinese')
    with open('./sample_data/lawyer_emd.pickle', 'rb') as f:
        lawyer_emd = pickle.load(f)

    user_input = "股票"
    result = lawyer_query([user_input], model, lawyer_emd)
    print(result)


if __name__ == '__main__':
    main()
