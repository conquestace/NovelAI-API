import aiohttp
import asyncio
import zipfile
import time
import random
from pathlib import Path

class NovelAIError(Exception):
    def __init__(self, status_code, message="NovelAI Error"):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class NovelAI:
    BASE_ADDRESS = 'https://api.novelai.net'
    TIMEOUT = 100

    @classmethod
    async def getToken(cls):
        # Implement your token retrieval logic here
        key = open('key').read()
        return key  # For simplicity, returning the token directly


    @classmethod
    async def generateImage(cls, input, width, height):
        token = await cls.getToken()
        base = "best quality, amazing quality, very aesthetic, absurdres"
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            url = cls.BASE_ADDRESS + "/ai/generate-image"
            payload = {
                "input": input + base,
                "model": "nai-diffusion-3",
                "parameters": {
    "legacy": False,
    "quality_toggle": False,
    "width": width,
    "height": height,
    "scale": 8,
    "sampler": "k_euler",
    "steps": 28,
    "n_samples": 1,
    "reference_strength": 0.0,
    "noise": 0,
    "uc_preset": 1,
    "controlnet_strength": 1,
    "dynamic_thresholding": False, 
    "dynamic_thresholding_percentile": 0.999, 
    "dynamic_thresholding_mimic_scale": 10.0, 
    "sm": True, 
    "sm_dyn": False, 
    "skip_cfg_below_sigma": 0.0,
    "uncond_scale": 1,
    "cfg_rescale": 0,
    "noise_schedule": "native",
    "seed": 0,
    "negative_prompt": "lowres, {bad}, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract]"
}
                
            }
            async with session.post(url, headers=headers, json=payload, timeout=cls.TIMEOUT) as response:
                if response.status == 200:
                    data = await response.read()
                    return data
                else:
                    error = await response.json()
                    raise NovelAIError(response.status, error.get("message", "Unknown error!"))

async def main():

    def randomLine():
        afile = open('prompts.txt')
        line = next(afile)
        for num, aline in enumerate(afile, 2):
            if random.randrange(num):
                continue
            line = str(aline)
        return line

    def reso():
        pairs = [(384, 640), (640, 384), (512, 512), (512, 768), (768, 512), (640, 640), (512, 1024), (1024, 512), (1024,1024), (832, 1216), (1216,832), (768, 384), (1024, 384), (1216, 384)]
        width, height = random.choice(pairs)
        return width, height
    
    line=randomLine()
    width, height=reso()
    image_data = await NovelAI.generateImage(line, width, height)

    # Save the ZIP file
    zip_path = Path("results/image.zip")
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    zip_path.write_bytes(image_data)

    # Extract the contents of the ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        extracted_images = zip_ref.namelist()
        for image_file in extracted_images:
            # Ensure unique filename
            i = 0
            new_image_path = zip_path.parent / "image.png"
            while new_image_path.exists():
                i += 1
                new_image_path = zip_path.parent / f"image_{i}.png"
            zip_ref.extract(image_file, path=zip_path.parent)
            (zip_path.parent / image_file).rename(new_image_path)

    # Delete the original ZIP file
    zip_path.unlink()
    
    
    

# Run the asyncio event loop

for i in range(4):
    asyncio.run(main())
    time.sleep(10)
