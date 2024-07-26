from tkinter import *
from tkinter import ttk,filedialog
from tkinter import messagebox
import os,windnd,cv2,ffmpeg,ctypes,sys
import numpy as np
#import moviepy.editor as mp     
from Icon import img
if hasattr(sys, 'frozen'):
    File = os.path.dirname(sys.executable)
elif __file__:
    File = os.path.dirname(__file__)
print(os.path.dirname(sys.executable),os.path.dirname(os.path.abspath(__file__)))
print(f"路径：{File}\n启动ing~")
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
ico_name="tMp"
Repeat=True
while Repeat:
    Repeat=False
    files=list(os.walk(os.path.dirname(File)))[0][2]
    if ico_name+".ico" in files:
        ico_name+="tMp"
        Repeat=True
        break
ico_PATH=os.path.dirname(File)+"\\"+ico_name+".ico"

myappid = "product"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root=Tk()

with open(ico_PATH,"wb+") as tmp:
    tmp.write(img)
root.iconbitmap(ico_PATH)
os.remove(ico_PATH)

w,h=202,346
scr=root.maxsize()
root.geometry(f"{w}x{h}+{int(scr[0]/2-w/2)}+{int(scr[1]/2-h/2)-134}")
root.resizable(height=False, width=False)
root.title("视频转图像序列")

is_info_show=True
def Info_show():
    global is_info_show
    info_show.config(text="展开面板 ▲" if is_info_show else "收起面板 ▼")
    for i in (name,resloution,framerate_name,Frame_all,preview_png_size):
        i.grid_remove() if is_info_show else i.grid()
    is_info_show=not is_info_show
info_show=Button(root,text="收起面板 ▼",bg="ivory",command=Info_show)
name=Label(root,text="文件名：",bg="darkslategrey",fg="lightblue")
resloution=Label(root,text="视频分辨率：",bg="darkslategrey",fg="lightblue")
framerate_name=Label(root,text="输入视频帧率：",bg="darkslategrey",fg="lightblue")
Frame_all=Label(root,text="输入视频总帧数：",bg="darkslategrey",fg="lightblue")
preview_png_size=Label(root,text="输出图片大小：",bg="darkslategrey",fg="lightblue")
framerateoutput_name=Label(root,text="输出帧率",bg="lightblue")
output_process=Label(root,text="处理进度：0%",bg="lightblue")

def Preview_png_size(content):
    realfps=fps if content=="" else int(content)
    imgcount=int(timelength*realfps)
    if direction.get()=="竖向":
        w,h=video_width,video_height*imgcount
    else:
        w,h=video_width*imgcount,video_height
    preview_png_size.config(text=f"输出图片大小：{w}x{h}")
def test(content):
    if content.isdigit() or content == "":
        if fps and not content=="":
            if int(content)>fps:
                return False
        Preview_png_size(content)
        return True
    else:
        return False
test_cmd = root.register(test)
framerate=Entry(root,
        validate = "key",
        validatecommand = (test_cmd, '%P'))
def framerate_refresh(event):
    if fps:
        framerate.delete(0,END)
        framerate.insert(0,fps)
framerate.bind("<Button-3>",framerate_refresh)
        
direction_name=Label(root,text='方向',bg="lightblue")
direction=ttk.Combobox(root,)
direction["value"]=("横向","竖向")
direction.current(1)
direction['state']='readonly'

Use_Alpha=IntVar()
Invert=IntVar()
use_Alpha=Checkbutton(root,text="使用透明度",bg="lightblue",variable=Use_Alpha)
invert=Checkbutton(root,text="反转",bg="lightblue",variable=Invert)

#empty=Label(root,text="")

def read_frame_as_png(in_file, frame_num):
    out, err = (
    ffmpeg.input(in_file)
       .filter('select', 'gte(n,{})'.format(frame_num))
       .output('pipe:', vframes=1, format='image2', vcodec='png')
       .run(cmd=File+r"\ffmpeg.exe",capture_stdout=True)
  )
    return out
def Output():
    video=cv2.VideoCapture(Path)
    if int((fps if framerate.get()=="" else int(framerate.get()))*timelength)*(video_height if direction.get()=="竖向" else video_width)>10000 or video_height>10000 or video_width>10000:
        if not messagebox.askyesno("警告","png文件的长或(和)宽将在10000以上,是否继续导出？",icon=messagebox.WARNING):
            return
    #print(int((fps if framerate.get()=="" else int(framerate.get()))*timelength)*(video_height if direction.get()=="竖向" else video_width),video_height,video_width)
    realfps=fps if framerate.get()=="" else int(framerate.get())
    imgcount=int(timelength*realfps)
    h,w=video_height*((imgcount) if direction.get()=="竖向" else 1),video_width*((imgcount) if direction.get()=="横向" else 1)
    img = np.zeros((h,w,4 if Use_Alpha.get() else 3), np.uint8)
    ca=0
    if Invert.get():
        ca_sel_height,ca_sel_width=h,w
    else:
        ca_sel_height,ca_sel_width=0,0
    output_process.grid()
    Is_4=True
    for i in range(imgcount):
        i+=1
        t=int(i*(fps/realfps))
        sp=t-ca-1
        ca=t
        for o in range(sp):
            video.read()
        if Use_Alpha.get() and Is_4:
            out=read_frame_as_png(Path,t-1)
            image_array = np.asarray(bytearray(out), dtype="uint8")
            content = [0,cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)]
            if len(content[1][0][0])==3:
                print("alpha but 3")
                Is_4=False
                content=video.read()
                img = np.zeros((h,w,3), np.uint8)
        else:
            content=video.read()
        #print(content[1])

        if Invert.get():
            sel_height=h-(video_height*(i if direction.get()=="竖向" else 1))
            sel_width=w-(video_width*(i if direction.get()=="横向" else 1))
            #print(len(content),ca_sel_height,sel_height,ca_sel_width,sel_width,"\n",ca_sel_height-sel_height,ca_sel_width-sel_width,"\n",video_height,video_width)
            img[sel_height:ca_sel_height,sel_width:ca_sel_width]=content[1]
        else:
            sel_height=video_height*(i if direction.get()=="竖向" else 1)
            sel_width=video_width*(i if direction.get()=="横向" else 1)
            #print(len(content),ca_sel_height,sel_height,ca_sel_width,sel_width,"\n",ca_sel_height-sel_height,ca_sel_width-sel_width,"\n",video_height,video_width)
            img[ca_sel_height:sel_height,ca_sel_width:sel_width]=content[1]
        if direction.get()=="竖向":
            ca_sel_height=sel_height
        else:
            ca_sel_width=sel_width
        output_process.config(text=f"处理进度：{int((i/imgcount)*100)}%")
        root.update()
    output_process.config(text="处理进度：完成，等待输出")
    print(os.path.dirname(Path))
    f=filedialog.asksaveasfile(initialfile="save",initialdir=os.path.dirname(Path),title="图片保存路径",filetypes=[("PNG",".png")],defaultextension = ".png")
    if f is None:
        output_process.grid_remove()
        output_process.config(text="处理进度：0%")
        return
    fname=f.name
    f.close()
    try:
        os.remove(fname)
    except:
        pass
    cv2.imencode('.png', img)[1].tofile(fname)
    #cv2.imwrite(fname,img)
    output_process.grid_remove()
    output_process.config(text="处理进度：0")

output=Button(root,text="导出",width=20,bg="darkred",command=Output)

for c,i in enumerate((info_show,name,resloution,framerate_name,Frame_all,preview_png_size,framerateoutput_name,framerate,direction_name,direction,use_Alpha,invert,output,output_process)):
    i.grid(row=c,column=1,columnspan=4,sticky=W)
for i in (info_show,name,resloution,framerate_name,Frame_all,preview_png_size,output,output_process):
    i.grid_remove()
'''for i in (framerate,invert):
    i.config(state='disable')'''

timelength=0
video_width=0
video_height=0
fps=False
def drag(files):
    if len(files)>1:
        return

    global video_height,video_width,fps,frame_all,timelength,Path
    Path=files[0].decode('gbk')
    
    video=cv2.VideoCapture(Path)
    if not video.isOpened():
        messagebox.showerror('错误', '非可解析文件！')
        return
    name.config(text=f"文件名：{os.path.basename(Path)}")
    '''if Path[-3:len(Path)]=="gif":
        clip = mp.VideoFileClip(Path)     
        clip.write_videofile(os.getenv('TEMP')+"\\videoTEMP_BY_THE_CONVERT_PLUG_IN(若你能找到这个文件,请在关闭视频转图像序列这个插件后再删除)(为防重复而导致的可能其他软件运行不正常,再重复一遍(如果这都能文件名重复我也没办法了))videoTEMP_BY_THE_CONVERT_PLUG_IN(若你能找到这个文件,请在关闭视频转图像序列这个插件后再删除).mp4",codec="png")
    '''
    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_all=int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    timelength=frame_all/fps

    framerate_name.config(text=f"输入视频帧率：{fps}")
    Frame_all.config(text=f"输入视频总帧数：{frame_all}")
    resloution.config(text=f"视频分辨率：{video_width}x{video_height}")
    for i in (name,info_show,resloution,framerate_name,Frame_all,preview_png_size,output):
        i.grid()
    if int(0 if framerate.get()=="" else framerate.get())>fps:
        framerate.delete(0,END)
        framerate.insert(0,fps)
    Preview_png_size(fps if framerate.get()=="" else int(framerate.get()))
windnd.hook_dropfiles(root,func=drag)

root.mainloop()

