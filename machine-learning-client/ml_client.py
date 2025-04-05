# pip install transformers torch scipy
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch

# Load model and tokenizer
# Using a pre-trained RoBERTa model fine-tuned for sentiment analysis on Twitter data
model_name = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Analyze sentiment of a given text
def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text using a RoBERTa-based sentiment analysis model.

    Args:
        text (str): The input text to analyze.
    Returns:
        dict[str, float]: A dictionary containing sentiment probabilities ('negative', 'neutral', 'positive') 
                          and a 'composite_score' ranging from 1 to 5, where 1 indicates strong negativity 
                          and 5 indicates strong positivity.

                          Example:
                          {
                              'negative': 0.01,
                              'neutral': 0.15,
                              'positive': 0.84,
                              'composite_score': 4.53
                          }
    """
    # Tokenize the input text
    encoded_text = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_text)
    # Get the raw scores from the model output
    scores = output[0][0].detach().numpy()
    # Convert raw scores of each sentiment class (neg, neu, pos) to probabilities
    score = softmax(scores)

    # Map to composite score (1 to 5): Negative - 1, Neutral - 3, Positive - 5
    composite_score = score[0] * 1 + score[1] * 3 + score[2] * 5
    composite_score = round(composite_score, 2)

    scores_dict = {
        'negative': float(score[0]),
        'neutral': float(score[1]),
        'positive': float(score[2]),
        'composite_score': composite_score
    }
    return scores_dict

if __name__ == "__main__":
    example_positive = "Today was such a good day. I woke up feeling refreshed and energized. The sun was shining, and I finally had time to go for a walk in the park. "
    scores_dict = analyze_sentiment(example_positive)
    # print(f"Example1 Scores: {scores_dict}")
    print(f"Composite Score for Example1: {scores_dict['composite_score']:.2f}")

    example_neutral = "Today was a fairly ordinary day. I woke up and had a simple breakfast. I worked for a few hours and had a couple of meetings in the afternoon."
    scores_dict = analyze_sentiment(example_neutral)
    # print(f"Example2 Scores: {scores_dict}")
    print(f"Composite Score for Example2: {scores_dict['composite_score']:.2f}")

    example_negative = "I feel frustrated today. Nothing seems to be going right at work, and I’m overwhelmed by everything on my to-do list."
    scores_dict = analyze_sentiment(example_negative)
    # print(f"Example3 Scores: {scores_dict}")
    print(f"Composite Score for Example3: {scores_dict['composite_score']:.2f}")