import pandas as pd
import pyodbc
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings

# Suppress minor formatting warnings
warnings.filterwarnings('ignore')

print("Starting Machine Learning Pipeline...")

# ==========================================
# STEP 1: EXTRACT (Connect to SQL Server)
# ==========================================
print("Connecting to SQL Server database...")

# REPLACE 'YOUR_SERVER_NAME_HERE' with your actual SSMS server name!
# Keep the Trusted_Connection=yes so it uses your Windows login automatically.
server_name = r'LAPTOP-M870H89R\SQLEXPRESS' 

try:
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};'
        f'SERVER={server_name};'
        f'DATABASE=RFM_Segmentation;'
        f'Trusted_Connection=yes;'
    )
    
    # Run the SQL Query to grab our clean View
    sql_query = "SELECT * FROM vw_RFM_Base"
    df = pd.read_sql(sql_query, conn)
    print(f"Successfully extracted {len(df)} customers from SQL!")

except Exception as e:
    print(f"SQL Connection Failed. Error: {e}")
    exit()

# ==========================================
# STEP 2: PREPROCESS (Scaling the Data)
# ==========================================
print("Preprocessing data for the algorithm...")

# K-Means measures distance. Because 'Monetary' is in the thousands, and 'Frequency' is small (like 5 or 10),
# the algorithm will unfairly prioritize Monetary. We must "scale" them so they are weighted equally.
features = df[['Recency', 'Frequency', 'Monetary']]

scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# ==========================================
# STEP 3: MACHINE LEARNING (K-Means Clustering)
# ==========================================
print("Running K-Means Clustering Algorithm...")

# We are telling the AI to group our customers into exactly 4 segments
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)

# The algorithm studies the scaled data and assigns a Cluster Number (0, 1, 2, or 3) to every customer
df['Cluster'] = kmeans.fit_predict(scaled_features)

# ==========================================
# STEP 4: LOAD (Export for Power BI)
# ==========================================
print("Exporting segmented data to Excel...")

# Save the final dataset with the new 'Cluster' column attached
output_filename = "Customer_RFM_Segments.xlsx"
df.to_excel(output_filename, index=False, engine='openpyxl')

print(f"Success! Pipeline complete. File saved as: {output_filename}")