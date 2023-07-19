from flask import Flask, render_template, request
import random, os, requests
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
# import urllib3

# urllib3.disable_warnings()

app = Flask(__name__)
load_dotenv()

STDICT_API_KEY = os.environ.get('STDICT_API_KEY')
# KRDICT_API_KEY = os.environ.get('KRDICT_API_KEY')

# def midReturn_all(val, s, e):
#     if s in val:
#         tmp = val.split(s)
#         val = []
#         for i in range(0, len(tmp)):
#             if e in tmp[i]: val.append(tmp[i][:tmp[i].find(e)])
#     else:
#         val = []
#     return val

def generate_word(starting_char):
    words = []
    # 한국어 기초사전 API 사용
    # url = '	https://krdict.korean.go.kr/api/search'

    # params = {
    #     'key': KRDICT_API_KEY,
    #     'part': 'word',
    #     'pos': 1,
    #     'q': starting_char
    # }
    # response = requests.get(url, params=params, verify=False)
    # words = midReturn_all(response.text,'<item>','</item>')

    # dict.txt에서 단어 추출
    with open("dict.txt", "r", encoding="utf-8") as file:
        for line in file:
            word = line.strip()
            if len(word) >= 2:
                words.append(word)
    
    # 한방 단어 제거하기
    # noNextSet = set()
    # for i in words:
    #     delList = list()
    #     for j in words[i]:
    #         if j[-1] not in words:
    #             delList.append(j) # 단어 j의 마지막 글자가 words에 없으면 한방 단어로 간주
    #     for j in delList:
    #         noNextSet.add(j)
    #         words[i].remove(j)

    candidates = [word for word in words if word.startswith(starting_char)]
     
    if candidates:
        return random.choice(candidates)
    else:
        return "일치하는 단어가 없습니다. 유저 승!"

# 단어 체크
def isCorrectWord(word):
    url = 'https://stdict.korean.go.kr/api/search.do'
    params = {
        'key': STDICT_API_KEY,
        'q': word,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_body = ET.fromstring(response.text)
        total_value = response_body.find('total').text
        return int(total_value)
    else:
        print('API 요청 실패')

# 전역변수
userInput = "" 
comOutput = ""

@app.route('/', methods=["GET", "POST"]) 
def index():
    form_data = request.form
    global userInput, comOutput

    if request.method == "POST":
        # 단어 입력하고 엔터치면 p태그에 입력한 단어 끝 글자로 시작하는 단어가 출력됨
        userInput = form_data["userInput"]
        print("user : {} com : {}".format(userInput, comOutput))
        if (len(userInput) < 2):
            if comOutput != "":
                return render_template("index.html", title="Home", result = "두 글자 이상 입력하세요.", last = comOutput[-1])
            else:
                return render_template("index.html", title="Home", result = "두 글자 이상 입력하세요.")
        elif (isCorrectWord(userInput) == 0): # 단어 아닌 문자 입력 처리
            if comOutput != "":
                return render_template("index.html", title="Home", result = "사전에 등록된 단어를 입력하세요!", last = comOutput[-1])
            else:
                return render_template("index.html", title="Home", result = "사전에 등록된 단어를 입력하세요!")   

        if comOutput != "":
            if comOutput[-1] == userInput[0]:
                print("일치")
                comOutput = generate_word(userInput[-1])
            else:
                return render_template("index.html", title="Home", result = "땡")
        elif comOutput == "":
            comOutput = generate_word(userInput[-1])

        return render_template("index.html", title="Home", result = comOutput, last = comOutput[-1])
    
    return render_template("index.html", title="Home")

if __name__ == '__main__':
    app.run(debug=True)