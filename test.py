import requests

def download_md(url: str, save_path: str):
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"✅ 已保存到 {save_path}")
    else:
        print(f"❌ 下载失败，状态码：{resp.status_code}")

# 调用
download_md(
    url="https://docs.nexconn.ai/chatsdk-android.md",
    save_path="chatsdk-android.md"
)