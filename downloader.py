# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os

import requests
import csv
import os,sys
import datetime
from bs4 import BeautifulSoup
from pprint import pprint
import json
import sys
import threading
import urllib.request

BASE_URL = "http://braintrust.iwtstudents.com"


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

class DownloaderApp:
    
    
    def login_and_get_list(self, username, password):
        
        LOGIN_URL = "http://braintrust.iwtstudents.com/users/login"
        
        
        headers = {
         
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
         
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        
        'Connection': 'keep-alive'
    }
 
        login_payload = {
                          
                         '_method' :'POST',
                         'data[User][email]':    username,
                         'data[User][password]': password,    
                         'data[User][remember_me]' : 1   
                          
                         }
         
        self.session = requests.Session()
         
        self.session.get(LOGIN_URL,headers=headers)
         
        r= self.session.post(LOGIN_URL, data=login_payload)
        
        soup = BeautifulSoup(r.content)
        div_list = soup.find_all('div',{'class':'modulenav-single'})
        
        items = []
        for div in div_list:
            num = int(div.find('span',{'class':'numPart'}).text.strip('#'))
            a =  div.find('a')
            title =a.text
            url = BASE_URL + a.attrs['href']
             
            item ={}
            item['id'] = num
            item['url'] = url
            pprint(item)
            items.append(item)
            
        return items
    
    def get_item_data(self,item):
        
        r = self.session.get(item['url'])
        html = r.content
        
        soup = BeautifulSoup(html)
        div = soup.find('div',{'class':'modulebtn'})
        
        div_video = div.find('div',{'class':'video'})
        div_audio = div.find('div',{'class':'audio'})
        div_transcript = div.find('div',{'class':'transcript'})
        
        txt = soup.find('h1',{'class':'moduletitle'}).text
        parts = txt.rsplit('with',1)
        
        title = parts[0].strip(' -').replace(':',' -').replace("'","")
        author = parts[-1].strip()
        
        item['title'] = title
        item['author'] = author
       
            
        
        video = BASE_URL + div_video.find('a').attrs['href']
        audio = BASE_URL + div_audio.find('a').attrs['href']
        transcript = BASE_URL + div_transcript.find('a').attrs['href']
        files_to_down = []
        files_to_down.append(transcript)
        files_to_down.append(audio)
        files_to_down.append(video)
        
        item['downloads'] = files_to_down
        
        

    def __init__(self, root):
        
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        self.save_path = StringVar()
        self.root = root
        self.root.title("Amp Your Results - Ramit's Brain Trust Downloader")
        self.root.iconbitmap(default='app.ico')

        self.counter = 0
        self.session = None
        self.download_percentage = DoubleVar()
        
        frame = ttk.Frame(root)
        frame.pack()
        frame.config(height = 400, width = 600)
        frame.config(relief = RIDGE)
        frame.config(padding = (30, 15))
        
        frame2 = ttk.Frame(root)
        frame2.pack()
        frame2.config(height = 200, width = 600)
        frame2.config(padding = (30, 15))
        
        
        
        self.logo = ttk.Label(frame)
        logo_path = os.path.join(BASE_DIR,'logo.png')
        self.logo_file = PhotoImage(file = logo_path)
        self.logo.config(image = self.logo_file)
        self.logo.grid(row = 0, column = 0, columnspan = 4)
        
        self.title = ttk.Label(frame, text = "Ramit's Brain Trust Downloader")
        self.title.grid(row = 1, column = 0, columnspan = 4)
        self.title.config(font = ('Courier', 18, 'bold'))

       
        
        label = ttk.Label(frame, text = "Username:")
        label.grid(row = 2, column = 0)
        self.username = ttk.Entry(frame, width = 30)
        self.username.grid(row = 2, column = 1)
        
        label = ttk.Label(frame, text = "Password:")
        label.grid(row = 3, column = 0)
        
        self.password = ttk.Entry(frame, width = 30,show='*')
        self.password.grid(row = 3, column = 1)
        
        
        label = ttk.Label(frame, text = "Download Folder:")
        label.grid(row = 4, column = 0)
        
        
        
        self.folder = ttk.Entry(frame, width = 30, textvariable = self.save_path)
        self.folder.grid(row = 4, column = 1)
        ttk.Button(frame, text = "Browse...",
                   command = self.choose_folder).grid(row = 4, column = 2)
        self.save_path.set(BASE_DIR)
        ttk.Button(frame, text = "Download",
                   command = self.do_download).grid(row = 5, column = 1)
                   
                   
        
                   
        self.status1 = ttk.Label(frame2,text="--")
        self.status1.pack()
        self.status2 = ttk.Label(frame2,text="--")
        self.status2.pack()
        
        
        self.progressbar = ttk.Progressbar(frame2, mode='determinate' ,orient = HORIZONTAL,length = 400)

        self.progressbar.pack()
        
        
        
    
    def update_bar(self,block_count, block_size, total_size):
        
        if block_count == 0:
            self.counter = 0
            self.progressbar.config(maximum = total_size )
        self.counter += block_size
        self.progressbar.config( value = self.counter )
        self.root.update()
        
        
        
      

    def choose_folder(self):
        self.save_path.set( filedialog.askdirectory(initialdir = self.save_path.get()))
        pass
    
    def do_download(self):
        username = self.username.get()
        if username.strip()=="":
            messagebox.showerror("Error", "Username field is required")
            self.username.focus()
            return
        
        password = self.password.get()
        if password.strip()=="":
            messagebox.showerror("Error", "Password field is required")
            self.password.focus()
            return
        
        _status1 = ""
        self.status1.config(text=_status1)
        _status2 = "Start Downloading..."
        self.status2.config(text=_status2)  
        self.root.update()
        
        items = self.login_and_get_list(username, password)
        
        total_files = len(items) * 1
        counter = 1
        
        
        for item in items:
            self.get_item_data(item)
            
            dir_name = "{0}_{1}_{2}".format(item['id'],item['author'],item['title'])
            save_location = os.path.join(self.save_path.get(),dir_name)
            
            if not os.path.exists(save_location):
                print ("creating saving directory", save_location)
                os.makedirs(save_location)
            
            for f in item['downloads']:
 
                status1 = "Downloading {0}/{1}".format(counter , total_files )
                self.status1.config(text=status1)
                self.root.update()
                self.download_file(f,save_location)

                counter = counter + 1
                
            
        
        
        _status1 = ""
        self.status1.config(text=_status1)
        _status2 = "Download Completed."
        self.status2.config(text=_status2)  
        self.root.update()
        pass
    
    def download_file(self, url ,save_location):
    
    
        r = self.session.get(url, stream=True)
        print("downloading:", r.url)
        filename = r.url.split('/')[-1].split('?')[0]
        
        file_size = int(r.headers['Content-Length'])
      
        file_path = os.path.join(save_location,filename)
        self.status2.config(text="")
        status2 = "   {0}    {1}   ".format(filename , convert_bytes(file_size))
        self.status2.config(text = status2)
        
        self.root.update()
        urllib.request.urlretrieve(r.url, file_path, reporthook=self.update_bar)
                   
        return file_path
    
    
      

            
def main():            
    
    root = Tk()
    app = DownloaderApp(root)
    root.mainloop()
    
if __name__ == "__main__": 
    main()