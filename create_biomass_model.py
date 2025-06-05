#!/usr/bin/env python3
"""
Script to create the biomass regression model.
This runs the analysis from the notebook to generate models/biomass_rf.pkl
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from joblib import dump, load
import warnings
import os

warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

print("🌿 Kelp Biomass Regression Analysis")
print("=" * 40)

# 1. Load sample data
print("📊 Loading sample data...")
samples_df = pd.read_csv('data/mock_samples.csv')

print(f"   Loaded {len(samples_df)} sample points")
print(f"   Longitude range: {samples_df['lon'].min():.4f} to {samples_df['lon'].max():.4f}")
print(f"   Latitude range: {samples_df['lat'].min():.4f} to {samples_df['lat'].max():.4f}")
print(f"   Biomass range: {samples_df['kg_dry'].min():.1f} to {samples_df['kg_dry'].max():.1f} kg")

# 2. Generate mock spectral data
print("\n🛰️ Generating spectral indices...")

# Add some spatial correlation based on location
location_factor = (samples_df['lon'] + 123.4) * 100 + (samples_df['lat'] - 48.4) * 100

# FAI: Higher values for higher biomass + some noise + spatial correlation
fai_base = 0.01 + (samples_df['kg_dry'] - samples_df['kg_dry'].min()) / (samples_df['kg_dry'].max() - samples_df['kg_dry'].min()) * 0.15
fai_noise = np.random.normal(0, 0.02, len(samples_df))
fai_spatial = location_factor * 0.001
samples_df['fai'] = fai_base + fai_noise + fai_spatial

# NDRE: Similar correlation but different range
ndre_base = 0.1 + (samples_df['kg_dry'] - samples_df['kg_dry'].min()) / (samples_df['kg_dry'].max() - samples_df['kg_dry'].min()) * 0.4
ndre_noise = np.random.normal(0, 0.05, len(samples_df))
ndre_spatial = location_factor * 0.002
samples_df['ndre'] = ndre_base + ndre_noise + ndre_spatial

# Ensure realistic ranges
samples_df['fai'] = np.clip(samples_df['fai'], -0.05, 0.3)
samples_df['ndre'] = np.clip(samples_df['ndre'], -0.2, 0.8)

print(f"   FAI range: {samples_df['fai'].min():.3f} to {samples_df['fai'].max():.3f}")
print(f"   NDRE range: {samples_df['ndre'].min():.3f} to {samples_df['ndre'].max():.3f}")

# 3. Prepare data for modeling
print("\n📈 Preparing data for modeling...")
X = samples_df[['fai', 'ndre']].values
y = samples_df['kg_dry'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=None
)

print(f"   Training set: {X_train.shape[0]} samples")
print(f"   Test set: {X_test.shape[0]} samples")

# 4. Train models
print("\n🤖 Training models...")

# Log-Linear Regression
y_train_log = np.log(y_train + 1)
y_test_log = np.log(y_test + 1)

linear_model = LinearRegression()
linear_model.fit(X_train, y_train_log)

y_pred_linear_log = linear_model.predict(X_test)
y_pred_linear = np.maximum(np.exp(y_pred_linear_log) - 1, 0)

linear_mse = mean_squared_error(y_test, y_pred_linear)
linear_r2 = r2_score(y_test, y_pred_linear)

print(f"   Log-Linear - MSE: {linear_mse:.2f}, R²: {linear_r2:.3f}")

# Random Forest Regression
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42
)

rf_model.fit(X_train, y_train)
y_pred_rf = np.maximum(rf_model.predict(X_test), 0)

rf_mse = mean_squared_error(y_test, y_pred_rf)
rf_r2 = r2_score(y_test, y_pred_rf)

print(f"   Random Forest - MSE: {rf_mse:.2f}, R²: {rf_r2:.3f}")

# 5. Save the Random Forest model
print("\n💾 Saving model...")
os.makedirs('models', exist_ok=True)
model_path = 'models/biomass_rf.pkl'

dump(rf_model, model_path)
print(f"   Model saved to: {model_path}")

# 6. Test the saved model
print("\n✅ Testing saved model...")
try:
    loaded_model = load(model_path)
    test_input = np.array([[0.1, 0.3], [0.05, 0.2]])
    test_predictions = loaded_model.predict(test_input)
    
    print(f"   Test predictions: {test_predictions}")
    print(f"   All predictions non-negative: {np.all(test_predictions >= 0)}")
    print(f"   Model ready for unit tests!")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n🎉 Biomass regression model creation complete!")
print(f"   Features: FAI, NDRE")
print(f"   Model: Random Forest Regressor")
print(f"   Performance: R² = {rf_r2:.3f}, MSE = {rf_mse:.2f}") 