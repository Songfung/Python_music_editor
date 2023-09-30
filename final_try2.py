#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import flet as ft
from pydub import AudioSegment
from pydub.playback import play
from numpy import linalg as la
from numpy.random import uniform
import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt
import scipy.io.wavfile as wf
import numpy.fft as nf
import wave
from flet import (
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    FilePickerUploadEvent,
    FilePickerUploadFile,
    Page,
    ProgressRing,
    Ref,
    Row,
    Text,
    icons,
)



# In[2]:


"""function of dealing with the sound """

## get the length of sound
def get_all_lentgh(file):
        sr, signal1s = wf.read(file)
        print("sr = {}".format(sr))
        print("signals number = {}".format(signal1s.size))
        times = np.arange(len(signal1s))/sr#時間=訊號點數量/取樣頻率
        print("times=",len(signal1s)/sr*1000)
        
        return len(signal1s)/sr*1000
##   change_speed
def change_speed(file ,speed):
    audio = AudioSegment.from_file(file, format="wav")
    if speed != 1:
        speed_shifted = audio.speedup(playback_speed= speed)
    else:
        speed_shifted = audio

    wav_file = "speed_shifted.wav"
    speed_shifted.export(wav_file, format="wav")
    return 0

## change_volume 
def change_volume(file , volumn):
    audio = AudioSegment.from_file(file, format="wav")
    volumn_shifted = audio + volumn
    wav_file = "volumn_shifted.wav"
    volumn_shifted.export(wav_file, format="wav")
    return 0



def add_noice(file, if_noise):
    data,sr = sf.read(file)
    if(if_noise):
        
        data_noise = data
        #print(data.shape)
        snr_db =20 ## snr_db( Signal-to-noise ratio )為音訊與噪音power的比例
        signal_power = np.sum(data**2)/len(data)
        noise_power = signal_power / (10**(snr_db / 10))
        ##使噪音呈常態分佈
        noise = np.random.normal(scale = np.sqrt(noise_power), size = len(data))
        noise = np.transpose(noise)
        data_noise = np.transpose(data_noise)
        #print((data_noise).shape)
        data_noise[:] = data_noise[:] + noise
        

        #data_noise[0][:] = data_noise[0][:] + noise
        #data_noise[1][:] = data_noise[1][:] +noise
        sf.write("data_noise.wav", np.transpose(data_noise),sr)
    else:
        sf.write("data_noise.wav", data,sr)
    return 0

##function: noice_cancel
def noice_cancel(file, if_cancel):
    sr, signals = wf.read(file)
    if(if_cancel):
        complex_arr = nf.fft(signals)
        print("complex_arr = ",complex_arr)
        power = np.abs(complex_arr)
        power_tran=np.transpose(power)
        
        
        #################
        #plt.title("original with noice")
        #plt.plot(power)
        #plt.show()
        ###########

        print("power_tran =",power_tran)
        descend_0 =np.sort(power_tran[0]) 
        print("descend_0 is =",descend_0)
        descend_0 =descend_0 [: :-1]
        print("descend_0 ---1 is =",descend_0)
        print("8888888888888",descend_0[0] > descend_0[-1] )
        print("8888888877777",descend_0[0] ,descend_0[-1] )
        descend_1 =np.sort(power_tran[1]) [ 0: :-1]
        
        remove_rate = 0.03
        remove_arr = complex_arr
        
#         for i in range(complex_arr.shape[0]):
#             print(abs(complex_arr[i]))
#             print((descend_0[0]*remove_rate))
#             if(abs(complex_arr[i]) <= (descend_0[0]*remove_rate)):
#                 remove_arr[i] = 0+0j
        for i in range(complex_arr.shape[0]):
            #print(abs(complex_arr[i][0]),(descend_0[0]*remove_rate))
            if(abs(complex_arr[i][0]) <= (descend_0[0]*remove_rate)):
                
                remove_arr[i][0] = 0+0j

        for i in range(complex_arr.shape[0]):
            if(abs(complex_arr[i][1]) <= (descend_1[0]*remove_rate)):
                remove_arr[i][1] = 0 +0j
                
        #################
        #plt.title("noice canceling")
        #plt.plot(remove_arr)
        #plt.show()
        ###########
        
        
        filter_signals = nf.ifft(remove_arr)
        filter_signals = filter_signals.astype("i2")
        wf.write("noice_cancel.wav", sr ,filter_signals)
    else:
        wf.write("noice_cancel.wav", sr ,signals)
    print("enddddd")    
    return 0

##sound clip
def sound_cut(audio,start_t, end_t):
    audio_cut = audio[start_t:end_t]
    wav_file = "audio_cut.wav"
    audio_cut.export(wav_file, format="wav")
    return audio_cut
    
##sound echo
def echo(file,if_echo1):
    audio, fs = sf.read(file)
    if if_echo1:
        
        delay_sec = 0.3  # Delay time in seconds
        decay = 0.5  # Decay ratio (0.0 to 1.0)
        gain = 0.5  # Echo gain
        delay_samples = int(delay_sec * fs)
        echoed_audio = np.zeros_like(audio)
        echoed_audio[delay_samples:] += audio[:-delay_samples] * decay
        echoed_audio += audio * gain
        sf.write('output.wav', echoed_audio, fs)
    else:
        sf.write('output.wav', audio, fs)
    return 0
    # Save the echoed audio to a file
       

    


# In[ ]:


"""python GUI"""
DEFAULT_FLET_PATH = ''
DEFAULT_FLET_PORT = 8502

def main(page: Page):
    
    global input_sound
    global start_time1
    global end_time1
    global if_noise
    if_noise = False
    global if_addnoise
    if_addnoise = False 
    global if_echo
    if_echo = False
    global all_length
    
    page.title = " Sound editor"

    
    
    
    speed_number = ft.TextField(value="1", text_align="right", width=100)
    volume_number = ft.TextField(value="0", text_align="right", width=100)
    
    

    def pick_files_result(e: FilePickerResultEvent):
        selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        )

        selected_files.update()
        
            
        global input_sound
        input_sound = selected_files.value
        
        global all_length
        all_length = get_all_lentgh(input_sound)
        print(all_length)

        
        
        page.update()

    pick_files_dialog = FilePicker(on_result=pick_files_result)
    selected_files = Text()
    
    def picker_clicked(e):
        global input_sound  
        global all_length
        word1.value = "You have seleced " +input_sound +". Please choose the effect you want."
        tell_time_word.value = "The upload file length is "+str(all_length)+ " ms"
        print(selected_files.value)  
        print(type(selected_files.value))
    
        
        page.update()



    #  ############123123123       
    # def visualize(path, title):
    #     fig, ax = plt.subplots()  # 建立單一圖表
    #     raw = wave.open(path)          # 開啟聲音
    #     signal = raw.readframes(-1)    # 讀取全部聲音採樣
    #     signal = np.frombuffer(signal, dtype ="int16")  # 將聲音採樣轉換成 int16 的格式所組成的 np 陣列
    #     f_rate = raw.getframerate()    # 取得 framerate
    #     time = np.linspace(0, len(signal)/f_rate, num = len(signal))  # 根據聲音採樣產生成對應的時間

    #     ax.plot(time, signal)          # 畫線，橫軸時間，縱軸陣列值
    #     plt.title(title)        # 圖表標題
    #     plt.xlabel("Time")             # 橫軸標題
    #     plt.show()
    
    
    
    def start_click(aaa):
        global input_sound
        global start_time1
        global end_time1
        global if_noise
        global if_addnoise
        global if_echo
        global all_length
        
        wait_button.icon=icons.REPLAY_CIRCLE_FILLED_ROUNDED
        word2.value = None
        page.update()
        print("speed_number",int(speed_number.value))
        print("volume_number",volume_number.value)
        print("start_time1 =",start_time1)
        print("end_time1 = ",end_time1)
        
        
        
        
        ##start to do the process of sound
        audio = AudioSegment.from_file(input_sound, format="wav")
        s_cut = sound_cut(audio,start_time1, end_time1)
        print("cut finish!!!!!")
        
        ##################
        #visualize(input_sound, "input_sound")##@@@@@@

        # 建立繪製聲波的函式
                # 讀取聲音


        sr, signals = wf.read("audio_cut.wav")
        signals = signals/(2**15)
        complex_arr = nf.fft(signals)
        print("complex_arr = ",complex_arr)
        power = np.abs(complex_arr)
        power_tran=np.transpose(power)
        
        
        #plt.title("original without noice")
        #plt.plot(power)
        #plt.show()
        ######################
        #visualize("audio_cut.wav", "audio_cut")##@@@@@@
        
        change_volume("audio_cut.wav" , int(volume_number.value))
        print("volumn finish!!!!!")
        #visualize("volumn_shifted.wav", "volumn_shifted")##@@@@@@
        
        change_speed("volumn_shifted.wav", int(speed_number.value) )
        print("speef finish!!!!!")
        #visualize("speed_shifted.wav", "speed_shifted")##@@@@@@
        
        
        add_noice("speed_shifted.wav", if_addnoise)
        print("add noicd finish!!!!!")
        
        
        ##################
        #visualize("data_noise.wav", "add noice")##@@@@@@
        
        ######################
        
        
        noice_cancel("data_noise.wav", if_noise)
        print("cancel finish!!!!!")
        
        #visualize("noice_cancel.wav", "noice canceling") ##@@@@@@
        
        echo("noice_cancel.wav",if_echo)
        print("echo finish!!!!!")
        #visualize("output.wav", "add echo")##@@@@@@
      
        
        
        ##finish
        word2.value = " The process is finish, please go to find output.wav "
        wait_button.icon=icons.CHECK_CIRCLE
        wait_button.value = None
        page.update()
    
    
    def speed_minus_click(e):
        speed_number.value = str(int(speed_number.value) - 1)
        if(int(speed_number.value) == 0):
            speed_warn_word.value= "Warning! Speed can't be 0!!!"
        else:
            speed_warn_word.value= None
    
        
        page.update()
        
        
    def speed_plus_click(e):
        speed_number.value = str(int(speed_number.value) + 1)
        if(int(speed_number.value) == 0):
            speed_warn_word.value= "Warning! Speed can't be 0!!!"
        else:
            speed_warn_word.value= None
            
        
        page.update()
        
        
        
    
    def volume_minus_click(e):
        volume_number.value = str(int(volume_number.value) - 1)
        page.update()

    def volume_plus_click(e):
        volume_number.value = str(int(volume_number.value) + 1)
        page.update()
        

        
    def noise_yes_clicked(e):
        noise_no_button.icon = None
        noise_yes_button.icon = icons.CHECK_CIRCLE_OUTLINE_OUTLINED
        global if_noise
        if_noise = True
        page.update()
        
    def noise_no_clicked(e):
        noise_no_button.icon = icons.CHECK_CIRCLE_OUTLINE_OUTLINED
        noise_yes_button.icon = None
        global if_noise
        if_noise = False
        page.update()
        
    def addnoise_yes_clicked(e):
        
        addnoise_yes_button.icon = icons.CHECK_CIRCLE_OUTLINE_OUTLINED
        addnoise_no_button.icon = None
        global if_addnoise
        if_addnoise = True
        page.update()
        
    def addnoise_no_clicked(e):
        addnoise_no_button.icon = icons.CHECK_CIRCLE_OUTLINE_OUTLINED
        addnoise_yes_button.icon = None
        global if_addnoise
        if_addnoise = False
        page.update()
        
    def echo_yes_clicked(e):
        
        echo_yes_button.icon = icons.CHECK_CIRCLE_OUTLINE_OUTLINED
        echo_no_button.icon = None
        global if_echo
        if_echo = True
        page.update()
        
    def echo_no_clicked(e):
        echo_no_button.icon = icons.CHECK_CIRCLE_OUTLINE_OUTLINED
        echo_yes_button.icon = None
        global if_echo
        if_echo = False
        page.update()
        
    def clip_start_click(e):
        global start_time1
        
        if not start_time.value:
            start_time.error_text = "Default_starttime = 0ms"
            start_time1= 0
            page.update()
        else:
            start_time1 = int(start_time.value)
            

            
    def clip_end_click(e):
        global end_time1,all_length
            
        if not end_time.value:
            end_time.error_text = "Default_starttime ="+ str(all_length)+ " ms"
            end_time1= all_length
            page.update()
        else:
            end_time1 = int(end_time.value)
    
    
    
    
    
    
    
    ##st_echo########
    echo_yes_button = ElevatedButton(text="Yes", width=150, on_click=echo_yes_clicked)
    echo_no_button = ElevatedButton(text="No", width=150, on_click=echo_no_clicked)
    
    
    echo_text = ft.TextButton(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="echo", size=25),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=ft.padding.all(10),
            ),
            style = {ft.MaterialState.HOVERED: ft.colors.WHITE})
    
    echo_row = ft.Row(
            [
                echo_text,
                echo_yes_button,
                echo_no_button,
                

            ],)
    
    
    ####set_clip#####    
            
    tell_time_word = ft.Text()    
    start_time = ft.TextField(label="start_time(ms)")
    end_time = ft.TextField(label="end_time(ms)")
    set_start_button = ft.ElevatedButton("set start_time", on_click=clip_start_click)
    set_end_button = ft.ElevatedButton("set end_time", on_click=clip_end_click) 
    
    
    set_start_row = ft.Row(
            [
                start_time,
                set_start_button,
            ],)
    set_end_row = ft.Row(
            [
                end_time,
                set_end_button,
            ],)
    
    set_clip_text = ft.TextButton(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="set_clip_time", size=25),
                        #ft.Text(value="Please set the speed you want"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=ft.padding.all(10),
            ),
            style = {ft.MaterialState.HOVERED: ft.colors.WHITE})
    
    set_clip_row=ft.Row(
            [
                set_clip_text,
                tell_time_word,
            ],)    
        
    # hide dialog in a overlay
    page.overlay.extend([pick_files_dialog])
    
    
    
    ##end
    word1 = ft.Text(size = 20, color='#191970')
    word2 = ft.Text(size = 20, color='#191970')
    done_word = ft.Text()
    result_button = ElevatedButton(text=f"start", width=300, on_click=start_click)
    
    
    
    ####noise_cancel##### 
    noise_yes_button = ElevatedButton(text="Yes", width=150, on_click=noise_yes_clicked)
    noise_no_button = ElevatedButton(text="No", width=150, on_click=noise_no_clicked)
    
    
    noise_text = ft.TextButton(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="noise_canceling", size=25),
                        #ft.Text(value="Please set the speed you want"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=ft.padding.all(10),
            ),
            style = {ft.MaterialState.HOVERED: ft.colors.WHITE})
    
    noise_row = ft.Row(
            [
                noise_text,
                noise_yes_button,
                noise_no_button,
                

            ],)
    
    ####noise_add##### 
    addnoise_yes_button = ElevatedButton(text="Yes", width=150, on_click=addnoise_yes_clicked)
    addnoise_no_button = ElevatedButton(text="No", width=150, on_click=addnoise_no_clicked)
    
    
    addnoise_text = ft.TextButton(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="noise_adding", size=25),
                        #ft.Text(value="Please set the speed you want"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=ft.padding.all(10),
            ),
            style = {ft.MaterialState.HOVERED: ft.colors.WHITE})
    
    addnoise_row = ft.Row(
            [
                addnoise_text,
                addnoise_yes_button,
                addnoise_no_button,
                

            ],)
    
    ####speed##### 
    speed_warn_word = ft.Text() 
    speed_text = ft.TextButton(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="speed", size=25),
                        #ft.Text(value="Please set the speed you want"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=ft.padding.all(10),
            ),
            style = {ft.MaterialState.HOVERED: ft.colors.WHITE})
    
    
    speed_row = ft.Row(
            [
                speed_text,
                ft.IconButton(ft.icons.REMOVE, on_click=speed_minus_click),
                speed_number,
                ft.IconButton(ft.icons.ADD, on_click=speed_plus_click),
                speed_warn_word,
            ],)
    
    
    ####volume#####
    volume_text = ft.TextButton(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="volume ", size=25),
                        #ft.Text(value="Please set the speed you want"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                padding=ft.padding.all(10),
            ),
            style = {ft.MaterialState.HOVERED: ft.colors.WHITE})
    
    
    volume_row = ft.Row(
            [
                volume_text,
                ft.IconButton(ft.icons.REMOVE, on_click=volume_minus_click),
                volume_number,
                ft.IconButton(ft.icons.ADD, on_click=volume_plus_click),
            ],)
    
    ##wait button
    wait_button = ft.TextButton("Wait...")
    
    ##picker
    picker_button = ElevatedButton(text="OK", width=100, on_click=picker_clicked)
    
    picker_row = Row(
            [
                ElevatedButton(
                    "Pick files",
                    icon=icons.UPLOAD_FILE,
                    on_click=lambda _: pick_files_dialog.pick_files(
                        allow_multiple=True
                    ),
                ),
                selected_files,
                picker_button,
            ]
        )
    
    ####page#####
    page.add(
        picker_row,
        
        word1,
        
        speed_row,
        volume_row,
        echo_row,
        noise_row,
        addnoise_row,
        set_clip_row,
        set_start_row,
        set_end_row,
        ft.Row(
        [
            result_button,
            wait_button,
        word2,
        ],)
        
    )


ft.app(target=main)

