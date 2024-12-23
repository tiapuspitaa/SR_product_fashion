# -- coding: utf-8 --
"""sr_fashionProduct.ipynb
# Nama Kelompok :
## 1. Tia Puspita Sari (22.12.2481)
## 2. Renita Tri Hastuti (22.12.2476)
## 3. Fadhila Asla Shana (22.12.2538)
"""

# Step 1: Import Libraries
import os
import subprocess

# Install required packages if not already installed
def install_requirements():
    try:
        import pandas
        import numpy
        import nltk
        import streamlit
        from sklearn.preprocessing import LabelEncoder
    except ImportError:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])

install_requirements()

# Proceed with imports
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from sklearn.preprocessing import LabelEncoder
import streamlit as st

# Download NLTK resources
nltk.download('stopwords')

# Step 2: Load Dataset
def load_dataset():
    dataset_path = 'product_fashion.csv'  # Ensure the dataset is in the same directory as this script
    return pd.read_csv(dataset_path)

df = load_dataset()

# Step 3: Preprocessing Data
# Handle missing values
df['PrimaryColor'] = df['PrimaryColor'].fillna('Unknown')

# Map Gender values to Men, Women, or Unisex (only if mapping is necessary)
valid_genders = ['Men', 'Women', 'Unisex']
df['Gender'] = df['Gender'].apply(lambda x: x if x in valid_genders else 'Unisex')  # Default to 'Unisex' if invalid


# Normalize text data in 'Description'
stop_words = set(stopwords.words('english'))
def preprocess_text(text):
    text = str(text).lower()  # Convert to lowercase
    words = text.split()  # Tokenize
    words = [word for word in words if word not in stop_words]  # Remove stopwords
    return ' '.join(words)

df['Description'] = df['Description'].apply(preprocess_text)

# Step 4: Implement Jaccard Similarity
# Function to calculate Jaccard Similarity
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

# Calculate similarity scores for one product
def compute_similarity_for_product_name(product_name):
    set_i = set(preprocess_text(product_name).split())
    similarity_scores = []
    for j in range(len(df)):
        set_j = set(df['Description'].iloc[j].split())
        similarity_scores.append(jaccard_similarity(set_i, set_j))
    return similarity_scores

# Step 5: Create Recommendation Function
# Function to recommend products based on Jaccard similarity
def recommend_products_by_name(product_name, top_n=5):
    similarity_scores = compute_similarity_for_product_name(product_name)  # Get similarity scores
    similarity_scores = list(enumerate(similarity_scores))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)  # Sort by similarity
    top_products = similarity_scores[:top_n]  # Get top N products
    recommended_ids = [df.iloc[i[0]]['ProductID'] for i in top_products]
    return df[df['ProductID'].isin(recommended_ids)]

# Step 6: Streamlit Interface
st.title("Product Recommendation System")

# Select product name from dropdown
product_name = st.selectbox("Select a Product Name", df['ProductName'].unique())

# Recommendation Button
if st.button("Get Recommendations"):
    # Save recommendations to session state
    similarity_scores = compute_similarity_for_product_name(product_name)  # Get similarity scores
    recommendations = recommend_products_by_name(product_name, top_n=5)
    
    # Add similarity scores to the recommendations
    recommendations = recommendations.reset_index()  # Reset index for proper mapping
    recommendations['Similarity'] = [
        similarity_scores[i] for i in recommendations.index
    ]  # Add similarity scores to dataframe
    
    st.session_state.recommendations = recommendations.to_dict('records')

# Display recommendations
if "recommendations" in st.session_state:
    st.write("### Recommended Products")
    for index, row in enumerate(st.session_state.recommendations, start=1):  # Add numbering with start=1
        with st.container():  # Create a container for each recommendation
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{index}. {row['ProductName']}**")  # Display the numbered product name in bold
            if col2.button("Detail", key=f"detail_{index}"):
                # Save the selected product details to session state
                st.session_state.selected_product = row
                st.session_state.selected_index = index
            
            # Display details below the relevant product
            if "selected_index" in st.session_state and st.session_state.selected_index == index:
                st.write("#### Product Details")
                product = st.session_state.selected_product
                st.write(f"**Product ID:** {product['ProductID']}")
                st.write(f"**Product Name:** {product['ProductName']}")
                st.write(f"**Brand:** {product['ProductBrand']}")
                st.write(f"**Gender:** {product['Gender']}")
                st.write(f"**Primary Color:** {product['PrimaryColor']}")
                st.write(f"**Description:** {product['Description']}")
                st.write(f"**Similarity Score:** {product['Similarity']:.2f}")
