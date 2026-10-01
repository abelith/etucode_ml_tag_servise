import json
import logging
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model():
    logger.info("Загрузка базовой модели DeepPavlov...")
    model = SentenceTransformer('DeepPavlov/rubert-base-cased-sentence')
    
    logger.info("Чтение датасета из categories.json...")
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    train_examples = []
    
    for category, phrases in categories.items():
        for phrase in phrases:
            train_examples.append(InputExample(texts=[phrase, category]))
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    
    logger.info(f"Старт обучения с защитой от коллапса...")
    
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=10, 
        warmup_steps=10,
        show_progress_bar=True
    )
    
    output_path = './fine_tuned_rubert'
    model.save(output_path)
    logger.info(f"Готово! Правильно обученная модель сохранена в: {output_path}")

if __name__ == '__main__':
    train_model()