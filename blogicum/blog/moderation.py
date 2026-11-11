from functools import cache

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from core.constants import TOXICITY_THRESHOLD


MODEL_NAME = 'cointegrated/rubert-tiny-toxicity'


@cache
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def get_toxicity_score(text: str) -> float:
    """Вернуть оценку токсичности от 0 до 1."""
    tokenizer, model = load_model()
    inputs = tokenizer(
        text,
        return_tensors='pt',
        truncation=True,
    )

    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = torch.sigmoid(outputs.logits)[0]
        score = 1 - probabilities[0] * (1 - probabilities[-1])

    return score.item()


def is_toxic(text: str) -> bool:
    """Определить, достигла ли оценка заданного порога."""
    return get_toxicity_score(text) >= TOXICITY_THRESHOLD
