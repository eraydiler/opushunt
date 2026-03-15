import requests

def test_remoteok_tags():
    tags_to_test = [
        "ios", 
        "ios, swift", 
        "ios,swift",
        "ios, xcode, figma, swift, swiftui"
    ]
    
    headers = {"User-Agent": "JobSearchAutomation/1.0"}
    
    for tag in tags_to_test:
        print(f"Testing tag: '{tag}'")
        url = f"https://remoteok.com/api?tag={tag}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = len(data) - 1 if len(data) > 0 else 0
                print(f"  -> Found {count} jobs.")
            else:
                print(f"  -> Failed with status {response.status_code}")
        except Exception as e:
            print(f"  -> Error: {e}")
        print("-" * 20)

if __name__ == "__main__":
    test_remoteok_tags()
