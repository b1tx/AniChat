import webbrowser

from scipy.io.wavfile import write
from mel_processing import spectrogram_torch
from text import text_to_sequence, _clean_text
from models import SynthesizerTrn
import utils
import commons
import sys
import re
import Shout
from torch import no_grad, LongTensor
import logging
from winsound import PlaySound
from openai import OpenAI
import tkinter as tk
from tkinter import simpledialog
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file, abort, make_response
from flask_cors import CORS, cross_origin
from pyutils.live2d_control import tts_and_play_audio
import threading
import os
import subprocess
from werkzeug.utils import secure_filename

import LoginRegister
import Options


chinese_model_path = ".\model\default\model.pth"
chinese_config_path = ".\model\default\config.json"
japanese_model_path = ".\model\model.pth"
japanese_config_path = ".\model\config.json"

####################################
#CHATGPT INITIALIZE
from pyChatGPT import ChatGPT
import json

modelmessage = """ID      Output Language
0       Chinese
1       Japanese
"""

idmessage_cn = """ID      Speaker
0       綾地寧々
1       在原七海
2       小茸
3       唐乐吟
"""

idmessage_jp = """ID      Speaker
0       綾地寧々
1       因幡めぐる
2       朝武芳乃
3       常陸茉子
4       ムラサメ
5       鞍馬小春
6       在原七海
"""

session = [
    {
        "role": "system",
        "content": """从现在开始请你扮演绫地宁宁,现在你是一个有着白色长发,紫色眼睛的16岁美少女,在说话时会使用可爱的语气.你喜欢图书馆,喜欢吃甜点,喜欢可爱的衣服.你对专业知识都很不了解,总是表现出恍惚的样子""",
    }
]

def get_input():
    # prompt for input
    print("You:")
    user_input = input()
    return user_input

def get_input_jp():
    # prompt for input
    print("You:")
    usr_in = input()
    if usr_in == 'quit()':
        return usr_in
    else:
        user_input = usr_in +" 使用日本语回答"
    return user_input



logging.getLogger('numba').setLevel(logging.WARNING)


# 注释掉了控制台信息
log = logging.getLogger('werkzeug')
log.disabled = True


def ex_print(text, escape=False):
    if escape:
        print(text.encode('unicode_escape').decode())
    else:
        print(text)


def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


def ask_if_continue():
    while True:
        answer = input('Continue? (y/n): ')
        if answer == 'y':
            break
        elif answer == 'n':
            sys.exit(0)


def print_speakers(speakers, escape=False):
    if len(speakers) > 100:
        return
    print('ID\tSpeaker')
    for id, name in enumerate(speakers):
        ex_print(str(id) + '\t' + name, escape)


def get_speaker_id(message):
    speaker_id = input(message)
    if speaker_id == '':
        print(str(speaker_id) + ' is not a valid ID!')
        sys.exit(1)
    else:
        try:
            speaker_id = int(speaker_id)
        except:
            print(str(speaker_id) + ' is not a valid ID!')
            sys.exit(1)
    return speaker_id

def get_model_id(message):
    model_id = input(message)
    if model_id == '':
        print(str(model_id) + ' is not a valid ID!')
        sys.exit(1)
    else:
        try:
            model_id = int(model_id)
        except:
            print(str(model_id) + ' is not a valid ID!')
            sys.exit(1)
    return model_id

def get_label_value(text, label, default, warning_name='value'):
    value = re.search(rf'\[{label}=(.+?)\]', text)
    if value:
        try:
            text = re.sub(rf'\[{label}=(.+?)\]', '', text, 1)
            value = float(value.group(1))
        except:
            print(f'Invalid {warning_name}!')
            sys.exit(1)
    else:
        value = default
    return value, text


def get_label(text, label):
    if f'[{label}]' in text:
        return True, text.replace(f'[{label}]', '')
    else:
        return False, text

def get_response(input):
    session.append({"role": "user", "content": input})
    # Call the OpenAI API with the prompt
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",  # Adjust based on available engine versions
      messages=session,
      temperature=1
    )
    # Extract and return the text from the API response
    msg = response.choices[0].message.content
    session.append({"role": "assistant", "content": msg})
    return msg


def generateSound(inputString, id, model_id):
    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    #model = input('0: Chinese')
    #config = input('Path of a config file: ')
    if model_id == 0:
        model = chinese_model_path
        config = chinese_config_path
    elif model_id == 1:
        model = japanese_model_path
        config = japanese_config_path
        

    hps_ms = utils.get_hparams_from_file(config)
    n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False

    net_g_ms = SynthesizerTrn(
        n_symbols,
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=n_speakers,
        emotion_embedding=emotion_embedding,
        **hps_ms.model)
    _ = net_g_ms.eval()
    utils.load_checkpoint(model, net_g_ms)

    if n_symbols != 0:
        if not emotion_embedding:
            #while True:
            if(1 == 1):
                choice = 't'
                if choice == 't':
                    text = inputString
                    if text == '[ADVANCED]':
                        text = "我不会说"
                    length_scale, text = get_label_value(
                        text, 'LENGTH', 1, 'length scale')
                    noise_scale, text = get_label_value(
                        text, 'NOISE', 0.667, 'noise scale')
                    noise_scale_w, text = get_label_value(
                        text, 'NOISEW', 0.8, 'deviation of noise')
                    cleaned, text = get_label(text, 'CLEANED')

                    stn_tst = get_text(text, hps_ms, cleaned=cleaned)
                    speaker_id = id 
                    out_path = "output.wav"
                    with no_grad():
                        x_tst = stn_tst.unsqueeze(0)
                        x_tst_lengths = LongTensor([stn_tst.size(0)])
                        sid = LongTensor([speaker_id])
                        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
                write(out_path, hps_ms.data.sampling_rate, audio)

app = Flask(__name__)
CORS(app)

if __name__ == "__main__":

    loginapp = LoginRegister.LoginApp()
    loginapp.run()

    


    client = OpenAI(api_key="sk-iOnpyBF1S3AlZ3Yf60D0945193Ea4d129a1e29E48f32877e", base_url="https://api.bianxie.ai/v1")
    '''
    model_id = -1
    while True:
        print(modelmessage)
        model_id = int(get_model_id('选择回复语言: '))
        if model_id == 0 or model_id == 1:
            if model_id == 1:
                session.append({"role": "system", "content": "用日本语回答"})
            break
        else:
            print(str(model_id) + ' is not a valid ID!\n')
    print()
    
    speaker_id = -1
    while True:
        if model_id == 0:
            print("\n" + idmessage_cn)
        elif model_id == 1:
            print("\n" + idmessage_jp)
        
        speaker_id = get_speaker_id('选择角色: ')
        if (model_id == 0 and speaker_id in list(range(4))) or (model_id == 1 and speaker_id in list(range(7))):
            break
        else:
            print(str(speaker_id) + ' is not a valid ID!\n')
    print()
    '''
    Options.options_choose()

    model_id = Options.input_output_language_id
    print(model_id)
    if model_id == 1:
        session.append({"role": "system", "content": "用日本语回答"})
    speaker_id = Options.input_speaker_id
    print(speaker_id)
    prompt = Options.input_prompt
    print(prompt)

    session = [
        {
            "role": "system",
            "content": prompt
        }
    ]


    webbrowser.open("http://127.0.0.1:5000", new=0)

    # while True:
    #     if model_id == 0:
    #         usr_in = get_input()

    #         if(usr_in == "quit()"):
    #             break
    #         resp = get_response(usr_in)
    #         print("ChatGPT:")
    #         answer = resp.replace('\n','')
    #         generateSound("[ZH]"+answer+"[ZH]", speaker_id, model_id)
    #         print(answer)
    #         PlaySound(r'./output.wav', flags=1)
    #     elif model_id == 1:
    #         usr_in = get_input_jp()
    #         if(usr_in == "quit()"):
    #             break
    #         resp = get_response(usr_in)
    #         print("ChatGPT:")
    #         answer = resp.replace('\n','')
    #         generateSound(answer, speaker_id, model_id)
    #         print(answer)
    #         PlaySound(r'./output.wav', flags=1)

with open('./local/now.txt', 'r') as f:
    line = f.readline().strip()
    if line:
        usr_name, usr_pwd = line.split(":")

@app.route('/send_message', methods=['POST'])
def send_message():
    input_text = request.json['input']
    if input_text == "quit()":
        return jsonify({"response": "退出程序"})
    # if model_id == 1:
    #     input_text += """(用日本语回答)"""
    if model_id == 0:
        response = get_response(input_text)
    else:
        response = get_response(input_text+"""(用日本语回答)""")
    answer = response.replace('\n', '')
    file_path = f'./static/{usr_name}/history.txt'
    print(file_path)
    # 确保目录存在，如果不存在则创建
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # 将answer写入文件
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(usr_name+': '+input_text+'\n')
        file.write('GPT: '+answer + '\n')  # 在答案后添加换行符以便区分不同的记录
    if model_id == 0:
        generateSound("[ZH]" + answer + "[ZH]", speaker_id, model_id)
    else:
        generateSound(answer, speaker_id, model_id)
    threading.Thread(target=tts_and_play_audio).start()
    return jsonify({"response": answer})

@app.route('/shout', methods=['POST'])
def call_shout():
    response = Shout.playShout()
    return jsonify({"response": response})

@app.route('/assets/<path:path>')
def serve_static(path):
    return send_from_directory('./templates/assets', path)

@app.route('/api/get_mouth_y')
def api_get_one_account():
    with open("tmp.txt", "r") as f:
        return json.dumps({
            "y": f.read()
        })

@app.route('/api/get_user_avatar_path', methods=['GET'])
def get_user_avatar_path():
    with open('./local/now.txt', 'r') as f:
        line = f.readline().strip()
        if line:
            usr_name, usr_pwd = line.split(":")
    print(usr_name)
    return jsonify({'user_avatar_path': usr_name})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '没有文件部分', 400
    file = request.files['file']
    print(file.filename)
    if file.filename == '':
        return '没有选择文件', 400
    if file:
        file_path = './static/' + usr_name + '/' + 'user_avatar.jpg'
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(file_path)
        print(file_path)
        return '文件已上传', 200
    
@app.route('/history_open', methods=['POST'])
def open_history():
    data = request.json
    filename = data.get('filename')
    print(filename)

    # 确保文件路径是安全的
    if os.path.exists(filename):
        try:
            print
            os.startfile(filename)  # 仅适用于 Windows
            return jsonify({"status": "success"}), 200
        except Exception as e:
            print(f"Error opening file: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        print(65)
        return jsonify({"status": "error", "message": "文件不存在"}), 404

@app.route('/')
def index():
    return render_template('index.html')

app.run(debug=False)
