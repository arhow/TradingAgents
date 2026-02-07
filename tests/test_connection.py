import praw
import base64, requests
# reddit = praw.Reddit(
#     client_id="FFTtkIQGxr5G6H8XZ4jzCQ",
#     client_secret="gWcJBkZGgVEaniAQbGVEzO17rP3Jtw",
#     user_agent="testapp:v1.0 (by /u/AdPrimary9539)",
#     username="AdPrimary9539",
#     password="Lemon1619",
# )
#
# # reddit.read_only = True
# print("Scopes:", reddit.user.me())


CLIENT_ID = "ppI5ZarRxoSV3Xw1q-McuA"
CLIENT_SECRET = "NLclXHZeMfTQoLtihrSYTnIW9eg6rQ"
USERNAME = "AdPrimary9539"           # ← u/ は付けない
PASSWORD = "Lemon1619"

basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
headers = {
    "Authorization": f"Basic {basic}",
    "User-Agent": "testapp:v1.0 (by /u/AdPrimary9539)",
    # 2FAが有効なら次の行のコメントを外して6桁コードを入れる
    # "X-Reddit-OTP": "123456",
}
data = {
    "grant_type": "password",
    "username": USERNAME,
    "password": PASSWORD,
}

r = requests.post("https://www.reddit.com/api/v1/access_token",
                  headers=headers, data=data, timeout=20)

print(r.status_code)
print(r.text)
