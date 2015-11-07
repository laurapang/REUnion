import requests

# Obtain from making an account at http://bit.ly/nuance-yhack
appID = APPID

# Obtain from making an account at http://bit.ly/nuance-yhack
appKey = APPKEY

# Generate a random string and then set it to ID when using this for the first time
ID = random_string

TTSLang = "en_US"

requestURL = "https://tts.nuancemobility.net:443/NMDPTTSCmdServlet/tts?appId="+appID+"&appKey="+appKey+"&id="+ID+"&ttsLang="+TTSLang

text = "Hello, world!"

def postrequest(requestURL,text):
    headers = {"Content-Type": "text/plain", "Accept": "audio/x-wav"}
    req = requests.post(requestURL,data=text,headers=headers)
    return req.content

with open("audio.wav", 'wb') as output:
    output.write(postrequest(requestURL))
