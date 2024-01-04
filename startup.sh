#!/bin/bash

# 创建 ./out 目录，如果它不存在
mkdir -p ./out

# 创建或更新日志文件
touch ./out/kafkaToSpark.out
touch ./out/writeIntoKafka.out
touch ./out/frontend.out
touch ./out/backend.out

docker-compose up -d
echo "容器初始化开始......"
echo "请等待一会，正在拉起所有容器......"
sleep 30  # 等待

docker exec hive-server hive -f /csv/hive.sql
echo "hive表初始化结束"
docker exec namenode hdfs dfs -rm -r /model
docker exec namenode hdfs dfs -put /model /model
echo "hdfs初始化结束"
docker exec spark-master bash /python/stopAll.sh
docker exec spark-master nohup spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.8 /python/kafkaToSpark.py > ./out/kafkaToSpark.out 2>&1 &
echo "Spark Streaming启动"
docker exec spark-master nohup python /python/writeIntoKafka.py > ./out/writeIntoKafka.out 2>&1 &
echo "爬虫写入kafka启动"
docker exec spark-master nohup python /python/frontend/web_vis/manage.py runserver 0.0.0.0:8000 > ./out/frontend.out 2>&1 &
echo "前端启动"
docker exec spark-master nohup spark-submit --master spark://spark-master:7077 /python/backend/integration_app.py > ./out/backend.out 2>&1 &
echo "后端启动"

docker exec hive-metastore-postgresql createdb -U postgres hue_mate
docker-compose restart hue
docker exec hue /usr/share/hue/build/env/bin/hue syncdb
docker exec hue /usr/share/hue/build/env/bin/hue migrate
docker-compose restart hue
echo "hue初始化完成"

echo "------项目启动成功------"