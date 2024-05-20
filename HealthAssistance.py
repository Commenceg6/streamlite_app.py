#!python3
# File: chatbot.py
import warnings

# Suppress InconsistentHashingWarning (use with caution)
warnings.filterwarnings("ignore", category=UserWarning, message="InconsistentHashingWarning")

import streamlit as st

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')

st.sidebar.markdown(
    """
    <h1 style='text-align: center; color: #0080FF;'>HEALTH ASSISTANT ❤</h1>
    """,
    unsafe_allow_html=True
)
# Add a logo image
#logo = st.sidebar.image("logo.png", use_column_width=True)

# Add CSS to position the logo in the top right corner
st.markdown(
    """
    <style>
    .css-1l02zno {
        position: absolute;
        top: 10px;
        right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def preprocess_symptoms(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stopwords and punctuation
    tokens = [word for word in tokens if word not in stopwords.words('english') and word not in string.punctuation]
    # Join the tokens back into a string
    return ', '.join(tokens)

def filter_symptoms(user_input, all_symptoms):
    user_symptoms = preprocess_symptoms(user_input)
    matched_symptoms = set(user_symptoms.split(',')).intersection(all_symptoms)
    return matched_symptoms

def predict_disease_and_treatment(data_path):

    def predict(user_symptoms):
        # Load data
        data = pd.read_csv(data_path)
        
        # Extract all symptoms from the dataset
        all_symptoms = set(data['Symptoms'].str.lower().str.split(',').sum())

        # Filter user input for valid symptoms
        matched_symptoms = filter_symptoms(user_symptoms, all_symptoms)

        if not matched_symptoms:
            return "Unknown", "Please provide valid symptom descriptions."

        # Train-Test Split with fixed random state
        X_train, X_test, y_train, y_test = train_test_split(data["Symptoms"], data["Name"], test_size=0.2, random_state=42)

        # Feature Engineering (TF-IDF)
        vectorizer = TfidfVectorizer()
        X_train_features = vectorizer.fit_transform(X_train)
        X_test_features = vectorizer.transform(X_test)

        # Model Training
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train_features, y_train)

        # Prediction
        symptoms_features = vectorizer.transform([user_symptoms])
        predicted_disease = model.predict(symptoms_features)[0]

        # Treatment Lookup
        treatment_dict = {disease: treatment for disease, treatment in zip(data["Name"], data["Treatment"])}
        predicted_treatment = treatment_dict.get(predicted_disease, "No treatment available")

        return predicted_disease, predicted_treatment

    return predict


def main():
    st.title(" HEALTH ASSISTANT ❤")

    # Check if logged_in query parameter is present
    # query_params = st.experimental_get_query_params()
    # logged_in = query_params.get("logged_in", [False])[0]

    if st.session_state.get("logged_in", False):
        # Load model and tokenizer
        data_path = "pages/updated_data.csv"  # Replace with the path to your CSV file
        predict_function = predict_disease_and_treatment(data_path)

        
        st.header("GOOD DAY DEAR USER 😊")
        st.header("Ask me something concerning your health:")
        user_input = st.text_input("", placeholder="ENTER YOUR SYMPTOMS...")

        if st.button("Diagnose"):
            with st.spinner("Generating response..."):
                
                predicted_disease, predicted_treatment = predict_function(user_input)
    

            st.info("Medical Chatbot Response:")
            st.success(predicted_disease)
            st.success(predicted_treatment)

        st.markdown("---")
        st.info("## Additional Guide:\n1. Ensure your prompts are concise and to the point.\n2. Opt for mentioning each symptom individually and separate them with commas for clarity and ease of understanding.\n3. Example 1: excessive thirst, frequent urination, unexplained weight loss, fatigue, and slow healing of wounds\n4. Example 2 (Conversational style): It's been days since I've been feeling excessive thirst, frequent urination, unexplained weight loss, fatigue, and slow healing of wounds. So what could be the reason?\n\n*You still need to visit the doctor")

        st.sidebar.header("About")
        st.sidebar.write("Health Assistent was crafted using Python alongside Pandas and Scikit-learn. These tools empowered data manipulation, machine learning model training, and text processing tasks efficiently.")
    else:
        st.error("Please log in to get assistence.")  # Display a message or redirect to the login page

if __name__ == "__main__":
    main()
