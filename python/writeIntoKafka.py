from kafka import KafkaProducer
import json
import pandas as pd
import random
import time
from datetime import datetime

producer = KafkaProducer(bootstrap_servers='kafka:9092', api_version=(3, 6, 1))
topic = 'comment-topic'
df = pd.read_csv('/python/data/comments.csv', encoding='utf-8')
cnt = 5 # 每次爬几条评论
minute = 5 # 每次爬取之间间隔几分钟
seconds = 5 # 每次爬取之间间隔几秒钟
while(True):
    print("write!")
    random_row = df.sample(n=cnt)
    json_data = random_row.to_json(orient='records', force_ascii=False)
    json_data_list = json.loads(json_data)
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    for j in json_data_list:
        j['create_time'] = timestamp_str
        message = json.dumps(j)
        producer.send(topic, value=message.encode('utf-8'))
    producer.flush()
    time.sleep(minute*60)

# producer.close()
