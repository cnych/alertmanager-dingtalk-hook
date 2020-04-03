import os
import json
import logging
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
from urllib.parse import urlparse

from flask import Flask
from flask import request

app = Flask(__name__)

logging.basicConfig(
    level=logging.DEBUG if os.getenv('LOG_LEVEL') == 'debug' else logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')


@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data = request.get_data()
        app.logger.debug(post_data)
        send_alert(json.loads(post_data))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def send_alert(data):
    token = os.getenv('ROBOT_TOKEN')
    secret = os.getenv('ROBOT_SECRET')
    if not token:
        app.logger.error('you must set ROBOT_TOKEN env')
        return
    if not secret:
        app.logger.error('you must set ROBOT_SECRET env')
        return
    timestamp = int(round(time.time() * 1000))
    url = 'https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%d&sign=%s' % (token, timestamp, make_sign(timestamp, secret))

    status = data['status']
    alerts = data['alerts']
    alert_name = alerts[0]['labels']['alertname']

    def _mark_item(alert):
        labels = alert['labels']
        annotations = "> "
        for k, v in alert['annotations'].items():
            annotations += "{0}: {1}\n".format(k, v)
        if 'job' in labels:
            mark_item = "\n> job: " + labels['job'] + '\n\n' + annotations + '\n'
        else:
            mark_item = annotations + '\n'
        return mark_item

    if status == 'resolved':  # 告警恢复
        send_data = {
            "msgtype": "text",
            "text": {
                "content": "报警 %s 已恢复" % alert_name
            }
        }
    else:
        title = '%s 有 %d 条新的报警' % (alert_name, len(alerts))
        external_url = alerts[0]['generatorURL']
        prometheus_url = os.getenv('PROME_URL')
        if prometheus_url:
            res = urlparse(external_url)
            external_url = external_url.replace(res.netloc, prometheus_url)
        send_data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": title + "\n" + "![](https://bxdc-static.oss-cn-beijing.aliyuncs.com/images/prometheus-recording-rules.png)\n" + _mark_item(alerts[0]) + "\n" + "[点击查看完整信息](" + external_url + ")\n"
            }
        }

    req = requests.post(url, json=send_data)
    result = req.json()
    if result['errcode'] != 0:
        app.logger.error('notify dingtalk error: %s' % result['errcode'])


def make_sign(timestamp, secret):
    """新版钉钉更新了安全策略，这里我们采用签名的方式进行安全认证
    https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq
    """
    secret_enc = bytes(secret, 'utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = bytes(string_to_sign, 'utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
