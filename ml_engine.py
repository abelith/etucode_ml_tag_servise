import logging
import json
from typing import Dict, Any
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

logger = logging.getLogger(__name__)

class TagPredictor:
    def __init__(self) -> None:
        logger.info("Загрузка локальной дообученной модели DeepPavlov...")
        self.model = SentenceTransformer('./fine_tuned_rubert')
        
        logger.info("Загрузка категорий из categories.json...")
        with open('categories.json', 'r', encoding='utf-8') as f:
            self.categories = json.load(f)

        self.intent_embeddings: Dict[str, Any] = {
            tag: self.model.encode(tag) for tag in self.categories.keys()
        }
        logger.info("ML-движок инициализирован: прямое векторное сравнение с защитой.")

    def process_message(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        text_embedding = self.model.encode(text_lower)
        
        scores = {
            tag: 1 - cosine(text_embedding, tag_emb) 
            for tag, tag_emb in self.intent_embeddings.items()
        }
        
        # Сортируем результаты по убыванию уверенности
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_tag, best_score = sorted_scores[0]
        second_best_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
        
        MIN_SCORE = 0.35 
        MIN_DELTA = 0.05 
        
        if best_score < MIN_SCORE:
            logger.info(f"Слишком низкая уверенность ({best_score:.2f} < {MIN_SCORE}). Тег сброшен на 'прочее'.")
            best_tag = "прочее"
        elif (best_score - second_best_score) < MIN_DELTA:
            logger.info(f"Спорное сообщение (разница всего {best_score - second_best_score:.2f}). Тег сброшен на 'прочее'.")
            best_tag = "прочее"
            
        return {
            "tags": [best_tag],
            "vector": text_embedding.tolist()
        }

predictor = TagPredictor()