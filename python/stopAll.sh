p1=$(ps aux | grep "python /python/kafkaToSpark.py" | grep -v grep | grep -v /opt | awk '{print $2}')
if [ "$p1" ]; then
    kill -9 "$p1"
    echo "进程 $p1 已终止"
fi
p2=$(ps aux | grep "python /python/writeIntoKafka.py" | grep -v grep | awk '{print $2}')
if [ "$p2" ]; then
    kill -9 "$p2"
    echo "进程 $p2 已终止"
fi
p3=$(ps aux | grep "/opt/bitnami/python/bin/python /python/frontend/web_vis/manage.py runserver 0.0.0.0:8000" | grep -v grep | awk '{print $2}')
if [ "$p3" ]; then
    kill -9 "$p3"
    echo "进程 $p3 已终止"
fi
p3=$(ps aux | grep "python /python/frontend/web_vis/manage.py runserver 0.0.0.0:8000" | grep -v grep | grep -v /opt | awk '{print $2}')
if [ "$p3" ]; then
    kill -9 "$p3"
    echo "进程 $p3 已终止"
fi
p4=$(ps aux | grep "python /python/backend/integration_app.py" | grep -v grep | grep -v /opt | awk '{print $2}')
if [ "$p4" ]; then
    kill -9 "$p4"
    echo "进程 $p4 已终止"
fi