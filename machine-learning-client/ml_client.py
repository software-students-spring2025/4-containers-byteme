"""
Sentiment analysis Flask API using RoBERTa and MongoDB.
Module to analyze sentiment using a pre-trained
RoBERTa model for sentiment analysis on Twitter data.
This module loads the model and tokenizer,
then performs sentiment analysis on input text.
"""

# pip install transformers torch scipy
import logging

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch

# import flask
from flask import Flask, request, jsonify
from bson.objectid import ObjectId

# import database connection
from db import db

app = Flask(__name__)
entries_col = db["entries"]

# Set up logging in Docker container's output
logging.basicConfig(level=logging.DEBUG)

# Load model and tokenizer
# Using a pre-trained RoBERTa model fine-tuned for sentiment analysis on Twitter data
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)


def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text using a RoBERTa-based sentiment analysis model.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict[str, float]: A dictionary containing sentiment
        probabilities ('negative', 'neutral', 'positive')
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
    encoded_text = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**encoded_text)
    # Get the raw scores from the model output
    scores = output[0][0].detach().numpy()
    # Convert raw scores of each sentiment class (neg, neu, pos) to probabilities
    score = softmax(scores)

    # Map to composite score (1 to 5): Negative - 1, Neutral - 3, Positive - 5
    composite_score = round(score[0] * 1 + score[1] * 3 + score[2] * 5, 2)

    sentiment_scores = {
        "negative": float(score[0]),
        "neutral": float(score[1]),
        "positive": float(score[2]),
        "composite_score": composite_score,
    }
    return sentiment_scores


@app.route("/analyze", methods=["POST"])
def analyze_and_store():
    """Handle POST requests to analyze sentiment and update the database."""

    data = request.get_json()
    entry_id = data.get("entry_id")
    text = data.get("text")

    if not entry_id or not text:
        return jsonify({"error": "entry_id and text are required"}), 400

    sentiment_scores = analyze_sentiment(text)
    # Convert all sentiment scores to native Python types (float)
    sentiment_scores = {
        "negative": float(sentiment_scores.get("negative", 0)),
        "neutral": float(sentiment_scores.get("neutral", 0)),
        "positive": float(sentiment_scores.get("positive", 0)),
        "composite_score": float(sentiment_scores.get("composite_score", 0)),
    }
    app.logger.debug("* analyze_and_store(): Sentiment scores: %s", sentiment_scores)
    print("* analyze_and_store(): Sentiment scores: %s", sentiment_scores)
    entries_col.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": {"sentiment": sentiment_scores}},
        upsert=True,
    )
    app.logger.debug("* analyze_and_store(): Updated entry with ID %s", entry_id)
    print("* analyze_and_store(): Updated entry with ID %s", entry_id)
    return jsonify({"status": "updated", "entry_id": entry_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
    print("ml-client running on port 5001")
    app.logger.debug("*** ml-client is running")
