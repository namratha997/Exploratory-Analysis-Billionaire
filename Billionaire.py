import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import streamlit as st
from pathlib import Path

# Load the dataset
billionaire_data = pd.read_csv("C:/Users/namra/OneDrive/Desktop/Project1/Billionaires Statistics Dataset.csv", encoding='unicode_escape')

# Data cleaning
df = billionaire_data.drop(columns=[
    'state', 'residenceStateRegion', 'cpi_country', 'cpi_change_country', 'gdp_country',
    'gross_tertiary_education_enrollment', 'gross_primary_education_enrollment_country',
    'life_expectancy_country', 'tax_revenue_country_country', 'total_tax_rate_country',
    'population_country', 'latitude_country', 'longitude_country', 'date'
])

df.fillna({
    'city': 'Unknown',
    'country': 'Unknown',
    'age': 65.14,
    'organization': 'Unknown',
    'birthDate': '1/1/1111',
    'title': 'unknown',
    'birthYear': 0,
    'birthDay': 0,
    'birthMonth': 'none',
    'firstName': 'Unknown'
}, inplace=True)

df['birthYear'] = df['birthYear'].astype(int)
df['birthDay'] = df['birthDay'].astype(int)

# Connect to SQLite database
Path('billion_dat.db').touch()
billion_conn = sqlite3.connect('billion_dat.db')
df.to_sql('billion_dat', billion_conn, if_exists='replace', index=False)

# Custom CSS for styling
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #222;
            text-align: center;
            padding-bottom: 100px;
            padding-top: 30px;
        }
        .subheader {
            font-size: 22px;
            font-weight: bold;
            color: #444;
            padding: 10px 0;
            text-align: center;
        }
        .stPlotlyChart, .stImage {
            border-radius: 10px;
            padding: 10px;
            background-color: #fff;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit Dashboard Title
st.markdown('<h1 class="title">Billionaire Statistics Dashboard</h1>', unsafe_allow_html=True)

# Query 1: Top Industries Producing the Most Billionaires
top_industries = pd.read_sql('''
    SELECT industries, COUNT(*) AS billionaire_count
    FROM billion_dat
    GROUP BY industries
    ORDER BY billionaire_count DESC''', billion_conn)

# Query 2: Distribution of Male and Female Billionaires Across Industries
male_billionaires = pd.read_sql('''
    SELECT industries, COUNT(gender) AS billionaire_count
    FROM billion_dat
    WHERE gender = 'M'
    GROUP BY industries
    ORDER BY billionaire_count DESC
    ''', billion_conn)

female_billionaires = pd.read_sql('''
    SELECT industries, COUNT(gender) AS billionaire_count
    FROM billion_dat
    WHERE gender = 'F'
    GROUP BY industries
    ORDER BY billionaire_count DESC
    ''', billion_conn)

# Query 3: Top 10 Countries with the Most Billionaires
top_countries = pd.read_sql('''
    SELECT country, COUNT(*) AS billionaire_count
    FROM billion_dat
    GROUP BY country
    ORDER BY billionaire_count DESC
    LIMIT 10;
    ''', billion_conn)

# Query 4: Average Net Worth of Billionaires by Industry
avg_net_worth_by_industry = pd.read_sql('''
    SELECT industries, AVG(finalWorth) AS avg_net_worth
    FROM billion_dat
    GROUP BY industries
    ORDER BY avg_net_worth DESC''', billion_conn)

# Add gender column to both DataFrames
male_billionaires['gender'] = 'Male'
female_billionaires['gender'] = 'Female'

# Combine both DataFrames
combined_billionaires = pd.concat([male_billionaires, female_billionaires])

# Create two columns for side-by-side visualization
col1, col2 = st.columns(2)

# Chart 1: Top Industries Producing the Most Billionaires
with col1:
    st.markdown('<h3 class="subheader">Top Industries Producing the Most Billionaires</h3>', unsafe_allow_html=True)
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    sns.barplot(x='industries', y='billionaire_count', data=top_industries, palette='viridis', ax=ax1)
    ax1.set_xlabel('Industry', fontsize=12)
    ax1.set_ylabel('Number of Billionaires', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig1)

# Chart 2: Male vs Female Billionaires by Industry
with col2:
    st.markdown('<h3 class="subheader">Male vs Female Billionaires by Industry</h3>', unsafe_allow_html=True)
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    sns.barplot(x='industries', y='billionaire_count', hue='gender', data=combined_billionaires, palette='Set2', ax=ax2)
    ax2.set_xlabel('Industry', fontsize=12)
    ax2.set_ylabel('Number of Billionaires', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig2)

# Create another two columns for additional visualizations
col3, col4 = st.columns(2)

# Chart 3: Top 10 Countries with the Most Billionaires
with col3:
    st.markdown('<h3 class="subheader">Top 10 Countries with the Most Billionaires</h3>', unsafe_allow_html=True)
    fig3, ax3 = plt.subplots(figsize=(6, 4.7))
    sns.barplot(x='country', y='billionaire_count', data=top_countries, palette='coolwarm', ax=ax3)
    ax3.set_xlabel('Country', fontsize=12)
    ax3.set_ylabel('Number of Billionaires', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig3)

# Chart 4: Average Net Worth of Billionaires by Industry
with col4:
    st.markdown('<h3 class="subheader">Average Net Worth by Industry</h3>', unsafe_allow_html=True)
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    sns.barplot(x='industries', y='avg_net_worth', data=avg_net_worth_by_industry, palette='coolwarm', ax=ax4)
    ax4.set_xlabel('Industry', fontsize=12)
    ax4.set_ylabel('Average Net Worth (in billion USD)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig4)

# Close the database connection
billion_conn.close()
