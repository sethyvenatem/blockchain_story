# -----------------------------------------------------------
# Graphical user interface for the 3 blockchain functionalities
#
# 24/10/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
import json
import os
import glob
import sys
from io import StringIO
#from tkinter.tix import *
#from tkinter.ttk import *

from chapter_signature import *
from mining import *
from checks import *
from blockchain_functions import *

class ScrollableFrame:
    # thanks https://stackoverflow.com/questions/1844995/how-to-add-a-scrollbar-to-a-window-with-tkinter?answertab=modifieddesc#tab-top
    """
    # How to use class
    from tkinter import *
    obj = ScrollableFrame(master,height=300 # Total required height of canvas,width=400 # Total width of master)
    objframe = obj.frame
    # use objframe as the main window to make widget
    """
    def __init__ (self,master,width,height,mousescroll=0):
        self.mousescroll = mousescroll
        self.master = master
        self.height = height
        self.width = width
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill='both',expand=1)

        self.scrollbar = tk.Scrollbar(self.main_frame, orient= 'vertical')
        self.scrollbar.pack(side='right',fill='y')

        self.canvas = tk.Canvas(self.main_frame,yscrollcommand=self.scrollbar.set)
        self.canvas.pack(expand=True,fill='both')
 
        self.scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        self.frame = tk.Frame(self.canvas,width=self.width,height=self.height)
        self.frame.pack(expand=True,fill='both')
        self.canvas.create_window((0,0), window=self.frame, anchor="nw")

        self.frame.bind("<Enter>", self.entered)
        self.frame.bind("<Leave>", self.left)

    def _on_mouse_wheel(self,event):
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    def entered(self,event):
        if self.mousescroll:
            self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def left(self,event):
        if self.mousescroll:
            self.canvas.unbind_all("<MouseWheel>")

def open_chapter_signature_window(event):
    
    welcome_window.destroy()
    global chapter_signature_window
    chapter_signature_window = tk.Tk()
    #Just set the nb of pixels below small enough!
    chapter_signature_window.geometry("800x600")
    chapter_signature_window.title('Chapter signature')

    chapter_signature_frame_scroll = ScrollableFrame(chapter_signature_window,height=800 ,width=600)
    chapter_signature_frame = chapter_signature_frame_scroll.frame
 #   chapter_signature_frame = tk.Frame(chapter_signature_window)
 #   chapter_signature_frame.grid(row = 0,column = 0)

    #Do this above in the class definition. Do it to the canvas
#    chapter_signature_window.rowconfigure([0], weight=1)
#    chapter_signature_window.columnconfigure([0], weight=1)
#    chapter_signature_frame_scroll.main_frame.rowconfigure([0], weight=1)
#    chapter_signature_frame_scroll.main_frame.columnconfigure([0], weight=1)
#    chapter_signature_frame_scroll.canvas.rowconfigure([0], weight=1)
#    chapter_signature_frame_scroll.canvas.columnconfigure([0], weight=1)
 #   chapter_signature_frame.rowconfigure([0,1,2,3,4,5], weight=1)
#    chapter_signature_frame.columnconfigure([0,1], weight=1)

    fr_accept= tk.Frame(master = chapter_signature_frame, highlightbackground="black", highlightthickness=2)
    text_boxes_widths = 40
    lbl_sign_greeting = tk.Label(master = chapter_signature_frame, text="Please fill in your chapter data here.")
    lbl_story_title = tk.Label(master = chapter_signature_frame, text="Story title:")
    lbl_chapter_number = tk.Label(master = chapter_signature_frame, text="Chapter number:")
    lbl_chapter_title = tk.Label(master = chapter_signature_frame, text="Chapter title:")
    lbl_author_name = tk.Label(master = chapter_signature_frame, text="Author name:")
    lbl_chapter_text = tk.Label(master = chapter_signature_frame, text="Chapter text (no spell-check here!):")
    lbl_above_accept = tk.Label(master = fr_accept, text='Click below to digitally sign your chapter submission')
    lbl_below_accept = tk.Label(master = fr_accept, text='Be careful that:\n - The story title field is correct.\n - The chapter number is correct.\n - There are no typos in you submission.',justify="left")
    global ent_story_title 
    ent_story_title= tk.Entry(master = chapter_signature_frame, width = text_boxes_widths)
    global ent_chapter_number
    ent_chapter_number = tk.Entry(master = chapter_signature_frame, width = text_boxes_widths)
    global ent_chapter_title
    ent_chapter_title = tk.Entry(master = chapter_signature_frame, width = text_boxes_widths)
    global ent_author_name
    ent_author_name = tk.Entry(master = chapter_signature_frame, width = text_boxes_widths)
    but_accept_entry = tk.Button(master = fr_accept, text = 'Sign it!')
    # thanks https://stackoverflow.com/questions/13832720/how-to-attach-a-scrollbar-to-a-text-widget
    global scroll_txt
    scroll_txt = scrolledtext.ScrolledText(master = chapter_signature_frame, width = text_boxes_widths, height = 30)
        
    # Place the widgets on the window
    lbl_sign_greeting.grid(row = 0, column = 1, pady = 10, sticky='ew')
    lbl_story_title.grid(row = 1, column = 0, padx = 10, sticky='w')
    lbl_chapter_number.grid(row = 2, column = 0, padx = 10, sticky='w')
    lbl_chapter_title.grid(row = 3, column = 0, padx = 10, sticky='w')
    lbl_author_name.grid(row = 4, column = 0, padx = 10, sticky='w')
    lbl_chapter_text.grid(row = 5, column = 0, padx = 10, sticky='nw')
    ent_story_title.grid(row = 1, column = 1, padx=10, sticky='EW')
    ent_chapter_number.grid(row = 2, column = 1, padx=10, sticky='EW')
    ent_chapter_title.grid(row = 3, column = 1, padx=10, sticky='EW')
    ent_author_name.grid(row = 4, column = 1, padx=10, sticky='EW')

    scroll_txt.grid(row = 5, column = 1, padx=10, sticky='EW')
    
    lbl_above_accept.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = 'nw')
    lbl_below_accept.grid(row = 1, column = 0)
    but_accept_entry.grid(row = 2, column = 0, pady = 10)

    fr_accept.grid(row = 5, column = 0, pady = 60, padx = 10, sticky = 'nw')
    
    but_accept_entry.bind("<Button-1>", run_chapter_signature)
    
    chapter_signature_window.mainloop()
    
def run_chapter_signature(event):
    
    story_title = ent_story_title.get()
    chapter_number = ent_chapter_number.get()
    chapter_title = ent_chapter_title.get()
    author_name = ent_author_name.get()
    text = scroll_txt.get("1.0", tk.END)
    
    chapter_data = {'story_title': story_title,
                    'chapter_number': int(chapter_number),
                    'author': author_name,
                    'chapter_title': chapter_title,
                    'text': text}
    
    with open('temp_chapter_data.json', "w", encoding='utf-8') as outfile:
        json.dump(chapter_data, outfile, ensure_ascii = False, sort_keys = True)

    #thanks! https://stackoverflow.com/questions/5884517/how-to-assign-print-output-to-a-variable
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    status = sign_chapter('temp_chapter_data.json')
    result_string = result.getvalue()
    sys.stdout = old_stdout
    
    chapter_signature_window.destroy()
    signed_chapter_window = tk.Tk()
    signed_chapter_window.title('Signed chapter')
    signed_chapter_window.geometry("800x600")
    #signed_chapter_window.columnconfigure(0, weight=1)
    #signed_chapter_window.rowconfigure([0,1], weight=1)
    signed_chapter_frame_scroll = ScrollableFrame(signed_chapter_window,height=800 ,width=600)
    signed_chapter_frame = signed_chapter_frame_scroll.frame
    
    lbl_signed_chapter_data = tk.Label(master = signed_chapter_frame, text = 'Your chapter has been digitally signed!\nSee the text below for a description of what happened.\nClose this window when you are finished.')
    if status == 'error':
        lbl_signed_chapter_data.config(text = 'Oups, something is not right.\nSee the text below for a description of what happened.\nClose this window and try again.')
    
    scroll_sign_messages = scrolledtext.ScrolledText(master = signed_chapter_frame, height = 35, width = 105)
    scroll_sign_messages.insert("1.0", result_string)
    lbl_signed_chapter_data.grid(row = 0, column = 0, padx=10, pady = 10)
    scroll_sign_messages.grid(row = 1, column = 0, padx=10, pady = 10)
    os.remove('temp_chapter_data.json')
    
    signed_chapter_window.mainloop()
    
def open_mining_window(event):
    
    welcome_window.destroy()
    global mining_window
    mining_window = tk.Tk()
    mining_window.title('Chapter mining')
    mining_window.geometry("800x600")
    #mining_window.columnconfigure([0,1], weight=1)
    #mining_window.rowconfigure([0,1,2,3,4,5], weight=1)

    mining_window_frame_scroll = ScrollableFrame(mining_window,height=800 ,width=600)
    mining_window_frame = mining_window_frame_scroll.frame
    
    lbl_story_choice = tk.Label(master = mining_window_frame, text="Select an unfinished validated story below. This is the story\nto which you want to add a new chapter. Pick the story with\nthe right title and the largest number of chapters. If multiple\nstories have the same title and number of chapters, then pick\nthe one with the smallest story run-time. You can scroll!",justify="left")
#    lbl_story_choice = tk.Label(text="Select an unfinished validated story below. This is the story to which you want to add a new chapter.\n\nPick the story with:\n - the right title.\n - the largest number of chapters.\n \nIf multiple stories have the same title and number of chapters, then pick the one with the smallest story run-time. You can scroll !",justify="left")
    lbl_story_choice.grid(row = 0, column = 0, sticky = 'nw', padx = 10)
    
    json_files = glob.glob('*.json')
    
    validated_stories = sorted([f for f in json_files if all([x.isdigit() for x in import_json(f, False).keys()]) and (len(import_json(f, False)) != 0)])
    validated_stories.reverse()

    signed_chapters = sorted([f for f in json_files if set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(import_json(f, False).keys())])
    signed_chapters.reverse()

    # Import all the available signed chapters and validated stories
    validated_stories_json = []
    for validated_story in validated_stories:
        temp = import_json(validated_story)
        if temp != 'error':
            temp = temp[str(max([int(b) for b in temp.keys()]))]['block_content']
            validated_stories_json.append(temp)
    signed_chapters_json = []
    for signed_chapter in signed_chapters:
        temp = import_json(signed_chapter)
        if temp != 'error':
            temp = temp['chapter_data']
            signed_chapters_json.append(temp)
    
    table_validated_chapters = ttk.Treeview(master = mining_window_frame, height = 9)

    table_validated_chapters['columns'] = ('story_title', 'chapter_number', 'miner_name', 'story_runtime_seconds')
    table_validated_chapters.column("#0", width=0, stretch='NO')
    table_validated_chapters.column("story_title", width=100)
    table_validated_chapters.column("chapter_number",width=70)
    table_validated_chapters.column("miner_name",width=100)
    table_validated_chapters.column("story_runtime_seconds",width=85)
    
    table_validated_chapters.heading("#0",text="",)
    table_validated_chapters.heading("story_title",text="Story title")
    table_validated_chapters.heading("chapter_number",text="Chapters")
    table_validated_chapters.heading("miner_name",text="Last miner name")
    table_validated_chapters.heading("story_runtime_seconds",text="Story run-time")
    
    for ind, validated_story in enumerate(validated_stories_json):
        if 'signed_chapter_data' in validated_story.keys():
            val = (validated_story['signed_chapter_data']['chapter_data']['story_title'], validated_story['signed_chapter_data']['chapter_data']['chapter_number'],validated_story['miner_name'],validated_story['story_runtime_seconds'])
        else:
            val = (validated_story['story_title'], validated_story['chapter_number'],validated_story['miner_name'],validated_story['story_runtime_seconds'])
        table_validated_chapters.insert(parent='',index='end',iid=ind,text='', values = val)
        
    table_validated_chapters.grid(row = 1,column = 0, padx = 10, pady = 10)

    def get_validated_story_file(a):
        # thanks: https://stackoverflow.com/questions/30614279/tkinter-treeview-get-selected-item-values
        curItem = table_validated_chapters.focus()
        global validated_story_file
        validated_story_file = validated_stories[int(curItem)]

    table_validated_chapters.bind('<ButtonRelease-1>', get_validated_story_file)

    lbl_chapter_choice = tk.Label(master = mining_window_frame, text="Select a signed chapter below. This is the chapter that you want\nto add to the story. Pick the story with the right title and the right\nchapter number. You can scroll!",justify="left")
#    lbl_chapter_choice = tk.Label(text="Select a signed chapter below. This is the chapter that you want to add to the story.\n\nPick the story with:\n - the right title.\n - the right chapter number.\n \nYou can scroll !",justify="left")    
    lbl_chapter_choice.grid(row = 2, column = 0,  padx = 10)
    
    table_signed_chapters = ttk.Treeview(master = mining_window_frame,height = 9)
    table_signed_chapters['columns'] = ('story_title', 'chapter_number', 'author', 'chapter_title')
    table_signed_chapters.column("#0", width=0, stretch='NO')
    table_signed_chapters.column("story_title", width=100)
    table_signed_chapters.column("chapter_number",width=60)
    table_signed_chapters.column("author",width=100)
    table_signed_chapters.column("chapter_title",width=120)
    
    table_signed_chapters.heading("#0",text="",)
    table_signed_chapters.heading("story_title",text="Story title")
    table_signed_chapters.heading("chapter_number",text="Chapter")
    table_signed_chapters.heading("author",text="Author")
    table_signed_chapters.heading("chapter_title",text="Chapter title")
    
    for ind, signed_chapter in enumerate(signed_chapters_json):
        val = (signed_chapter['story_title'], signed_chapter['chapter_number'],signed_chapter['author'],signed_chapter['chapter_title'])
        table_signed_chapters.insert(parent='',index='end',iid=ind,text='', values = val)
    
    table_signed_chapters.grid(row = 3,column = 0, padx = 10, pady = 10)
    
    def get_signed_chapter_file(a):
        curItem = table_signed_chapters.focus()
        global signed_chapter_file
        signed_chapter_file = signed_chapters[int(curItem)]
    
    table_signed_chapters.bind('<ButtonRelease-1>', get_signed_chapter_file)
    
    lbl_miner_name = tk.Label(master = mining_window_frame, text="Enter your miner name:",justify="left")
    lbl_miner_name.grid(row = 0, column = 1, sticky = 'ws', padx = 10)
    global ent_miner_name
    ent_miner_name = tk.Entry(master = mining_window_frame, width = 25)
    ent_miner_name.grid(row = 1, column = 1, sticky = 'nw', padx = 10, pady = 10)
    
    global var1
    var1 = tk.IntVar(master = mining_window_frame, )
    check_send_to_discord = tk.Checkbutton(master = mining_window_frame, text="Automatically send the validated file to\nthe discord server. You can also\nupload it manually later.", variable=var1,justify="left")
    check_send_to_discord.grid(row = 2,column = 1, padx = 10, pady = 10, sticky = 'nw')
    but_start_mining = tk.Button(master = mining_window_frame, text = 'Start mining! This will take some time.')
    but_start_mining.grid(row = 3, column = 1,padx = 10, pady = 10)
    but_start_mining.bind("<Button-1>", run_mining)
    #https://www.geeksforgeeks.org/how-to-get-selected-value-from-listbox-in-tkinter/
    # to make tickboxes: https://python-course.eu/tkinter/checkboxes-in-tkinter.php
    #to make table: https://pythonguides.com/python-tkinter-table-tutorial/
    
    mining_window.mainloop()
    
def run_mining(event):
    
    miner_name = ent_miner_name.get()
    send = var1.get()
    if send:
        send = 'yes'
    else:
        send = 'no'

    mining_window.destroy()
    mined_chapter_window = tk.Tk()
    mined_chapter_window.title('Mined chapter')
    mined_chapter_window.geometry("800x600")
    #mined_chapter_window.columnconfigure(0, weight=1)
    #mined_chapter_window.rowconfigure([0,1], weight=1)

    mined_chapter_window_frame_scroll = ScrollableFrame(mined_chapter_window,height=800 ,width=600)
    mined_chapter_window_frame = mined_chapter_window_frame_scroll.frame
    
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    status = mine_chapter(validated_story_file, signed_chapter_file, miner_name, send = send)
    result_string = result.getvalue()
    sys.stdout = old_stdout
    
    scroll_sign_messages = scrolledtext.ScrolledText(master = mined_chapter_window_frame, height = 35, width = 105)
    scroll_sign_messages.insert("1.0", result_string)
    if status == 'error':
        lbl_mined_chapter = tk.Label(master = mined_chapter_window_frame, text = 'Something is not right.\nSee the text below for a description of what happened.\nClose this window and try again.')
    else:
        lbl_mined_chapter = tk.Label(master = mined_chapter_window_frame, text = 'Your have mined a new chapter!\nSee the text below for a description of what happened.\nClose this window when you are finished.')
    lbl_mined_chapter.grid(row = 0, column = 0, sticky = 'n', padx=10, pady = 10)
    scroll_sign_messages.grid(row = 1, column = 0, sticky = 'n', padx=10, pady = 10)
    
    mined_chapter_window.mainloop()
    
def open_check_window(event):
    
    welcome_window.destroy()
    global check_window
    check_window = tk.Tk()
    check_window.title('Check file')
    check_window.geometry("800x600")
#    check_window.columnconfigure(0, weight=1)
#    check_window.rowconfigure([0,1,2], weight=1)

    check_window_frame_scroll = ScrollableFrame(check_window,height=800 ,width=600)
    check_window_frame = check_window_frame_scroll.frame
    
    lbl_check_greeting = tk.Label(master = check_window_frame, text="Select a file to check and then view.\n\nYou can scroll!")
    lbl_check_greeting.grid(row = 0, column = 0, padx = 10, pady = 10)
    
    file_names = sorted(glob.glob('*.json'))
    file_names.reverse()
    json_files = [import_json(f, False) for f in file_names]
    
    table_to_check = ttk.Treeview(master = check_window_frame, height = 22)
    table_to_check['columns'] = ('file_type', 'story_title', 'chapter_number', 'chapter_title', 'author')
    table_to_check.column("#0", width=0, stretch='NO')
    table_to_check.column("file_type", width=150)
    table_to_check.column("story_title",width=175)
    table_to_check.column("chapter_number",width=60)
    table_to_check.column("chapter_title",width=175)
    table_to_check.column("author",width=175)
    
    table_to_check.heading("#0",text="",)
    table_to_check.heading("file_type",text="File type")
    table_to_check.heading("story_title",text="Story title")
    table_to_check.heading("chapter_number",text="Chapters")
    table_to_check.heading("chapter_title",text="(Last) chapter title")
    table_to_check.heading("author",text="Author")
    
    for ind, file in enumerate(json_files):
        if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(file.keys()):
            val = ('un-signed chapter',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
            table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
        elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(file.keys()):
            val = ('signed chapter',file['chapter_data']['story_title'],file['chapter_data']['chapter_number'],file['chapter_data']['chapter_title'],file['chapter_data']['author'])
            table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
        elif set(['block_content', 'hash']) == set(file.keys()):
            if 'signed_chapter_data' in file['block_content'].keys():
                file = file['block_content']['signed_chapter_data']
                val = ('validated block (isolated)',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
                table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
            else:
                file = file['block_content']
                val = ('validated genesis block (isolated)',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
                table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
        elif all([x.isdigit() for x in file.keys()]) and (len(file) != 0):
            
            largest_block_nb = str(max([int(k) for k in file.keys()]))
            if largest_block_nb == '0':
                file = file['0']['block_content']
                val = ('validated genesis block',file['story_title'],file['chapter_number'], 'no title',file['author'])
                table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
            else:
                file = file[largest_block_nb]['block_content']['signed_chapter_data']['chapter_data']
                val = ('validated story',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
                table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
    
    def get_file_to_check(a):
        curItem = table_to_check.focus()
        global file_to_check
        file_to_check = file_names[int(curItem)]
    
    table_to_check.bind('<ButtonRelease-1>', get_file_to_check)
    
    table_to_check.grid(row = 1, column = 0, padx = 10, pady = 10)
    but_check_file = tk.Button(master = check_window_frame, text = 'Check the selected file.')
    but_check_file.bind("<Button-1>", run_checks)
    but_check_file.grid(row = 2, column = 0, padx = 10, pady = 10)
    
    check_window.mainloop()
    
def run_checks(event):
    
    check_window.destroy()
    checked_window = tk.Tk()
    checked_window.title('File checked')
    checked_window.geometry("800x600")
#    checked_window.columnconfigure([0,1], weight=1)
#    checked_window.rowconfigure([0,1], weight=1)

    checked_window_frame_scroll = ScrollableFrame(checked_window,height=800 ,width=600)
    checked_window_frame = checked_window_frame_scroll.frame
    
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    status = check_file(file_to_check)
    result_string = result.getvalue()
    sys.stdout = old_stdout
    
    scroll_sign_messages = scrolledtext.ScrolledText(master = checked_window_frame,height = 20)
    scroll_sign_messages.insert("1.0", result_string)
    if status == 'error':
        lbl_checked_file = tk.Label(master = checked_window_frame, text = 'Something is not right.\nTry again.')
    elif status == 'check_genesis':
        lbl_checked_file = tk.Label(master = checked_window_frame, text = 'File checked!')
    else:
        with open(status) as f:
            chapter_text = f.read()
        scroll_chapter_text = scrolledtext.ScrolledText(master = checked_window_frame,height = 20)
        scroll_chapter_text.insert("1.0", chapter_text)
        lbl_checked_file = tk.Label(master = checked_window_frame, text = 'File checked!')
        lbl_display_text = tk.Label(master = checked_window_frame, text = 'Read the file content:')
        lbl_display_text.grid(row = 1, column = 0, sticky = 'n', padx=10, pady = 10)
        scroll_chapter_text.grid(row = 1, column = 1, sticky = 'n', padx=10, pady = 10)
        
    lbl_checked_file.grid(row = 0, column = 0, sticky = 'n', padx=10, pady = 10)
    scroll_sign_messages.grid(row = 0, column = 1, sticky = 'n', padx=10, pady = 10)
    
    checked_window.mainloop()
    
welcome_window = tk.Tk()
welcome_window.title('What to do...')
welcome_window.columnconfigure([0,1,2], weight=1)
welcome_window.rowconfigure([0,1], weight=1)
welcome_window.eval('tk::PlaceWindow . center')

lbl_greeting = tk.Label(text="What do you want to do?")
but_sign_chapter = tk.Button(text = 'Digiatlly sign a chapter')
but_mine_chapter = tk.Button(text = 'Attempt to mine a chapter')
but_check_read = tk.Button(text = 'Check a json file and read it\'s content')

lbl_greeting.grid(row = 0, column = 1)
but_sign_chapter.grid(row=1, column=0, pady = 10, padx = 10)
but_mine_chapter.grid(row=1, column=1, pady = 10, padx = 10)
but_check_read.grid(row=1, column=2, pady = 10, padx = 10)

but_sign_chapter.bind("<Button-1>", open_chapter_signature_window)
but_mine_chapter.bind("<Button-1>", open_mining_window)
but_check_read.bind("<Button-1>", open_check_window)
    
welcome_window.mainloop()

# https://realpython.com/python-gui-tkinter/
# https://www.askpython.com/python-modules/tkinter/tkinter-text-widget-tkinter-scrollbar