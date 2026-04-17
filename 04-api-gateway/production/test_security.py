import requests

BASE_URL = "http://localhost:8000"

def test_api_key():
    print("Testing /ask without JWT token...")
    # Without key
    r = requests.post(f"{BASE_URL}/ask", json={"question": "test"})
    assert r.status_code == 401, f"Should reject without token. Got {r.status_code}"
    print("✅ Rejected without key correctly.")

    print("Fetching JWT Token to use API...")
    # VÌ app production sử dụng JWT, ta phải login trước
    auth = requests.post(f"{BASE_URL}/auth/token", json={"username": "student", "password": "demo123"})
    token = auth.json().get("access_token")

    print(f"Testing /ask with valid JWT token...")
    # Với key hợp lệ truyền qua Bearer
    r = requests.post(
        f"{BASE_URL}/ask",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "test"}
    )
    assert r.status_code == 200, f"Should accept with valid token. Got {r.status_code}. Response: {r.text}"
    print("✅ Accepted with valid token correctly.")
    return token

def test_rate_limit(token):
    print("Running 20 requests to test rate limit...")
    status_429_caught = False
    # Send 20 requests
    for i in range(20):
        r = requests.post(
            f"{BASE_URL}/ask",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": f"test {i}"}
        )
        if r.status_code == 429:
            status_429_caught = True
            print(f"Request {i+1} got 429 Too Many Requests as expected!")
            break
            
    assert status_429_caught, "Should rate limit after threshold, but it didn't!"
    print("✅ Rate limit works.")

if __name__ == "__main__":
    try:
        token = test_api_key()
        test_rate_limit(token)
        print("✅ All tests passed successfully!")
    except AssertionError as e:
        print("❌ TEST FAILED:", str(e))
