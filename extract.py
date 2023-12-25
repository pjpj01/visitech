api_url = 'https://dv5oxyuvj6.apigw.ntruss.com/custom/v1/26491/0bbfc9297d3aefffddf486485710617533b8e87dfd8fd1d3633d3cbe096708df/general'
secret_key = 'SVJMRFJ6dmFnSFlWblZhcWZJdWZ0RUVMWEhoanVNd3I='
OPENAI_API_KEY = "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"

import numpy as np
import platform
from PIL import ImageFont, ImageDraw, Image
from matplotlib import pyplot as plt
 
import uuid
import json
import time
import cv2
import requests
import openai

def plt_imshow(title='image', img=None, figsize=(8 ,5)):
    plt.figure(figsize=figsize)
 
    if type(img) == list:
        if type(title) == list:
            titles = title
        else:
            titles = []
 
            for i in range(len(img)):
                titles.append(title)
 
        for i in range(len(img)):
            if len(img[i].shape) <= 2:
                rgbImg = cv2.cvtColor(img[i], cv2.COLOR_GRAY2RGB)
            else:
                rgbImg = cv2.cvtColor(img[i], cv2.COLOR_BGR2RGB)
 
            plt.subplot(1, len(img), i + 1), plt.imshow(rgbImg)
            plt.title(titles[i])
            plt.xticks([]), plt.yticks([])
 
        plt.show()
    else:
        if len(img.shape) < 3:
            rgbImg = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            rgbImg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
 
        plt.imshow(rgbImg)
        plt.title(title)
        plt.xticks([]), plt.yticks([])
        plt.show()

def put_text(image, text, x, y, color=(0, 255, 0), font_size=22):
    if type(image) == np.ndarray:
        color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(color_coverted)
 
    if platform.system() == 'Darwin':
        font = 'AppleGothic.ttf'
    elif platform.system() == 'Windows':
        font = 'malgun.ttf'
        
    image_font = ImageFont.truetype(font, font_size)
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
 
    draw.text((x, y), text, font=image_font, fill=color)
    
    numpy_image = np.array(image)
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
 
    return opencv_image


path = './image/testPill1.jpg'
files = [('file', open(path,'rb'))]

request_json = {'images': [{'format': 'jpg',
                                'name': 'demo'
                               }],
                    'requestId': str(uuid.uuid4()),
                    'version': 'V2',
                    'timestamp': int(round(time.time() * 1000))
                   }
 
payload = {'message': json.dumps(request_json).encode('UTF-8')}
 
headers = {
  'X-OCR-SECRET': secret_key,
}
 
response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
result = response.json()

infer_texts = [field['inferText'] for field in result['images'][0]['fields']]
result_string = ' '.join(infer_texts)
result_prompt="1. 당신은 약사입니다. 아래 주어진 <정보>를 정리해서 <출력> 형식에 맞게 알려주세요\n2. 정보가 제공되지 않은 경우에는 공백으로 비워두세요.\n3. 약품 이름이 정확하지 않을 수 있으니 실제로 존재하는 약품 이름으로 작성하세요.\n4. 당신이 가진 의학적 정보를 바탕으로 설명해주세요\n<정보> : \n"+result_string+"<출력>\n환자 이름 :\n유통기한 :\n약품 이름:\n1회 투약량:\n일 투여 횟수:\n총 투약 일수 :\n무엇을 위한 치료제인지 :\n주의사항 :"

openai.api_key = OPENAI_API_KEY
model = "gpt-3.5-turbo"

messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": result_prompt}
]

response = openai.ChatCompletion.create(
    model=model,
    messages=messages
)
answer = response['choices'][0]['message']['content']

lines = answer.split('\n')

result_dict = {}

for line in lines:
    if ':' in line:
        key, value = map(str.strip, line.split(':', 1))
        result_dict[key] = value

json_filename = "patient_info.json"
with open(json_filename, 'w', encoding='utf-8') as json_file:
    json.dump(result_dict, json_file, ensure_ascii=False, indent=4)

print(f"JSON 파일이 저장되었습니다.")
