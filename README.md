Student Success Analytics Platform

End-to-End Data Engineering and Machine Learning Pipeline

Project Overview

This project builds an end-to-end analytics system to study student learning behavior, retention patterns, and academic risk.

It simulates how real educational platforms process large-scale learning data and convert it into actionable insights using data engineering, analytics, and machine learning.

The system follows a complete pipeline:

Raw Data → ETL Pipeline → Data Warehouse → Analytics Layer → Feature Engineering → Machine Learning Model → Business Insights

Problem Statement

Educational institutions often struggle to:

Identify students at risk of failing or dropping out
Understand student engagement behavior over time
Analyze cohort-level retention trends
Convert raw LMS data into meaningful insights

This project addresses these challenges by building a structured data pipeline and predictive model to support early intervention strategies.

System Architecture

The system is designed as a layered data pipeline:

Data Generation Layer
Synthetic dataset based on OULAD structure is created, including:
Student enrollment data
Assessment records
LMS clickstream data
ETL Pipeline
Extracts raw data
Transforms and cleans datasets
Loads into a structured warehouse
Data Warehouse
A relational structure built using SQLite:
fact_enrollment
fact_weekly_engagement
fact_retention
dim_student
Analytics Layer
Cohort retention analysis
Engagement scoring system
Outcome distribution analysis
Machine Learning Layer
Logistic regression model
Predicts at-risk students
Evaluates model performance using standard metrics
Key Features
1. ETL Pipeline

A complete data pipeline that generates and processes large-scale synthetic student data. It simulates real LMS behavior and structures it into analytical tables.

2. Data Warehouse Design

The project uses a star-schema style warehouse design to support analytics queries and ML feature extraction.

Core tables include:

fact_enrollment
fact_weekly_engagement
fact_retention
dim_student
3. Cohort Retention Analysis

Students are grouped by enrollment cohort to analyze retention over time.

This helps answer:

How student retention changes across academic terms
How dropout patterns vary by cohort
How outcomes are distributed within each cohort
4. Engagement Scoring System

Each student is assigned an engagement score based on LMS activity and academic behavior.

Students are classified into:

ON-TRACK
WATCH
AT-RISK

Key insight:

AT-RISK students show significantly lower pass rates compared to ON-TRACK students.
5. Machine Learning Model

A logistic regression model is trained to predict at-risk students using engineered features from the engagement layer.

The model includes:

Train/test split
Evaluation metrics (accuracy, precision, recall, ROC-AUC)
Confusion matrix analysis
Key Insights
Engagement score is strongly correlated with academic outcomes
AT-RISK students have a very low pass probability compared to ON-TRACK students
Cohort behavior remains consistent across different academic terms
Early behavioral signals are effective predictors of student performance
Tech Stack
Python
Pandas, NumPy
Scikit-learn
SQLite (Data Warehouse)
Matplotlib / Seaborn
ETL pipeline design patterns
Project Structure
student-success-analytics/
│
├── etl/              Data extraction, transformation, loading
├── analysis/         Cohort, engagement, and ML models
├── sql/              Warehouse schema and queries
├── dashboards/      Generated visualizations
├── data/            Raw and processed datasets
├── docs/            Documentation
└── README.md
How to Run

Install dependencies:

pip install -r requirements.txt

Run the full pipeline:

python etl/run_pipeline.py

Run analytics modules:

python analysis/retention_cohort.py
python analysis/engagement_scoring.py
python analysis/at_risk_model.py
What This Project Demonstrates

This project demonstrates practical experience in:

Building end-to-end data pipelines
Designing a data warehouse schema
Performing cohort and behavioral analytics
Engineering features for machine learning
Building and evaluating predictive models
Translating raw data into business insights
Future Improvements
Deploy model as an API using FastAPI
Build interactive dashboard using Power BI or Streamlit
Add real-time data streaming simulation
Deploy pipeline on cloud infrastructure (AWS or Azure)
Author

This project was built to demonstrate end-to-end skills in data engineering, analytics, and machine learning for real-world educational data systems.