# -----------------------------------------------------------
# Graphical user interface for the 3 blockchain functionalities
#
# 07/09/2023 Steven Mathey
# email steven.mathey@gmail.ch
# -----------------------------------------------------------

import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
import json
#import os
import glob
#import subprocess
import sys

from io import StringIO

from chapter_signature import *
from mining import *
from checks import *
from blockchain_functions import *

# use the json content to decide if it's a signed_chapter, validated story or something else.

def open_chapter_signature_window(event):
    
    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    # Place the widgets on the window
    lbl_sign_greeting.grid(row = 0, column = 0, sticky='w')
    lbl_story_title.grid(row = 1, column = 0, sticky='w')
    lbl_chapter_number.grid(row = 2, column = 0, sticky='w')
    lbl_chapter_title.grid(row = 3, column = 0, sticky='w')
    lbl_author_name.grid(row = 4, column = 0, sticky='w')
    lbl_chapter_text.grid(row = 5, column = 0, sticky='nw')
    lbl_above_accept.grid(row = 0, column = 2, sticky = 'nw')
    lbl_below_accept.grid(row = 2, column = 2)
    ent_story_title.grid(row = 1, column = 1, sticky='EW', padx=10)
    ent_chapter_number.grid(row = 2, column = 1, sticky='EW', padx=10)
    ent_chapter_title.grid(row = 3, column = 1, sticky='EW', padx=10)
    ent_author_name.grid(row = 4, column = 1, sticky='EW', padx=10)
    but_accept_entry.grid(row = 1, column = 2)
    scroll_txt.grid(row = 5, column = 1, sticky='EW', padx=10)
    
    fr_form.grid(row = 0, column = 0, sticky = 'nw', padx = 10, pady = 10)
    fr_accept.grid(row = 0, column = 1, sticky = 'nw', pady = 10)

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
    
    with open('temp_chapter_data.json', "w") as outfile:
        outfile.write(json.dumps(chapter_data))

    #thanks! https://stackoverflow.com/questions/5884517/how-to-assign-print-output-to-a-variable
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    status = sign_chapter('temp_chapter_data.json')
    result_string = result.getvalue()
    sys.stdout = old_stdout
    
    if status == 'error':
        lbl_signed_chapter_data.config(text = 'Oups, something is not right.\nSee the text below for a description of what happened.\nClose this window and try again.')

    lbl_sign_greeting.grid_forget()
    lbl_story_title.grid_forget()
    lbl_chapter_number.grid_forget()
    lbl_chapter_title.grid_forget()
    lbl_author_name.grid_forget()
    lbl_chapter_text.grid_forget()
    lbl_above_accept.grid_forget()
    lbl_below_accept.grid_forget()
    ent_story_title.grid_forget()
    ent_chapter_number.grid_forget()
    ent_chapter_title.grid_forget()
    ent_author_name.grid_forget()
    but_accept_entry.grid_forget()
    scroll_txt.grid_forget()
    fr_form.grid_forget()
    fr_accept.grid_forget()
    
    scroll_sign_messages = scrolledtext.ScrolledText()
    scroll_sign_messages.insert("1.0", result_string)
    lbl_signed_chapter_data.grid(row = 0, column = 0,sticky = 'n', padx=10, pady = 10)
    scroll_sign_messages.grid(row = 1, column = 0,sticky = 'n', padx=10)
    os.remove('temp_chapter_data.json')
    
def open_mining_window(event):

    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    lbl_story_choice.grid(row = 0, column = 0, sticky = 'nw', padx = 10)
    
    json_files = glob.glob('*.json')
    
    validated_stories = sorted([f for f in json_files if all([x.isdigit() for x in import_json(f).keys()])])
    validated_stories.reverse()
    
    signed_chapters = sorted([f for f in json_files if set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(import_json(f).keys())])
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
    
    table_validated_chapters['columns'] = ('story_title', 'chapter_number', 'miner_name', 'story_age_seconds')
    table_validated_chapters.column("#0", width=0, stretch='NO')
    table_validated_chapters.column("story_title", width=150)
    table_validated_chapters.column("chapter_number",width=150)
    table_validated_chapters.column("miner_name",width=150)
    table_validated_chapters.column("story_age_seconds",width=150)
    
    table_validated_chapters.heading("#0",text="",)
    table_validated_chapters.heading("story_title",text="Story title")
    table_validated_chapters.heading("chapter_number",text="Last validated chapter nb")
    table_validated_chapters.heading("miner_name",text="Last miner name")
    table_validated_chapters.heading("story_age_seconds",text="Story age")
    
    for ind, validated_story in enumerate(validated_stories_json):
        if 'signed_chapter_data' in validated_story.keys():
            val = (validated_story['signed_chapter_data']['chapter_data']['story_title'], validated_story['signed_chapter_data']['chapter_data']['chapter_number'],validated_story['miner_name'],validated_story['story_age_seconds'])
        else:
            val = (validated_story['story_title'], validated_story['chapter_number'],validated_story['miner_name'],validated_story['story_age_seconds'])
        table_validated_chapters.insert(parent='',index='end',iid=ind,text='', values = val)
#        tk.Checkbutton(text='').grid(row=1, column = 1, sticky='w')
        
    table_validated_chapters.grid(row = 1,column = 0, padx = 10, pady = 10)

    def get_validated_story_file(a):
        # thanks: https://stackoverflow.com/questions/30614279/tkinter-treeview-get-selected-item-values
        curItem = table_validated_chapters.focus()
        global validated_story_file
        validated_story_file = validated_stories[int(curItem)]
    #        print(table_validated_chapters.item(curItem),curItem)

    table_validated_chapters.bind('<ButtonRelease-1>', get_validated_story_file)

    lbl_chapter_choice.grid(row = 2, column = 0, sticky = 'nw', padx = 10)
    
    table_signed_chapters['columns'] = ('story_title', 'chapter_number', 'author', 'chapter_title')
    table_signed_chapters.column("#0", width=0, stretch='NO')
    table_signed_chapters.column("story_title", width=150)
    table_signed_chapters.column("chapter_number",width=150)
    table_signed_chapters.column("author",width=150)
    table_signed_chapters.column("chapter_title",width=150)
    
    table_signed_chapters.heading("#0",text="",)
    table_signed_chapters.heading("story_title",text="Story title")
    table_signed_chapters.heading("chapter_number",text="Chapter number")
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
    
    lbl_miner_name.grid(row = 5, column = 0, sticky = 'nw', padx = 10)
    ent_miner_name.grid(row = 6, column = 0, sticky = 'nw', padx = 10, pady = 10)
    
    check_send_to_discord.grid(row = 7,column = 0, padx = 10, pady = 10)
    but_start_mining.grid(row = 8, column = 0,padx = 10, pady = 10)
    #https://www.geeksforgeeks.org/how-to-get-selected-value-from-listbox-in-tkinter/
    # to make tickboxes: https://python-course.eu/tkinter/checkboxes-in-tkinter.php
    #to make table: https://pythonguides.com/python-tkinter-table-tutorial/
    
def run_mining(event):
    
    miner_name = ent_miner_name.get()
    send = var1.get()
    if send:
        send = 'yes'
    else:
        send = 'no'
    but_start_mining.grid_forget()
    ent_miner_name.grid_forget()
    lbl_miner_name.grid_forget()
    table_signed_chapters.grid_forget()
    lbl_chapter_choice.grid_forget()
    table_validated_chapters.grid_forget()
    lbl_story_choice.grid_forget()
    check_send_to_discord.grid_forget()
    
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    status = mine_chapter(validated_story_file, signed_chapter_file, miner_name, send = send)
    result_string = result.getvalue()
    sys.stdout = old_stdout
    
    scroll_sign_messages = scrolledtext.ScrolledText()
    scroll_sign_messages.insert("1.0", result_string)
    if status == 'error':
        lbl_mined_chapter = tk.Label(text = 'Something is not right.\nSee the text below for a description of what happened.\nClose this window and try again.')
    else:
        lbl_mined_chapter = tk.Label(text = 'Your have mined a new chapter!\nSee the text below for a description of what happened.\nClose this window when you are finished.')
    lbl_mined_chapter.grid(row = 0, column = 0, sticky = 'n', padx=10, pady = 10)
    scroll_sign_messages.grid(row = 1, column = 0, sticky = 'n', padx=10)
    
def open_check_window(event):

    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    lbl_check_greeting = tk.Label(text="Select a file to check and then view.")
    lbl_check_greeting.grid(row = 0, column = 0, padx = 10, pady = 10)
    
    file_names = sorted(glob.glob('*.json'))
    file_names.reverse()
    json_files = [import_json(f) for f in file_names]
    
    table_to_check['columns'] = ('file_type', 'story_title', 'chapter_number', 'chapter_title', 'author')
    table_to_check.column("#0", width=0, stretch='NO')
    table_to_check.column("file_type", width=150)
    table_to_check.column("story_title",width=150)
    table_to_check.column("chapter_number",width=150)
    table_to_check.column("chapter_title",width=150)
    table_to_check.column("author",width=150)
    
    table_to_check.heading("#0",text="",)
    table_to_check.heading("file_type",text="File type")
    table_to_check.heading("story_title",text="Story title")
    table_to_check.heading("chapter_number",text="(Last) chapter number")
    table_to_check.heading("chapter_title",text="(Last) chapter title")
    table_to_check.heading("author",text="Author")
    
    for ind, file in enumerate(json_files):
        if set(['story_title', 'chapter_number', 'author', 'chapter_title', 'text']) == set(file.keys()):
            val = ('un-signed chapter',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])        
        elif set(['chapter_data', 'encrypted_hashed_chapter', 'public_key']) == set(file.keys()):
            val = ('signed chapter',file['chapter_data']['story_title'],file['chapter_data']['chapter_number'],file['chapter_data']['chapter_title'],file['chapter_data']['author'])
        elif set(['block_content', 'hash']) == set(file.keys()):
            if 'signed_chapter_data' in file['block_content'].keys():
                file = file['block_content']['signed_chapter_data']
                val = ('validated block (isolated)',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
            else:
                file = file['block_content']
                val = ('validated genesis block (isolated)',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
        elif all([x.isdigit() for x in file.keys()]):
            
            largest_block_nb = str(max([int(k) for k in file.keys()]))
            if largest_block_nb == '0':
                file = file['0']['block_content']
                val = ('validated genesis block',file['story_title'],file['chapter_number'], 'no title',file['author'])
            else:
                file = file[largest_block_nb]['block_content']['signed_chapter_data']['chapter_data']
                val = ('validated story',file['story_title'],file['chapter_number'],file['chapter_title'],file['author'])
        else:
            val = ('unrecognised file','no title','no number', 'no title', 'no author')
            
        table_to_check.insert(parent='',index='end',iid=ind,text='', values = val)
    
    def get_file_to_check(a):
        curItem = table_to_check.focus()
        global file_to_check
        file_to_check = file_names[int(curItem)]
    
    table_to_check.bind('<ButtonRelease-1>', get_file_to_check)
    
    table_to_check.grid(row = 1, column = 0, padx = 10, pady = 10)
    but_check_file.grid(row = 2, column = 0, padx = 10, pady = 10)

def run_checks(event):
    
    lbl_check_greeting.grid_forget()
    table_to_check.grid_forget()
    but_check_file.grid_forget()
    
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    status = check_file(file_to_check)
    result_string = result.getvalue()
    sys.stdout = old_stdout
    
    scroll_sign_messages = scrolledtext.ScrolledText()
    scroll_sign_messages.insert("1.0", result_string)
    if status == 'error':
        lbl_checked_file = tk.Label(text = 'Something is not right.\nSee the text below for a description of what happened.\nClose this window and try again.')
    else:
        lbl_checked_file = tk.Label(text = 'Your file has been checked!\nSee the text below for a description of what happened.')
        lbl_display_text = tk.Label(text = 'You can read the text contained in the file that you checked below.\nClose this window when you are finished.')
    lbl_checked_file.grid(row = 0, column = 0, sticky = 'n', padx=10, pady = 10)
    scroll_sign_messages.grid(row = 1, column = 0, sticky = 'n', padx=10)
    lbl_display_text.grid(row = 2, column = 0, sticky = 'n', padx=10)
    
    
    
    
window = tk.Tk()
lbl_greeting = tk.Label(text="What do you want to do?")
but_sign_chapter = tk.Button(text = 'Digiatlly sign a chapter')
but_mine_chapter = tk.Button(text = 'Attempt to mine a chapter')
but_check_read = tk.Button(text = 'Check a json file and read it\'s content')

# Define all the widgets to appear on the first chapter signature window
fr_form = tk.Frame()
fr_accept= tk.Frame()
text_boxes_widths = 50
lbl_sign_greeting = tk.Label(master = fr_form, text="Please fill in your chapter data here.")
lbl_story_title = tk.Label(master = fr_form, text="Story title:")
lbl_chapter_number = tk.Label(master = fr_form, text="Chapter number:")
lbl_chapter_title = tk.Label(master = fr_form, text="Chapter title:")
lbl_author_name = tk.Label(master = fr_form, text="Author name:")
lbl_chapter_text = tk.Label(master = fr_form, text="Chapter text (this window does not check for typos!):")
lbl_above_accept = tk.Label(master = fr_accept, text='Click below to digitally sign your chapter submission')
lbl_below_accept = tk.Label(master = fr_accept, text='Be careful that:\n - The story title field is correct.\n - The chapter number is correct.\n - There are no typos in you submission.',justify="left")
ent_story_title = tk.Entry(master = fr_form, width = text_boxes_widths)
ent_chapter_number = tk.Entry(master = fr_form, width = text_boxes_widths)
ent_chapter_title = tk.Entry(master = fr_form, width = text_boxes_widths)
ent_author_name = tk.Entry(master = fr_form, width = text_boxes_widths)
but_accept_entry = tk.Button(master = fr_accept, text = 'Sign it!')
# thanks https://stackoverflow.com/questions/13832720/how-to-attach-a-scrollbar-to-a-text-widget
scroll_txt = scrolledtext.ScrolledText(master = fr_form, width = text_boxes_widths, height = text_boxes_widths)

lbl_signed_chapter_data = tk.Label(text = 'Your chapter has been digitally signed!\nSee the text below for a description of what happened.\nClose this window when you are finished.')

lbl_miner_name = tk.Label(text="Enter your miner name",justify="left")
but_start_mining = tk.Button(text = 'Start mining! This will take some time. Be patient.')

lbl_greeting.grid(row = 0, column = 1)
but_sign_chapter.grid(row=1, column=0)
but_mine_chapter.grid(row=1, column=1)
but_check_read.grid(row=1, column=2)

but_sign_chapter.bind("<Button-1>", open_chapter_signature_window)
but_mine_chapter.bind("<Button-1>", open_mining_window)
but_check_read.bind("<Button-1>", open_check_window)
    
but_accept_entry.bind("<Button-1>", run_chapter_signature)

but_start_mining.bind("<Button-1>", run_mining)
table_signed_chapters = ttk.Treeview()
ent_miner_name = tk.Entry(width = 50)
var1 = tk.IntVar()
check_send_to_discord = tk.Checkbutton(text="Automatically send the validated file to the discord server", variable=var1)
lbl_chapter_choice = tk.Label(text="Select a signed chapter below. Pick the story with:\n - the right title.\n - the right chapter number.",justify="left")
table_validated_chapters = ttk.Treeview()
lbl_story_choice = tk.Label(text="Select a validated story below. Pick the story with:\n - the right title.\n - the largest number of chapters.\n - The smallest story age.",justify="left")

table_to_check = ttk.Treeview()
but_check_file = tk.Button(text = 'Check the selected file.')
but_check_file.bind("<Button-1>", run_checks)
window.mainloop()

# https://realpython.com/python-gui-tkinter/
# https://www.askpython.com/python-modules/tkinter/tkinter-text-widget-tkinter-scrollbar