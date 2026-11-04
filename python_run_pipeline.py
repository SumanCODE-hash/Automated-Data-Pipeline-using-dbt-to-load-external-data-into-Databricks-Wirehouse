import os
import subprocess
from google.cloud import bigquery
import pandas as pd

def download_trends_data():
    client = bigquery.Client()

    query = """
    SELECT 
        country_name, 
        term, 
        rank, 
        percent_gain,
        refresh_date AS snapshot_date
    FROM `bigquery-public-data.google_trends.international_top_rising_terms`
    WHERE 
        country_name IN (
            'United Kingdom', 'Germany', 'France', 'Italy', 'Spain', 
            'Denmark', 'Sweden', 'Norway', 'Finland', 'Netherlands', 
            'Belgium', 'Switzerland', 'Austria'
        )
        AND rank <= 20
        AND refresh_date = DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)
    GROUP BY term, country_name, rank, percent_gain, refresh_date
    ORDER BY country_name ASC, rank ASC;
    """
    
    print("🚀 Executing BigQuery extraction...")
    df = client.query(query).to_dataframe()
    
    # --- UPDATED PATH: Points cleanly into your nested 'trends-dbt' folder ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "analytics", "trends-dbt", "seeds", "raw_trends.csv")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✅ Success! Saved {len(df)} rows locally to: {output_path}")

def run_pipeline_dbt():
    print("🛠️ Initiating local dbt transformations...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dbt_project_dir = os.path.join(base_dir, "analytics", "trends-dbt")
    
    # 1. Run seed first to establish the table inside the 'default' Databricks schema
    print("🌱 Pushing raw seed data to Databricks 'default' schema...")
    subprocess.run(["dbt", "seed"], cwd=dbt_project_dir)
    
    # 2. Run the models to build transformations
    print("🔄 Running dbt models...")
    result = subprocess.run(["dbt", "run"], cwd=dbt_project_dir, capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print("❌ dbt failed with errors:")
        print(result.stderr)
    else:
        print("🎉 dbt pipeline executed successfully!")
if __name__ == "__main__":
    download_trends_data()
    run_pipeline_dbt()
