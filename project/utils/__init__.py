import os, requests

from PIL import Image
from io import BytesIO
import concurrent.futures

def save_image_locally(url, path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(path)
            print(f"Downloaded image from {url} to {path}")
    except Exception as e:
        print(f"Error processing image from {url}: {e}")

def download_images(imageUrlDict, outputdir, max_workers=8):
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        futures = []
        for k, v in imageUrlDict.items():
            filepath = os.path.join(outputdir, k)
            os.makedirs(filepath, exist_ok=True)
            for url in v:
                filename = url.split('/')[-1]
                imgpath = os.path.join(filepath, filename)
                futures.append(executor.submit(save_image_locally, url, imgpath))
        
        for future in concurrent.futures.as_completed(futures):
            future.result()