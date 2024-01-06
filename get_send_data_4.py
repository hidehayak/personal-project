import boto3
import json
import time
import smbus
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from decimal import Decimal

# AWS IoT Coreの設定
host = "a3ci7drpivgj5u-ats.iot.ap-northeast-1.amazonaws.com"
rootCAPath = "/home/hidehayak/certs/Amazon-root-CA-1.pem"
certificatePath = "/home/hidehayak/certs/device.pem.crt"
privateKeyPath = "/home/hidehayak/certs/private.pem.key"
port = 8883
clientId = "raspberrypi"
topic = "topic/luminosity"

# AWS IoT SDKの初期化
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWS IoT Coreに接続
myAWSIoTMQTTClient.connect()

# BH1750の設定
i2c = smbus.SMBus(1)
i2c.write_byte(0x23, 0x10)
time.sleep(0.5)

# 照度データを取得
def get_lux():
    lux = i2c.read_word_data(0x23, 0x11)
    lux = ((lux & 0xff00) >> 8) | ((lux & 0xff) << 8)
    lux = lux / 1.2
    return lux

# 照度データをAWS IoT Coreに送信
while True:
    lux = get_lux()
    message = {}
    message['lux'] = lux
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    print('Published topic %s: %s\n' % (topic, messageJson))
    # 照度データをDynamo DBに保存
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
    table = dynamodb.Table('luminosity_data') # Dynamo DBテーブルの名前
    lux = Decimal(str(lux))
    table.put_item(
        Item={
            'sample_time': int(time.time()), # パーティションキーの値（現在のUNIXタイムスタンプ）
            'device_id': clientId, # ソートキーの値（クライアントID）
            'lux': lux # 照度データ
        }
    )
    time.sleep(900)
