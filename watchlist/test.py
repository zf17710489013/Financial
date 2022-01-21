from curl2py.curlParseTool import curlCmdGenPyScript

# curl_cmd = """curl 'https://loonflow.readthedocs.io/zh_CN/r2.0.6/manage/user&permission/' \
#   -H 'authority: loonflow.readthedocs.io' \
#   -H 'pragma: no-cache' \
#   -H 'cache-control: no-cache' \
#   -H 'sec-ch-ua: "Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "macOS"' \
#   -H 'upgrade-insecure-requests: 1' \
#   -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36' \
#   -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
#   -H 'sec-fetch-site: same-origin' \
#   -H 'sec-fetch-mode: navigate' \
#   -H 'sec-fetch-user: ?1' \
#   -H 'sec-fetch-dest: document' \
#   -H 'referer: https://loonflow.readthedocs.io/zh_CN/r2.0.6/manage/workflow_config/' \
#   -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
#   -H 'cookie: _ga=GA1.3.528420077.1629699508' \
#   --compressed"""
# output = curlCmdGenPyScript(curl_cmd)
# print(output)


import requests
import json

headers = {
    "authority": "loonflow.readthedocs.io",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua": "\"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://loonflow.readthedocs.io/zh_CN/r2.0.6/manage/workflow_config/",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8"
}
cookies = {
    "_ga": "GA1.3.528420077.1629699508"
}


res = requests.get(
    "https://loonflow.readthedocs.io/zh_CN/r2.0.6/manage/user&permission/",
    headers=headers,
    cookies=cookies
)
print(res.content)

