# %%
from google.colab import files

uploaded = files.upload()

# %%
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


# %%
df = pd.read_csv('honeypot_logs.logs.csv')

# %%
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import numpy as np

# 🧪 Load your dataset
# df = pd.read_csv('your_dataset.csv')  # or however you're loading it

# 🧹 Clean and Feature Engineer
df['referrer'] = df['referrer'].fillna('')
df['userAgent'] = df['userAgent'].fillna('')
df['interactionType'] = df['interactionType'].fillna('unknown')

df['referrer_len'] = df['referrer'].apply(len)
df['userAgent_len'] = df['userAgent'].apply(len)
df['userAgent_bot_flag'] = df['userAgent'].str.contains('bot|crawl|spider|crawler|slurp', case=False, na=False).astype(int)

# 🏷️ Encode interactionType
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
interaction_encoded = encoder.fit_transform(df[['interactionType']])
interaction_df = pd.DataFrame(interaction_encoded, columns=encoder.get_feature_names_out(['interactionType']))

# 🧩 Combine all features
features = pd.concat([
    df[['referrer_len', 'userAgent_len', 'userAgent_bot_flag']],
    interaction_df
], axis=1)

# 🧪 Use botScore > 0.5 as Bot, else Human (or adjust as per your logic)
df['Label'] = df['botScore'].apply(lambda x: 1 if x >= 0.5 else 0)

# 🧠 Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(features, df['Label'], test_size=0.2, random_state=42)

# 🌲 Train Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 📊 Evaluate
y_pred = model.predict(X_test)

print("✅ Accuracy Score:", accuracy_score(y_test, y_pred))
print("\n✅ Classification Report:\n", classification_report(y_test, y_pred))
print("✅ Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 📈 Feature Importance
importances = pd.Series(model.feature_importances_, index=features.columns)
print("\n📊 Feature Importance:\n", importances.sort_values(ascending=False))


# %%
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder

# ✅ Load your data
df = pd.read_csv("honeypot_logs.logs.csv")  # Replace with actual file or source

# ✅ Label Creation: Assume bots have a 'botScore' above a threshold (e.g., 0.5)
df['Label'] = df['botScore'].apply(lambda x: 1 if x >= 0.5 else 0)

# ✅ Feature Engineering
df['referrer'] = df['referrer'].fillna('')
df['referrer_len'] = df['referrer'].apply(len)

df['userAgent'] = df['userAgent'].fillna('')
df['userAgent_len'] = df['userAgent'].apply(len)

df['userAgent_bot_flag'] = df['userAgent'].str.contains('bot|crawl|spider|python', case=False, na=False).astype(int)

# ✅ Features WITHOUT interactionType to avoid data leakage
features = df[['referrer_len', 'userAgent_len', 'userAgent_bot_flag']]
labels = df['Label']

# ✅ Split data
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# ✅ Train Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ✅ Predict
y_pred = model.predict(X_test)

# ✅ Evaluate
print("✅ Accuracy Score:", accuracy_score(y_test, y_pred))
print("\n✅ Classification Report:")
print(classification_report(y_test, y_pred))
print("✅ Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ✅ Feature Importance
importances = pd.Series(model.feature_importances_, index=features.columns).sort_values(ascending=False)
print("\n📊 Feature Importance:")
print(importances)

# ✅ Optional: View predictions
output_df = X_test.copy()
output_df['Actual'] = y_test
output_df['Predicted'] = y_pred
output_df['Predicted_Label'] = output_df['Predicted'].map({1: 'Bot', 0: 'Human'})
print("\n🔍 Sample Prediction Output:")
print(output_df.head())


# %%
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import resample
import warnings
warnings.filterwarnings("ignore")

# 🔹 Load your dataset
df = pd.read_csv('honeypot_logs.logs.csv')  # Replace with your dataset path

# 🔹 Extract relevant features
df['referrer_len'] = df['referrer'].fillna('').apply(len)
df['userAgent_len'] = df['userAgent'].fillna('').apply(len)
df['userAgent_bot_flag'] = df['userAgent'].str.contains('bot|crawl|spider|curl|wget', case=False, na=False).astype(int)

# 🔹 Extract Label (Assuming bots have score ≥ 0.5)
df['Label'] = df['botScore'].apply(lambda x: 1 if x >= 0.5 else 0)

# ✅ Optional: Upsample minority class (Human = 0)
df_majority = df[df.Label == 1]
df_minority = df[df.Label == 0]

df_minority_upsampled = resample(df_minority,
                                 replace=True,
                                 n_samples=len(df_majority),
                                 random_state=42)

df = pd.concat([df_majority, df_minority_upsampled])

# 🔹 Features and Labels
features = ['referrer_len', 'userAgent_len', 'userAgent_bot_flag']
X = df[features]
y = df['Label']

# 🔹 Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Train RandomForest with class_weight='balanced'
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# 🔍 Predictions and Evaluation
y_pred = model.predict(X_test)

print("✅ Accuracy Score:", round(accuracy_score(y_test, y_pred), 4))
print("\n✅ Classification Report:\n", classification_report(y_test, y_pred))
print("\n✅ Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 📊 Feature Importance
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\n📊 Feature Importance:\n", importances)

# 🔍 Sample Predictions
sample = X_test.copy()
sample['Actual'] = y_test.values
sample['Predicted'] = y_pred
sample['Predicted_Label'] = sample['Predicted'].map({0: 'Human', 1: 'Bot'})
print("\n🔍 Sample Prediction Output:\n", sample.head())


# %%
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# 📥 Load your data
# Assuming your dataset is in a DataFrame called `df`
# Make sure these columns exist in your df
# Columns: 'userAgent', 'referrer', 'interactionType', 'botScore', 'details.query.token', 'details.formData.honeypot_field', etc.

# 🧹 Fill NaNs
df['userAgent'] = df['userAgent'].fillna('')
df['referrer'] = df['referrer'].fillna('')
df['interactionType'] = df['interactionType'].fillna('unknown')

# 🧠 Feature Engineering
df['userAgent_len'] = df['userAgent'].str.len()
df['referrer_len'] = df['referrer'].str.len()

# UserAgent Category
df['userAgent_browser'] = df['userAgent'].str.extract(r'(Chrome|Firefox|Safari|Edge|Bot|Crawler|Scrapy|curl)', expand=False).fillna('Other')

# Referrer Domain
df['referrer_domain'] = df['referrer'].str.extract(r'https?://(?:www\.)?([^/]+)', expand=False).fillna('unknown')

# Token Present or Not
df['has_token'] = df['details.query.token'].notna().astype(int)

# Honeypot field filled or not
df['honeypot_filled'] = df['details.formData.honeypot_field'].notna().astype(int)

# Convert target label
df['label'] = df['botScore'].apply(lambda x: 1 if x > 0.5 else 0)

# One-hot encode interactionType, userAgent_browser, referrer_domain
interaction_ohe = pd.get_dummies(df['interactionType'], prefix='interactionType')
browser_ohe = pd.get_dummies(df['userAgent_browser'], prefix='browser')
domain_ohe = pd.get_dummies(df['referrer_domain'], prefix='domain')

# Combine features
features = pd.concat([
    df[['referrer_len', 'userAgent_len', 'userAgent_bot_flag', 'has_token', 'honeypot_filled']],
    interaction_ohe,
    browser_ohe,
    domain_ohe
], axis=1)

# 🎯 Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, df['label'], test_size=0.2, random_state=42, stratify=df['label'])

# 🧠 Train the model
model = RandomForestClassifier(n_estimators=200, max_depth=10, class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

# 🧪 Evaluate
y_pred = model.predict(X_test)

print("✅ Accuracy Score:", round(accuracy_score(y_test, y_pred), 4))
print("\n✅ Classification Report:\n", classification_report(y_test, y_pred))
print("✅ Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 📊 Feature Importance
importances = pd.Series(model.feature_importances_, index=features.columns)
importances = importances.sort_values(ascending=False)
print("\n📊 Top 10 Feature Importances:\n", importances.head(10))

# 🔍 Sample predictions
sample = X_test.copy()
sample['Actual'] = y_test
sample['Predicted'] = y_pred
sample['Predicted_Label'] = sample['Predicted'].map({0: 'Human', 1: 'Bot'})
print("\n🔍 Sample Prediction Output:\n", sample.head())


# %%
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import resample
import warnings
warnings.filterwarnings("ignore")

# 🔹 Load Dataset
df = pd.read_csv('honeypot_logs.logs.csv')  # Update path if needed

# 🔹 Drop rows with missing target
df = df[df['botScore'].notna()]

# 🔹 Feature Engineering
df['referrer_len'] = df['referrer'].fillna('').apply(len)
df['userAgent_len'] = df['userAgent'].fillna('').apply(len)
df['userAgent_bot_flag'] = df['userAgent'].str.contains('bot|crawl|spider|curl|wget', case=False, na=False).astype(int)

# 🔹 Binary Label: 1 = Bot, 0 = Human
df['Label'] = df['botScore'].apply(lambda x: 1 if x >= 0.5 else 0)

# 🔹 Feature Set
features = ['referrer_len', 'userAgent_len', 'userAgent_bot_flag']
X = df[features]
y = df['Label']

# 🔹 Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 🔹 Upsample minority class in training set only
train_df = pd.concat([X_train, y_train], axis=1)
majority = train_df[train_df.Label == 1]
minority = train_df[train_df.Label == 0]

minority_upsampled = resample(minority,
                              replace=True,
                              n_samples=len(majority),
                              random_state=42)

train_balanced = pd.concat([majority, minority_upsampled])
X_train_bal = train_balanced[features]
y_train_bal = train_balanced['Label']

# ✅ Random Forest Classifier
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced_subsample',  # balances using bootstrap sample
    max_depth=10  # helps prevent overfitting
)
model.fit(X_train_bal, y_train_bal)

# 🔍 Predictions
y_pred = model.predict(X_test)

# ✅ Evaluation
print("✅ Accuracy Score:", round(accuracy_score(y_test, y_pred), 4))
print("\n✅ Classification Report:\n", classification_report(y_test, y_pred, target_names=['Human', 'Bot']))
print("\n✅ Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 📊 Feature Importance
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\n📊 Feature Importance:\n", importances)

# 🔍 Sample Predictions
sample = X_test.copy()
sample['Actual'] = y_test.values
sample['Predicted'] = y_pred
sample['Predicted_Label'] = sample['Predicted'].map({0: 'Human', 1: 'Bot'})
print("\n🔍 Sample Prediction Output:\n", sample.head())


# %%
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.utils import resample
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# Load your dataset
df = pd.read_csv('honeypot_logs.logs.csv')

# Feature Engineering
df['referrer_len'] = df['referrer'].fillna('').apply(len)
df['userAgent_len'] = df['userAgent'].fillna('').apply(len)
df['userAgent_bot_flag'] = df['userAgent'].str.contains('bot|crawl|spider|curl|wget', case=False, na=False).astype(int)
df['Label'] = df['botScore'].apply(lambda x: 1 if x >= 0.5 else 0)

# Split features and label
features = ['referrer_len', 'userAgent_len', 'userAgent_bot_flag']
X = df[features]
y = df['Label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Upsample minority class in training only
train_df = pd.concat([X_train, y_train], axis=1)
majority = train_df[train_df.Label == 1]
minority = train_df[train_df.Label == 0]

minority_upsampled = resample(minority,
                              replace=True,
                              n_samples=len(majority),
                              random_state=42)

train_balanced = pd.concat([majority, minority_upsampled])
X_train_bal = train_balanced[features]
y_train_bal = train_balanced['Label']

# Normalize (optional but helps with some models)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_bal)
X_test_scaled = scaler.transform(X_test)

# Try Gradient Boosting or Logistic Regression
# model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5)
model = LogisticRegression(class_weight='balanced', random_state=42)
model.fit(X_train_scaled, y_train_bal)

# Predict
y_pred = model.predict(X_test_scaled)

# Evaluation
print("✅ Accuracy Score:", round(accuracy_score(y_test, y_pred), 4))
print("\n✅ Classification Report:\n", classification_report(y_test, y_pred, target_names=['Human', 'Bot']))
print("\n✅ Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Sample predictions
sample = X_test.copy()
sample['Actual'] = y_test.values
sample['Predicted'] = y_pred
sample['Predicted_Label'] = sample['Predicted'].map({0: 'Human', 1: 'Bot'})
print("\n🔍 Sample Prediction Output:\n", sample.head())



