import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import json
import os

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
    
    os.system('python3 chapter_signature.py temp_chapter_data.json > temp_chapter_signature.txt')
    
    
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
    
    with open('temp_chapter_signature.txt') as file:
        print_statements = file.readlines()
    
    scroll_sign_messages = scrolledtext.ScrolledText()
    for p in print_statements:
        scroll_sign_messages.insert("1.0", p+'\n')
    lbl_signed_chapter_data.grid(row = 0, column = 0,sticky = 'n', padx=10)
    scroll_sign_messages.grid(row = 1, column = 0,sticky = 'n', padx=10)
    os.remove('temp_chapter_signature.txt')
    os.remove('temp_chapter_data.json')
    
def open_mining_window(event):

    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    lbl_mine_greeting = tk.Label(text="Chose a chapter to mine.")
    lbl_mine_greeting.grid(row = 0, column = 1)
    
    json_files = glob.glob('*.json')
    signed_chapters = sorted([f for f in json_files if f.startswith('signed_')])
    validated_stories = sorted([f for f in json_files if not(f.startswith('signed_')) and not(f.startswith('keys_'))])
    #https://www.geeksforgeeks.org/how-to-get-selected-value-from-listbox-in-tkinter/
    
def open_check_window(event):

    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    lbl_check_greeting = tk.Label(text="Select a file to check and view.")
    lbl_check_greeting.grid(row = 0, column = 1)

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

lbl_signed_chapter_data = tk.Label(text = 'If everything went well, your chapter has been digitally signed!\nSee the text below for a description of what happened.\nClose this window when you are finished.')

lbl_greeting.grid(row = 0, column = 1)
but_sign_chapter.grid(row=1, column=0)
but_mine_chapter.grid(row=1, column=1)
but_check_read.grid(row=1, column=2)

but_sign_chapter.bind("<Button-1>", open_chapter_signature_window)
but_mine_chapter.bind("<Button-1>", open_mining_window)
but_check_read.bind("<Button-1>", open_check_window)
    
but_accept_entry.bind("<Button-1>", run_chapter_signature)

window.mainloop()

# https://realpython.com/python-gui-tkinter/
# https://www.askpython.com/python-modules/tkinter/tkinter-text-widget-tkinter-scrollbar