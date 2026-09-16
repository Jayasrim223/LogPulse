from app.analyzer import load_logs
from app.database import insert_logs

df = load_logs()

insert_logs(df)