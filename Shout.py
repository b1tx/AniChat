import argparse
from scipy.io.wavfile import write
from mel_processing import spectrogram_torch
from text import text_to_sequence, _clean_text
from models import SynthesizerTrn
import utils
import commons
import sys
import re
import queue
from torch import no_grad, LongTensor
import logging
import sounddevice as sd
from winsound import PlaySound
from vosk import Model, KaldiRecognizer
import requests
import time
from pathlib import Path
import webbrowser

q = queue.Queue()


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)
try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info["default_samplerate"])

    if args.model is None:
        model = Model(lang="cn")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None



except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)


from pyChatGPT import ChatGPT
import json


def voice_input():
    print("正在录音...")
    with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,
                           dtype="int16", channels=1, callback=callback):

        rec = KaldiRecognizer(model, args.samplerate)
        # flag = 'y'
        while True:  # flag.lower() == 'y':
            data = q.get()
            if rec.AcceptWaveform(data):
                print("录音结束.")
                a = json.loads(rec.Result())
                a = str(a['text'])
                a = ''.join(a.split())
                if (len(a) > 0):
                    print(a)
                    user_input = a
                    return user_input
            if dump_fn is not None:
                dump_fn.write(data)
            # flag = input('Continue?(y/n):')

def openbrowser(text):
    maps = {
        '百度': ['百度', 'baidu'],
        '腾讯': ['腾讯', 'tengxun'],
        '网易': ['网易', 'wangyi']

    }
    for word in maps['百度']:
        if word in text:
            webbrowser.open_new_tab('https://www.baidu.com')
            return
    for word in maps['腾讯']:
        if word in text:
            webbrowser.open_new_tab('https://www.qq.com')
            return
    for word in maps['网易']:
        if word in text:
            webbrowser.open_new_tab('https://www.163.com')
            return

    '''
    if text in maps['百度']:
        webbrowser.open_new_tab('https://www.baidu.com')
    elif text in maps['腾讯']:
        webbrowser.open_new_tab('https://www.qq.com')
    elif text in maps['网易']:
        webbrowser.open_new_tab('https://www.163.com/')
    else:
        webbrowser.open_new_tab('https://www.baidu.com/s?wd=%s' % text)
    '''

def playShout():
    question = voice_input()
    # print("333333333")
    openbrowser(question)
    # print("444444444")
    return question


if __name__ == "__main__":
    question = voice_input()
    # print(question)
    openbrowser(question)