import requests
import os
import hashlib
import json
from urllib.parse import urlparse

HASH_FILE = "downloaded_hashes.json"

def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_hashes(hashes):
    with open(HASH_FILE, "w") as f:
        json.dump(list(hashes), f)

def download_images(urls):
    os.makedirs("Fetched_Images", exist_ok=True)
    downloaded_hashes = load_hashes()

    for url in urls:
        try:
            print(f"\n🔗 Processing: {url}")
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            # --- Precaution: Check headers ---
            content_type = response.headers.get("Content-Type", "")
            content_length = response.headers.get("Content-Length")

            if "image" not in content_type.lower():
                print("Skipping (Not an image)")
                continue

            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10 MB limit
                print("Skipping (File too large)")
                continue

            # --- Prevent duplicate downloads ---
            file_bytes = response.content
            file_hash = hashlib.md5(file_bytes).hexdigest()
            if file_hash in downloaded_hashes:
                print("Skipping (Duplicate image)")
                continue
            downloaded_hashes.add(file_hash)

            # --- Extract filename from URL ---
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = f"image_{len(downloaded_hashes)}.jpg"

            filepath = os.path.join("Fetched_Images", filename)

            with open(filepath, "wb") as f:
                f.write(file_bytes)

            print(f"Image saved at  {filename} at {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    # Save updated hashes after all downloads
    save_hashes(downloaded_hashes)

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")

    # --- Multiple URLs input ---
    user_input = input("Enter image URLs (comma-separated): ")
    urls = [url.strip() for url in user_input.split(",") if url.strip()]

    if not urls:
        print("✗ No URLs provided.")
        return

    download_images(urls)
    print("\nConnection strengthened. Community enriched.")

if __name__ == "__main__":
    main()

