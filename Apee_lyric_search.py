import requests
import ctypes
import tkinter as tk
import tkinter.ttk as ttk
import time
import threading
import requests
import json
import html


class Apee_lyric_search(tk.Tk):
    '''
    APEE 歌词搜索工具
    https//apee.top
    '''

    keyword: tk.StringVar
    '''搜索关键词'''
    search_tip: str = '请输入歌名/歌手名/专辑名'
    result_list = []
    '''搜索结果列表'''

    def __init__(self):
        super().__init__()
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        self.tk.call('tk', 'scaling', 2)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = 495
        win_height = 710
        self.geometry(
            '%dx%d+%d+%d'
            % (
                win_width,
                win_height,
                (screen_width - win_width) / 2,
                (screen_height - win_height) / 2,
            ),
        )
        self.title('APEE 歌词搜索工具')
        # self.resizable(False, False)
        self.init_style()
        self.load_component()
        self.mainloop()

    def init_style(self):
        style = ttk.Style()
        style.configure("My.TEntry", padding=10)

    def load_component(self):
        '''加载组件'''
        self.add_search_box()
        self.add_search_result()

    def add_lyric(self, lyric_text):
        '''歌词内容框'''
        com_text = tk.Text(self, width=30, height=17, font=('微软雅黑', 13))
        com_text.grid(column=0, columnspan=2, row=1, padx=10)
        com_text.delete('1.0', 'end')
        com_text.insert('end', lyric_text)
        button = ttk.Button(self, text='返回列表')
        self.com_text = com_text
        self.back_button = button
        button.grid(column=0, columnspan=2, row=2, pady='10 0')
        button.bind('<ButtonRelease-1>', self.back_to_list)
        self.result_frame.grid_forget()

    def back_to_list(self, event=None):
        self.back_button.grid_forget()
        self.com_text.grid_forget()
        self.add_search_result()

        # 清空列表
        self.list_box.delete(0, tk.END)
        for i in self.result_list:
            text = '  ' + i['name'] + ' - ' + i['artist'] + '\n'
            text = html.unescape(text)
            self.list_box.insert('end', text)

    def add_search_result(self):
        '''搜索结果'''

        def click_get_lyric(event):
            '''获取歌词'''
            indexs = self.list_box.curselection()
            if len(indexs) == 0:
                return
            index = indexs[0]
            data = self.result_list[index]
            music_id = data['musicrid'][6:]
            url = 'http://m.kuwo.cn/newh5/singles/songinfoandlrc?musicId=' + music_id
            r = requests.get(url)
            r.encoding = 'utf-8'
            result_data = json.loads(r.text)
            lyric_data = [i['lineLyric'] for i in result_data['data']['lrclist']]
            lyric_text = '\n'.join(lyric_data)
            self.add_lyric(lyric_text)

        frame = ttk.Frame(self)
        frame.grid(column=0, columnspan=2, row=1)
        self.result_frame = frame
        scroll_bar = ttk.Scrollbar(frame)
        scroll_bar_h = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        list_box = tk.Listbox(
            frame,
            yscrollcommand=scroll_bar.set,
            xscrollcommand=scroll_bar_h.set,
            width=41,
            height=25,
        )
        self.list_box = list_box
        scroll_bar_h.pack(side='bottom', fill='x')
        scroll_bar.pack(side='right', fill='y')
        list_box.pack(side='left', padx='10 0', fill='both')
        scroll_bar.config(command=list_box.yview)
        scroll_bar_h.config(command=list_box.xview)
        list_box.bind(
            '<Double-Button-1>',
            lambda event: threading.Thread(
                target=click_get_lyric, args=(event,)
            ).start(),
        )

    def add_search_box(self):
        '''搜索框'''
        self.keyword = tk.StringVar()
        self.keyword.set(self.search_tip)
        entry = ttk.Entry(
            self,
            width=30,
            textvariable=self.keyword,
        )
        button = ttk.Button(self, text='搜索')
        entry.grid(column=0, row=0, padx='10 0', pady=10)
        entry.bind('<FocusIn>', self.focus)
        entry.bind('<FocusOut>', self.focus)
        entry.bind('<Return>', lambda event: self.click_search(event, button))
        button.grid(column=1, row=0, padx='5 0')
        button.bind('<ButtonRelease-1>', lambda event: self.click_search(event, button))

    def click_search(self, event, widget):
        try:
            if not self.result_frame.winfo_ismapped():
                self.back_to_list()
        except:
            pass

        def search(widget, keyword):
            url = (
                'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?pn=1&rn=30&key='
                + keyword
            )
            r = requests.get(
                url,
                headers={
                    'Referer': 'kuwo.cn',
                    'Cookie': 'kw_token=apee',
                    'Csrf': 'apee',
                },
            )
            r.encoding = 'utf-8'
            result = json.loads(r.text)
            if result['code'] != 200:
                return
            list_data = result['data']['list']
            self.result_list = list_data
            # 清空列表
            self.list_box.delete(0, tk.END)
            for i in list_data:
                text = '  ' + i['name'] + ' - ' + i['artist'] + '\n'
                text = html.unescape(text)
                self.list_box.insert('end', text)
            widget.config(text='搜索')

        if str(widget['text']) == '搜索中':
            return
        keyword = self.keyword.get()
        if keyword == self.search_tip or keyword == '':
            return
        widget.config(text='搜索中')
        threading.Thread(target=search, args=(widget, keyword)).start()

    def focus(self, event):
        if str(event.type) == 'FocusIn':
            if self.keyword.get() == self.search_tip:
                self.keyword.set('')
        elif str(event.type) == 'FocusOut':
            if self.keyword.get() == '':
                self.keyword.set(self.search_tip)


if __name__ == '__main__':
    print('By: OuYangPeng, Link: https://apee.top.')
    Apee_lyric_search()
