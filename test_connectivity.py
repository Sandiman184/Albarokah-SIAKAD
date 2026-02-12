import urllib.request
import urllib.error

def check_url(url, name):
    try:
        response = urllib.request.urlopen(url)
        print(f"[{name}] Status: {response.getcode()}")
        if response.getcode() == 200:
            print(f"[{name}] OK")
        else:
            print(f"[{name}] Failed")
    except urllib.error.HTTPError as e:
        print(f"[{name}] HTTP Error: {e.code}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

if __name__ == "__main__":
    print("Testing SIAKAD (Internal)...")
    check_url("http://127.0.0.1:5000/auth/login", "SIAKAD Login")
    
    print("\nTesting Web Profile (Public)...")
    check_url("http://127.0.0.1:8001/", "Web Profile Home")
    check_url("http://127.0.0.1:8001/berita", "Web Profile Berita")
    
    print("\nTesting Dynamic Route...")
    # Assuming seed data created 'penerimaan-santri-baru-2026'
    slug = "penerimaan-santri-baru-2026"
    check_url(f"http://127.0.0.1:8001/berita/{slug}", "Web Profile Berita Detail")
