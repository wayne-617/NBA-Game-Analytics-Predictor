# NBA Game Predictor
A machine-learning model for predicting NBA game outcomes, developed to explore data processing, feature engineering, and building ML pipelines for real-world applications.

## Overview
This project uses data from over 10,000 historical NBA games to predict game outcomes with over 60% accuracy. Key features of the project include:

   - Data scraping from various NBA statistics sources using Python, Playwright, and BeautifulSoup
   - Data organization and enhancement with Pandas
   - Feature selection using Sequential Feature Selection to simplify the dataset
   - Prediction model using Ridge Regression and backtesting for validation

## Getting Started
1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/NBA-Game-Analytics-Predictor.git
   cd NBA-Game-Analytics-Predictor

### To run the data scraper for schedule and games, execute:

  ```bash
  python get_data.py
  ```

### Data Preparation
After collecting raw data, run the data preparation script to clean, organize, and enhance it with additional statistics:
  ```bash
  python parse_data.py
  ```
This step produces a processed dataset ready for feature selection and model training.

## Machine Learning Pipeline
Feature Selection: Using Sequential Feature Selection, the dataset is optimized to use only the most predictive features.

Model Training and Backtesting: Ridge regression is used to train the model, with backtesting applied for performance evaluation.

To train the model and test its accuracy:
  
  - Run predict.ipynb

