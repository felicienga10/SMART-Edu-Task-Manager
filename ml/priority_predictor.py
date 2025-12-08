import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

# Simple keyword-based priority prediction
def predict_priority_simple(description):
    description_lower = description.lower()
    
    urgent_keywords = ['urgent', 'deadline', 'due soon', 'important', 'critical', 'exam', 'test', 'final']
    high_keywords = ['high marks', 'major assignment', 'project', 'presentation']
    medium_keywords = ['homework', 'assignment', 'reading']
    low_keywords = ['optional', 'extra', 'practice', 'review']
    
    if any(keyword in description_lower for keyword in urgent_keywords):
        return 'urgent_important'
    elif any(keyword in description_lower for keyword in high_keywords):
        return 'high_priority'
    elif any(keyword in description_lower for keyword in medium_keywords):
        return 'medium_priority'
    elif any(keyword in description_lower for keyword in low_keywords):
        return 'optional'
    else:
        return 'medium_priority'

# ML-based prediction (placeholder for trained model)
def predict_priority(description):
    # For now, use simple keyword matching
    # In a real implementation, load a trained model
    return predict_priority_simple(description)

# Function to train model (to be called separately)
def train_model():
    # Sample training data
    descriptions = [
        "Complete the math exam by tomorrow",
        "Read chapter 5 for homework",
        "Prepare presentation for science project",
        "Optional practice problems",
        "Urgent: Submit assignment due today",
        "Group project meeting next week",
        "Review notes for final exam",
        "Extra credit assignment"
    ]
    
    priorities = [
        'urgent_important',
        'medium_priority',
        'high_priority',
        'optional',
        'urgent_important',
        'group_task',
        'important_not_urgent',
        'optional'
    ]
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(descriptions)
    
    model = MultinomialNB()
    model.fit(X, priorities)
    
    # Save model
    with open('ml/priority_model.pkl', 'wb') as f:
        pickle.dump((vectorizer, model), f)

# Load and use trained model
def predict_priority_ml(description):
    model_path = 'ml/priority_model.pkl'
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            vectorizer, model = pickle.load(f)
        
        X = vectorizer.transform([description])
        return model.predict(X)[0]
    else:
        return predict_priority_simple(description)