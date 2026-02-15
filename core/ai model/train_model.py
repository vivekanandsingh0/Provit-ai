
import sys
import os

# Check if required packages are installed
try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, accuracy_score
    import joblib
except ImportError as e:
    print(f"\n❌ Missing Requirement: {e.name}")
    print(f"Please install dependencies:\n\tpip install numpy pandas scikit-learn joblib")
    sys.exit(1)

# --- 1. Synthetic Data Generation ---
def generate_loan_data(n_samples=2000):
    print(f"Generating synthetic loan data for {n_samples} applicants...")
    np.random.seed(42)  # For reproducibility

    # Realistic Featues
    # 1. Income (Annual)
    incomes = np.random.lognormal(mean=11.0, sigma=0.5, size=n_samples)  # Roughly $30k - $150k distribution

    # 2. FICO Score (300-850)
    fico_scores = np.random.normal(loc=700, scale=100, size=n_samples).clip(300, 850)

    # 3. Debt-to-Income (DTI) ratio (0% - 60%)
    dtis = np.random.beta(a=2, b=5, size=n_samples) * 0.60

    # 4. Loan Amount ($5k - $50k)
    loan_amounts = np.random.randint(low=5000, high=50000, size=n_samples)

    # --- 2. Ground Truth Logic (The "Hidden" Rules) ---
    # We define who defaults so the model has something to learn.
    # Logic: Default if (Low FICO) OR (High DTI + Low Income)
    
    defaults = []
    for i in range(n_samples):
        score = 0
        
        # Penalize Low FICO
        if fico_scores[i] < 620: score += 5
        elif fico_scores[i] < 680: score += 2

        # Penalize High DTI
        if dtis[i] > 0.45: score += 3
        elif dtis[i] > 0.35: score += 1

        # Penalize Low Income relative to Loan
        if loan_amounts[i] > (incomes[i] * 0.5): score += 3  # Loan > 50% of annual income

        # Decision Threshold (with some noise)
        prob_default = 1 / (1 + np.exp(-(score - 3.5))) # Sigmoid function
        is_default = 1 if np.random.random() < prob_default else 0
        defaults.append(is_default)

    # Create DataFrame
    df = pd.DataFrame({
        'annual_income': incomes,
        'fico_score': fico_scores,
        'dti_ratio': dtis,
        'loan_amount': loan_amounts,
        'defaulted': defaults # Target
    })
    
    return df

# --- 3. Model Training ---
def train_and_save():
    # Load Data
    df = generate_loan_data()
    
    X = df.drop('defaulted', axis=1)
    y = df['defaulted']

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train (Random Forest - Explainable & Robust)
    print("\nTraining RandomForest Model (100 trees)...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n--- Model Performance ---")
    print(f"Accuracy: {acc:.2%}")
    print("\nFeature Importance:")
    for name, importance in zip(X.columns, clf.feature_importances_):
        print(f"  - {name}: {importance:.4f}")

    # Report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Paid Back', 'Defaulted']))

    # Save
    model_path = "loan_risk_model.pkl"
    joblib.dump(clf, model_path)
    print(f"\n✅ Model Saved to: {os.path.abspath(model_path)}")

if __name__ == "__main__":
    train_and_save()
