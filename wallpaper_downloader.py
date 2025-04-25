import requests
import os

UNSPLASH_ACCESS_KEY = "mQzVdzjrx1igEYWXiC8ykySzdNjvKtaY-2nSg5y_DcQ"  # 🔥 Paste your API key here

wallpaper_folder = "wallpapers"
os.makedirs(wallpaper_folder, exist_ok=True)

def download_wallpaper():
    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": "nature",  # You can change this to "mountains", "motivation", etc.
        "orientation": "landscape",
        "count": 50  # Download one image per run
    }
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        for idx, img in enumerate(data if isinstance(data, list) else [data]):
            img_url = img['urls']['full']
            img_data = requests.get(img_url).content
            img_name = f"wallpaper_{img['id']}.jpg"
            with open(os.path.join(wallpaper_folder, img_name), 'wb') as f:
                f.write(img_data)
            print(f"✅ Downloaded: {img_name}")
    else:
        print("❌ Failed to fetch wallpaper from Unsplash:", response.text)

# Run the download function
download_wallpaper()
