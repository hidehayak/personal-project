import os
import json
import urllib.request

# Switchbot APIの設定
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
DEVICE_ID = os.environ.get('DEVICE_ID')
API_BASE_URL = 'https://api.switch-bot.com'

# 朝目覚めに最適なルクス
LUX_THRESHOLD_ON = 1000

# 外が暗くなってきたらカーテンを閉じるルクス
LUX_THRESHOLD_OFF = 100

# Switchbotカーテンを操作する関数
def control_curtain(command):
    headers = {
        'Content-Type': 'application/json; charset: utf8',
        'Authorization': ACCESS_TOKEN
    }
    url = API_BASE_URL + '/v1.0/devices/' + DEVICE_ID + '/commands'
    body = {
        'command': command,
        'parameter': 'default',
        'commandType': 'command'
    }
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    res = urllib.request.urlopen(req)
    print(res)

# Lambda関数のメイン処理
def lambda_handler(event, context):
    # 照度データを取得
    lux = event['lux']
    print('Lux: ' + str(lux))

    # 照度に応じてカーテンの開閉を判断
    if lux >= LUX_THRESHOLD_ON:
        # カーテンを開く
        print('Turn on the curtain')
        control_curtain('turnOn')
    elif lux <= LUX_THRESHOLD_OFF:
        # カーテンを閉じる
        print('Turn off the curtain')
        control_curtain('turnOff')
    else:
        # カーテンをそのままにする
        print('Do nothing')
