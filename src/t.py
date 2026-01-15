import requests

if __name__ == "__main__":
    _url = "https://moes.lnaspiring.com/Moe233-Subs/qwbm/api/v1/client/subscribe?token=4848bcb141f58288d5e0e53ed15c5da1"
    headers = {
        "User-Agent": "mihomo",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    res = requests.get(_url, headers=headers)
    print(res.text)
