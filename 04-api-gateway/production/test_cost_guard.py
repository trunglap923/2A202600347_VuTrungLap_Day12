import requests

BASE_URL = "http://localhost:8000"

def test_cost_limit():
    # 1. Lấy token
    print("Đang lấy token...")
    auth = requests.post(f"{BASE_URL}/auth/token", json={"username": "student", "password": "demo123"})
    token = auth.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Gửi request liên tục cho đến khi hết tiền
    print("Đang gửi requests để 'đốt' budget...")
    for i in range(10):
        r = requests.post(f"{BASE_URL}/ask", headers=headers, json={"question": f"Câu hỏi thứ {i}"})
        if r.status_code == 402:
            print(f"✅ Thử nghiệm thành công! Request thứ {i+1} đã bị chặn.")
            print("Response:", r.json())
            return
        elif r.status_code == 200:
            print(f"Request {i+1}: OK (Vẫn còn tiền)")
        else:
            print(f"Lỗi không xác định: {r.status_code}")
            print(r.text)
            break

if __name__ == "__main__":
    test_cost_limit()
