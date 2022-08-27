import pickle
# 第一次執行會需要一點時間下載，之後就會使用 cache 住的
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity
from typing import Any, Optional

from pydantic import BaseModel
from dataclasses import dataclass


class AIService:

    def __init__(self):
        self.model = None
        self.lawyer_emd = None

    def load_model(self):
        """ 會花幾秒 load 一下"""
        self.model = SentenceTransformer('ckiplab/albert-base-chinese')
        with open('./sample_data/lawyer_emd.pickle', 'rb') as f:
            self.lawyer_emd = pickle.load(f)

    def get_similiar_lawyers(self,
                             cosine_sim: np.ndarray,
                             input_lawyer: int = 3) -> list[int]:
        # Get the similarity scores
        sim_scores = list(enumerate(cosine_sim))

        # Sort the layers based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the top-k most similar articles
        sim_scores = sim_scores[1:input_lawyer]

        # Get the lawyer indices
        lawyer_indices = [i[0] for i in sim_scores]

        # Return the top-k most similar article ID
        return lawyer_indices

    def lawyer_query(self, user_input: list[str]) -> list[str]:
        query_emd = self.model.encode(user_input)
        search_emd = np.array(list(self.lawyer_emd.values()))
        cosine_sim = cosine_similarity(
            search_emd,
            query_emd)  # using cosine_sim in scikit learn for quick access
        lawyer_indices = self.get_similiar_lawyers(cosine_sim, 6)
        lawyer = list(self.lawyer_emd.keys())

        found_lawyer_list = [lawyer[index] for index in lawyer_indices]
        return found_lawyer_list

    def predict(self, query_str_list: list[str]) -> list[str]:
        result = self.lawyer_query(query_str_list)
        return result


def main():
    ai_service = AIService()
    ai_service.load_model()
    result = ai_service.predict(["股票"])
    print(result)


if __name__ == '__main__':
    main()
