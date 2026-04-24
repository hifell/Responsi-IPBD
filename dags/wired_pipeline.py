from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import psycopg2

def fetch_data(ti):
    url = "http://host.docker.internal:8001/articles" 
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        ti.xcom_push(key='data', value=data)
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise e

def save_to_db(ti):
    data = ti.xcom_pull(task_ids='fetch_task', key='data')
    articles = data[0].get('articles', [])

    conn = psycopg2.connect(
        host="postgres_tugas", 
        database="wired_db",
        user="admin",
        password="admin123",
        port=5432
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT,
            url TEXT,
            author TEXT,
            description TEXT,
            scraped_at TIMESTAMP
        )
    """)
    
    for article in articles:
        cursor.execute("""
            INSERT INTO articles (title, url, author, description, scraped_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            article.get('title'), 
            article.get('url'),    
            article.get('author', 'Unknown'),
            article.get('description', 'N/A'),
            article.get('scraped_at')
        ))

    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    dag_id='wired_pipeline_v2',
    start_date=datetime(2026, 4, 24), 
    schedule=None,
    catchup=False
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_task',
        python_callable=fetch_data
    )

    save_task = PythonOperator(
        task_id='save_task',
        python_callable=save_to_db
    )

    fetch_task >> save_task