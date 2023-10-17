import openai
import json
import re
import time
import tkinter as tk
from tkinter import END
import tkinter.messagebox as messageBox
import tkinter.colorchooser as colorChooser

# 全局变量
t = ["3.0"]
message = []
jsonDict = {
    "isFirst": False,
    "colorConfig": "#fb7299",
    "Key": "",
    "Ser": "",
    "model": "gpt-3.5-turbo"
}


def noStream(ss, mod):  # 非流式应答，实测速度慢，故舍弃
    try:
        completion = openai.ChatCompletion.create(model=mod, messages=ss)
        return True, completion.choices[0].message.content
    except Exception as error:
        return False, str(error)


def gpt_35_api_stream(messages: list, mod):  # 流式应答函数，根据是否成功返回布尔值
    """

    :param messages: 聊天内容列表(list)
    :param mod: 模型参数(str)
    :return: True/False(bool)
    """
    # return noStream(messages, mod)

    try:
        response = openai.ChatCompletion.create(
            model=mod,
            messages=messages,
            stream=True,
        )
        completion = {'role': '', 'content': ''}
        for event in response:
            if event['choices'][0]['finish_reason'] == 'stop':
                print(f'收到的完成数据: {completion}')
                break
            for delta_k, delta_v in event['choices'][0]['delta'].items():
                completion[delta_k] += delta_v
            print(completion["content"])
        return True, completion["content"]
    except Exception as err:
        return False, str(err)


def delete():  # 实时检查输入框，防止用户删除“请输入:”，消除因快捷键产生的换行
    textn = textLittle.get(1.0, END)
    if (textn[0:6] == "请输入:\n\n") or textn[0:4] != "请输入:":
        textLittle.delete(1.0, END)
        textLittle.insert(END, "请输入:")
    else:
        rootWindows.after(100, delete)


def reset():  # 重置按钮函数

    def exitReset():
        showReset.destroy()

    message.clear()
    textBig.config(state="normal")
    textBig.delete("3.0", "end")
    textBig.insert("end", "\n")
    textBig.config(state="disabled")
    showReset = tk.Toplevel()
    showReset.title("提示")
    showReset.geometry("500x280+500+250")
    showReset.resizable(0, 0)
    lreset = tk.Label(showReset, text="对话已重置", font=("华文行楷", 25), foreground="green")
    lreset.place(anchor="center", width=350, height=50, x=250, y=110)

    b1reset = tk.Button(showReset, text="取消", command=exitReset, relief="flat", bg="#e0e0e0")
    b1reset.place(anchor="center", width=76, height=38, x=115, y=220)

    b11reset = tk.Button(showReset, text="确定", command=exitReset, relief="flat", bg="#e0e0e0")
    b11reset.place(anchor="center", width=76, height=38, x=385, y=220)
    showReset.mainloop()


def save():  # 保存对话记录函数，一次执行中将记录上次保存的位置并在下次保存时从该位置开始保存

    def exitSave():
        showSave.destroy()

    textSave = textBig.get(t[0], END)
    textFile = open("历史对话记录.txt", "a", encoding="utf-8")
    textFile.write(textSave)
    textFile.close()
    tt = textBig.index("end")
    ffind = tt.index(".")
    t[0] = str(int(tt[:ffind]) - 1) + tt[ffind:]
    showSave = tk.Toplevel()
    showSave.title("提示")
    showSave.geometry("500x280+500+250")
    showSave.resizable(0, 0)
    lsave = tk.Label(showSave, text="已保存至程序所在目录", font=("华文行楷", 25), foreground="green")
    lsave.place(anchor="center", width=350, height=50, x=250, y=110)

    b1save = tk.Button(showSave, text="取消", command=exitSave, relief="flat", bg="#e0e0e0")
    b1save.place(anchor="center", width=76, height=38, x=115, y=220)

    b11save = tk.Button(showSave, text="确定", command=exitSave, relief="flat", bg="#e0e0e0")
    b11save.place(anchor="center", width=76, height=38, x=385, y=220)
    showSave.mainloop()


def colorConfig():  # 颜色配置函数
    color = colorChooser.askcolor(parent=rootWindows, title="颜色选择")
    if color[0] is not None:  # 根据主题颜色计算时间标签的颜色，从而使时间标签清晰可见
        if (110 < color[0][0] < 136) and(110 < color[0][1] < 136) and(110 < color[0][2] < 136):
            color0 = [0, 0, 0]
        else:
            color0 = (255-color[0][0], 255-color[0][1], 255-color[0][2])
        color1 = []
        for i in color0:
            if i < 16:
                color1.append("0" + str(hex(i))[2:])
            else:
                color1.append(str(hex(i))[2:])
        colorReverse = "#%s%s%s" % (color1[0], color1[1], color1[2])
        jsonDict["colorConfig"] = color[1]
        rootWindows.configure(bg=color[1])
        modelLabel.configure(bg=color[1])
        labelTime.configure(bg=color[1])
        labelTime2.configure(bg=color[1])
        modelLabel0.configure(bg=color[1])
        labelTime.configure(foreground=colorReverse)
        labelTime2.configure(foreground=colorReverse)
        if (color[0][0] <= 128) and (color[0][1] <= 128) and (color[0][2] <= 128):  # 根据主题颜色更改文字标签颜色，使其清晰可见
            modelLabel0.configure(foreground="#ffffff")
            modelLabel.configure(foreground="#ffffff")
        else:
            modelLabel0.configure(foreground="#000000")
            modelLabel.configure(foreground="#000000")
        fileConfig = open("fileConfig.json", "w")
        json.dump(jsonDict, fileConfig)
        fileConfig.close()


def send(self):  # 用户提问消息发送函数，将根据应答函数的返回值分别处理
    if len(jsonDict["Key"]) == 0:
        messageBox.showerror(title="错误", message="你还没有有效的API-Key")
    else:
        textSend = textLittle.get("1.4", END)
        contentDict = {'role': 'user', 'content': textSend}
        message.append(contentDict)
        receiveCode, textReceive = gpt_35_api_stream(message, jsonDict["model"])
        if receiveCode is False:
            textBig.configure(state="normal")
            textBig.insert("end", "发生错误！" + textReceive + "\n--------------------\n\n")
            textBig.configure(state="disable")
            messageBox.showerror(title="error", message="API服务出错，错误信息:" + textReceive)
            message.remove(message[-1])
        else:
            message.append({'role': 'assistant', 'content': textReceive})
            textBig.configure(state="normal")
            textBig.insert(END, textSend)
            startIndex = textBig.index(END)  # 为问题和“回答:”添加格式标签
            print(startIndex)
            dotIndex = startIndex.find(".")
            startIndex01 = str(int(startIndex[:dotIndex]) - 2) + ".0"
            endIndex01 = startIndex01[:dotIndex + 1] + str(len(textSend))
            startIndex02 = str(int(startIndex01[:dotIndex]) + 1) + ".0"
            endIndex02 = startIndex02[:dotIndex] + ".4"
            textBig.tag_add("ask", startIndex01, endIndex01)
            textBig.insert(END, "回答:")
            textBig.tag_add("ans", startIndex02, endIndex02)
            textBig.insert(END, textReceive)
            textBig.insert(END, "\n--------------------\n\n")
            textBig.configure(state="disable")
            textLittle.delete("1.4", END)


def subWindows():  # 在用户首次启动时弹出的提示对话框
    r = tk.Toplevel(rootWindows)
    r.title("更新提示")
    r.geometry("500x400+300+150")
    r.config(bg="#e0e0e0")
    r.resizable(0, 0)
    t2 = tk.Text(r, relief="flat", font=("楷体", 15))
    t2.place(width="450", height="360", anchor="center", x="250", y="200")
    t2.insert("end", '更新内容说明:\n\n1.修复"发送"按钮失效的问题\n\n2.可支持自定义API与代理服务器\n\n3.优化了其他若干体验')
    t2.configure(state="disabled")
    r.mainloop()


def askApi():  # 接收API-Key的函数

    def getKey():

        def exitag():
            rag.destroy()

        keyIn = ta.get("1.0", "end")[:-1]
        inCheck = re.fullmatch(r"sk-[0-9a-zA-Z]{48}", keyIn)  # 此处会对接收的结果进行正则表达式检查
        if inCheck is not None:
            jsonDict["Key"] = keyIn
            openai.api_key = jsonDict["Key"]
            fa = open("fileConfig.json", "w")
            json.dump(jsonDict, fa)
            fa.close()
            ra.destroy()
            rag = tk.Toplevel()
            rag.title("API-Key")
            rag.geometry("500x280+500+250")
            rag.resizable(0, 0)
            lag = tk.Label(rag, text="保存成功", font=("华文行楷", 25), foreground="green")
            lag.place(anchor="center", width=350, height=50, x=250, y=110)

            b1ag = tk.Button(rag, text="取消", command=exitag, relief="flat", bg="#e0e0e0")
            b1ag.place(anchor="center", width=76, height=38, x=115, y=220)

            b11ag = tk.Button(rag, text="确定", command=exitag, relief="flat", bg="#e0e0e0")
            b11ag.place(anchor="center", width=76, height=38, x=385, y=220)

            rag.mainloop()
        else:
            messageBox.showwarning(title="警告", message="输入有误，请重试！", parent=ra)

    def exita():
        ra.destroy()

    ra = tk.Toplevel()
    ra.title("API-Key")
    ra.geometry("500x280+500+250")
    ra.resizable(0, 0)
    la = tk.Label(ra, text="在此输入API-Key:", font=("华文新魏", 15))
    la.place(anchor="center", width=350, height=50, x=250, y=40)

    ta = tk.Text(ra, relief="flat", font=("楷体", 13))
    ta.place(anchor="center", width=400, height=100, x=250, y=120)

    b1a = tk.Button(ra, text="取消", command=exita, relief="flat", bg="#e0e0e0")
    b1a.place(anchor="center", width=76, height=38, x=115, y=220)

    b11a = tk.Button(ra, text="确定", command=getKey, relief="flat", bg="#e0e0e0")
    b11a.place(anchor="center", width=76, height=38, x=385, y=220)

    ra.mainloop()


def askSer():  # 代理服务器地址接收函数

    def clear():
        jsonDict["Ser"] = ""
        fs = open("fileConfig.json", "w")
        json.dump(jsonDict, fs)
        fs.close()
        messageBox.showinfo(title="提示", message="已重置，重启生效", parent=rs)

    def getUrl():

        def exitsg():
            rsg.destroy()

        urlIn = ts.get("1.0", "end")[:-1]
        urlCheck = re.fullmatch(r"[0-9a-zA-Z.:/-]{10,200}", urlIn)  # 此处会利用正则表达式对接收的结果进行简单规则检查
        if urlCheck is not None:
            jsonDict["Ser"] = urlIn
            openai.api_base = jsonDict["Ser"]
            fs = open("fileConfig.json", "w")
            json.dump(jsonDict, fs)
            fs.close()
            rs.destroy()
            rsg = tk.Toplevel()
            rsg.title("代理地址")
            rsg.geometry("500x280+500+250")
            rsg.resizable(0, 0)
            lsg = tk.Label(rsg, text="保存成功", font=("华文行楷", 25), foreground="green")
            lsg.place(anchor="center", width=350, height=50, x=250, y=110)

            b1sg = tk.Button(rsg, text="取消", command=exitsg, relief="flat", bg="#e0e0e0")
            b1sg.place(anchor="center", width=76, height=38, x=115, y=220)

            b11sg = tk.Button(rsg, text="确定", command=exitsg, relief="flat", bg="#e0e0e0")
            b11sg.place(anchor="center", width=76, height=38, x=385, y=220)

            rsg.mainloop()
        else:
            messageBox.showwarning(title="警告", message="输入有误，请重试", parent=rs)

    def exits():
        rs.destroy()

    rs = tk.Toplevel()
    rs.title("代理URL")
    rs.geometry("500x280+500+250")
    rs.resizable(0, 0)
    ls = tk.Label(rs, text="在此输入服务器地址:", font=("华文行楷", 15))
    ls.place(anchor="center", width=350, height=50, x=250, y=40)

    ts = tk.Text(rs, relief="flat", font=("楷体", 13))
    ts.place(anchor="center", width=400, height=100, x=250, y=120)

    b1s = tk.Button(rs, text="取消", command=exits, relief="flat", bg="#e0e0e0")
    b1s.place(anchor="center", width=76, height=38, x=115, y=220)

    b11s = tk.Button(rs, text="确定", command=getUrl, relief="flat", bg="#e0e0e0")
    b11s.place(anchor="center", width=76, height=38, x=385, y=220)

    b12s = tk.Button(rs, text="重置", command=clear, relief="flat", bg="#e0e0e0")
    b12s.place(anchor="center", width=76, height=38, x=250, y=220)

    rs.mainloop()


def modelSelect():  # 模型选择函数

    def fun1(modelText):
        jsonDict["model"] = modelText
        modelLabel.configure(text=modelText)
        ff1 = open("fileConfig.json", "w")
        json.dump(jsonDict, ff1)
        ff1.close()
        modelWindows.destroy()

    def fun2():  # 自定义输入，暂未设置检查机制
        modelName = tm.get("1.0", "end")[:-1]
        jsonDict["model"] = modelName
        modelLabel.configure(text=modelName)
        ff2 = open("fileConfig.json", "w")
        json.dump(jsonDict, ff2)
        ff2.close()
        modelWindows.destroy()

    modelWindows = tk.Toplevel()
    modelWindows.title("模型选择")
    modelWindows.geometry("180x360+600+150")
    modelWindows.resizable(0, 0)

    bm1 = tk.Button(modelWindows, text="gpt-4", command=lambda: fun1("gpt-4"), relief="flat", font=("华文新魏", 13), bg="#e0e0e0")
    bm1.place(width=180, height=40, x=0, y=0)

    bm2 = tk.Button(modelWindows, text="gpt-3.5-turbo", command=lambda: fun1("gpt-3.5-turbo"), relief="flat", font=("华文新魏", 13), bg="#f0f0f0")
    bm2.place(width=180, height=40, x=0, y=40)

    bm3 = tk.Button(modelWindows, text="gpt-3.5-turbo-16k", command=lambda: fun1("gpt-3.5-turbo-16k"), relief="flat", font=("华文新魏", 13), bg="#e0e0e0")
    bm3.place(width=180, height=40, x=0, y=80)

    lm = tk.Label(modelWindows, text="自定义:", font=("华文新魏", 20), relief="flat", bg="#f0f0f0", anchor="w", foreground="blue")
    lm.place(width=180, height=40, x=0, y=160)

    tm = tk.Text(modelWindows, relief="flat", font=("楷体", 15), bg="#ffffff")
    tm.place(width=170, height=80, x=5, y=200)

    bm4 = tk.Button(modelWindows, text="确定", command=fun2, relief="flat", bg="#d0d0d0")
    bm4.place(anchor="center", width=64, height=32, x=90, y=310)

    modelWindows.mainloop()


def showHelp():  # 帮助信息对话框
    helpWindows = tk.Toplevel()
    helpWindows.title("帮助")
    helpWindows.geometry("600x600+350+100")
    helpWindows.configure(bg="#ffffff")
    helpWindows.resizable(0, 0)
    infoHelp = """1.请确保fileConfig文件与本程序位于同一目录下\n
2.暂未优化项说明:发送框中（即提问的消息中）应避免出现换行\n
3.注意：若API不可用或服务器连接延迟大将使程序一直处于发送请求或接收响应中，从而导致界面无法操作或无响应，请耐心等待结果反馈\n
4.特别建议使用快捷键进行复制粘贴操作（复制:"Ctrl+C"; 粘贴:"Ctrl+V"; 剪切:"Ctrl+X")\n
5.注意：并非所有GPT模型都被每个API支持，请正确选择\n
6.重置代理服务器即恢复为官方服务器, 需重启后生效"""
    textHelp = tk.Text(helpWindows, relief="flat", state="normal", bg="#ffffff", font=("楷体", 15))
    textHelp.insert("end", infoHelp)
    textHelp.tag_configure("r", foreground="#ff8000")
    textHelp.tag_add("r", "5.0", "5.64")
    textHelp.configure(state="disable")
    textHelp.place(anchor="center", width=590, height=590, x=300, y=300)
    helpWindows.mainloop()


def timeSet():  # 时间函数，刷新间隔为2毫秒
    strTime = time.strftime("%I:%M:%S", time.localtime())
    labelTime.configure(text=strTime)
    strTime2 = time.strftime("%Y-%m-%d %a %p", time.localtime())
    labelTime2.configure(text=strTime2)
    rootWindows.after(2, timeSet)


try:
    fileCheck = open("fileConfig.json", "r")  # 尝试加载配置文件信息
    dictCheck = json.load(fileCheck)
    jsonDict["colorConfig"] = dictCheck["colorConfig"]
    jsonDict["isFirst"] = dictCheck["isFirst"]
    jsonDict["Key"] = dictCheck["Key"]
    jsonDict["Ser"] = dictCheck["Ser"]
    jsonDict["model"] = dictCheck["model"]
    fileCheck.close()
except FileNotFoundError:
    jsonDict["colorConfig"] = "#fb7299"
    jsonDict["model"] = "gpt-3.5-turbo"
    r233 = tk.Tk()
    r233.geometry("1x1+700+440")
    messageBox.showwarning(title="警告", message="配置文件缺失，请检查文件完整性", parent=r233)
    r233.after(1, r233.destroy)
    r233.mainloop()

openai.api_key = jsonDict["Key"]
if len(jsonDict["Ser"]) != 0:  # 若未配置代理服务器，将使用官方服务器
    openai.api_base = jsonDict["Ser"]


# 主窗口启动
rootWindows = tk.Tk()
rootWindows.title("chat-GPT")
rootWindows.geometry("1080x720")
rootWindows.configure(bg=jsonDict["colorConfig"])

textBig = tk.Text(rootWindows, font=("楷体", 16), state="normal", relief="flat")
textBig.place(anchor="center", relwidth=0.73, relheight=0.65, relx=0.39, rely=0.35)
textBig.insert(END, "结果在此展示。项目完善中，欢迎反馈问题或提出建议，E-mail:f_x110@163.com, 开发者@F\n\n")

scrollbar = tk.Scrollbar(rootWindows, command=textBig.yview, cursor="arrow", relief="flat")
scrollbar.place(anchor="center", relwidth=0.02, relheight=0.65, relx=0.765, rely=0.350)

textBig.config(yscrollcommand=scrollbar.set)

textBig.tag_config("waring", font=("楷体", 11))
textBig.tag_add("waring", 1.0, 2.0)
textBig.configure(state="disable")
textBig.tag_config("ask", font=("华文行楷", 15), foreground="red")
textBig.tag_config("ans", font=("楷体", 16, "italic"), foreground="blue")

textLittle = tk.Text(rootWindows, font=("楷体", 16), bg="#f0f0f0", relief="flat")
textLittle.insert(END, "请输入:")
textLittle.bind("<Return>", send)
textLittle.place(anchor="center", relwidth=0.75, relheight=0.24, relx=0.4, rely=0.83)
delete()

button = tk.Button(rootWindows, text="发送", command=lambda: send(self=None), relief="flat")
button.place(anchor="center", relwidth=0.08, relheight=0.04, relx=0.83, rely=0.73)

buttonReset = tk.Button(rootWindows, text="重置对话", command=reset, relief="flat")
buttonReset.place(anchor="center", relwidth=0.08, relheight=0.04, relx=0.83, rely=0.8)

buttonSave = tk.Button(rootWindows, text="保存对话记录", command=save, relief="flat")
buttonSave.place(anchor="center", relwidth=0.08, relheight=0.04, relx=0.83, rely=0.87)

buttonColorSetting = tk.Button(rootWindows, text="主题颜色设置", command=colorConfig, relief="flat")
buttonColorSetting.place(anchor="center", relwidth=0.08, relheight=0.04, relx=0.95, rely=0.04)

buttonApi = tk.Button(rootWindows, text="自定义API-Key", command=askApi, relief="flat")
buttonApi.place(anchor="center", relwidth=0.12, relheight=0.04, relx=0.88, rely=0.12)

buttonSer = tk.Button(rootWindows, text="自定义代理服务器", command=askSer, relief="flat")
buttonSer.place(anchor="center", relwidth=0.12, relheight=0.04, relx=0.88, rely=0.18)

modelLabel0 = tk.Label(rootWindows, text="当前GPT模型:", font=("楷体", 14), relief="flat", bg=jsonDict["colorConfig"], anchor="w")
modelLabel0.place(anchor="center", relwidth=0.16, relheight=0.06, relx=0.88, rely=0.26)

modelLabel = tk.Label(rootWindows, text=jsonDict["model"], font=("楷体", 15), relief="flat", bg=jsonDict["colorConfig"])
modelLabel.place(anchor="center", relwidth=0.16, relheight=0.06, relx=0.88, rely=0.30)

modelButton = tk.Button(rootWindows, text="更多", relief="flat", command=modelSelect)
modelButton.place(anchor="center", relwidth=0.04, relheight=0.025, relx=0.97, rely=0.33)

helpButton = tk.Button(rootWindows, text="帮助", relief="flat", command=showHelp)
helpButton.place(anchor="center", relwidth=0.06, relheight=0.03, relx=0.849, rely=0.04)

labelTime = tk.Label(rootWindows, relief="flat", font=("华文琥珀", 25), foreground="red", bg=jsonDict["colorConfig"], anchor="center")
labelTime.place(anchor="center", relwidth=0.14, relheight=0.07, relx=0.885, rely=0.45)
labelTime2 = tk.Label(rootWindows, relief="flat", font=("Cooper black", 12), foreground="red", bg=jsonDict["colorConfig"])
labelTime2.place(anchor="center", relwidth=0.15, relheight=0.05, relx=0.885, rely=0.49)
timeSet()

if jsonDict["isFirst"] is False:  # 根据配置文件决定是否弹出第一次提示对话框
    rootWindows.after(2000, subWindows)
    jsonDict["isFirst"] = True
    f = open("fileConfig.json", "w")
    json.dump(jsonDict, f)
    f.close()

rootWindows.mainloop()
