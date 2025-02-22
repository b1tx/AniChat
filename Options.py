from pywebio.input import *
import webbrowser

'''
input("This is a simple text input")
select("This is a drop down menu", ['Option1', 'Option2'])
checkbox("Multiple Choices!", options=["a",'b','c','d'])
radio("Select any one", options=['1', '2', '3'])
textarea('Text Area', rows=3, placeholder='Multiple line text input')
'''

input_output_language_id = -1
input_speaker_id = -1
input_prompt = ""

def options_choose():
    global input_output_language_id, input_speaker_id,input_prompt
    input_output_language = select("Please choose output language", ["Chinese", "Japanese"])
    if input_output_language == "Chinese":

        input_output_language_id = 0
        print("CH")

        input_speaker = select("请选择角色声音", ["绫地宁宁", "在原七海", "小茸", "唐乐吟"])
        if input_speaker == "绫地宁宁":
            input_speaker_id = 0
            input_prompt = "从现在开始请你扮演绫地宁宁,现在你是一个有着白色长发,紫色眼睛的16岁美少女,在说话时会使用可爱的语气.你喜欢图书馆,喜欢吃甜点,喜欢可爱的衣服.你对专业知识都很不了解,总是表现出恍惚的样子"
        elif input_speaker == "在原七海":
            input_speaker_id = 1
        elif input_speaker == "小茸":
            input_speaker_id = 2
        elif input_speaker == "唐乐吟":
            input_speaker_id = 3

        input_if_prompt = radio("是否自定义角色设定", ["是", "否"], value=["否"])
        if input_if_prompt == "是":
            input_prompt = textarea("请输入角色设定", row=4, placeholder='Multiple line text input')

    elif input_output_language == "Japanese":

        input_output_language_id = 1
        print("JP")

        input_speaker = select("キャラクターボイスを選択してください",
                               ["綾地寧々", "因幡めぐる", "朝武芳乃", "常陸茉子", "ムラサメ", "鞍馬小春", "在原七海"])
        if input_speaker == "綾地寧々":
            input_speaker_id = 0
            input_prompt = "从现在开始请你扮演绫地宁宁,现在你是一个有着白色长发,紫色眼睛的16岁美少女,在说话时会使用可爱的语气.你喜欢图书馆,喜欢吃甜点,喜欢可爱的衣服.你对专业知识都很不了解,总是表现出恍惚的样子"
        elif input_speaker == "因幡めぐる":
            input_speaker_id = 1
        elif input_speaker == "朝武芳乃":
            input_speaker_id = 2
        elif input_speaker == "常陸茉子":
            input_speaker_id = 3
        elif input_speaker == "ムラサメ":
            input_speaker_id = 4
        elif input_speaker == "鞍馬小春":
            input_speaker_id = 5
        elif input_speaker == "在原七海":
            input_speaker_id = 6

        input_if_prompt = radio("役割設定をカスタマイズするかどうか", ["はい", "ネゲート"], value=["ネゲート"])
        if input_if_prompt == "はい":
            input_prompt = textarea("文字セットを入力してください", row=4, placeholder='Multiple line text input')

if __name__ == "__main__":
    options_choose()