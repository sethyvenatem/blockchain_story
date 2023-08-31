import tkinter as tk
import tkinter.scrolledtext as scrolledtext


def open_chapter_signature_window(event):
    
    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    lbl_sign_greeting = tk.Label(text="Please fill in your chapter data here.")
    
    lbl_story_title = tk.Label(text="Story title:")
    lbl_chapter_number = tk.Label(text="Chapter number:")
    lbl_chapter_title = tk.Label(text="Chapter title:")
    lbl_author_name = tk.Label(text="Author name:")
    lbl_chapter_text = tk.Label(text="Chapter text:")
    
    text_boxes_widths = 100
    ent_story_title = tk.Entry(width = text_boxes_widths)
    ent_chapter_number = tk.Entry(width = text_boxes_widths)
    ent_chapter_title = tk.Entry(width = text_boxes_widths)
    ent_author_name = tk.Entry(width = text_boxes_widths)
    
    lbl_sign_greeting.grid(row = 0, column = 0, sticky='w')
    lbl_story_title.grid(row = 1, column = 0, sticky='w')
    lbl_chapter_number.grid(row = 2, column = 0, sticky='w')
    lbl_chapter_title.grid(row = 3, column = 0, sticky='w')
    lbl_author_name.grid(row = 4, column = 0, sticky='w')
    lbl_chapter_text.grid(row = 5, column = 0, sticky='nw')
    
    ent_story_title.grid(row = 1, column = 1, sticky='EW', padx=10)
    ent_chapter_number.grid(row = 2, column = 1, sticky='EW', padx=10)
    ent_chapter_title.grid(row = 3, column = 1, sticky='EW', padx=10)
    ent_author_name.grid(row = 4, column = 1, sticky='EW', padx=10)

    # thanks https://stackoverflow.com/questions/13832720/how-to-attach-a-scrollbar-to-a-text-widget
    scroll_txt = scrolledtext.ScrolledText(width = text_boxes_widths, height = text_boxes_widths)
    scroll_txt.grid(row = 5, column = 1, sticky='EW', padx=10)
    
    text = scroll_txt.get("1.0", tk.END)
    
    print(text)



def open_mining_window(event):

    lbl_greeting.grid_forget()
    but_sign_chapter.grid_forget()
    but_mine_chapter.grid_forget()
    but_check_read.grid_forget()
    
    lbl_mine_greeting = tk.Label(text="Chose a chapter to mine.")
    lbl_mine_greeting.grid(row = 0, column = 1)
    
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

#lbl_greeting.pack()
#but_sign_chapter.pack(side=tk.LEFT)
#but_mine_chapter.pack(side=tk.LEFT)
#but_check_read.pack(side=tk.LEFT)
lbl_greeting.grid(row = 0, column = 1)
but_sign_chapter.grid(row=1, column=0)
but_mine_chapter.grid(row=1, column=1)
but_check_read.grid(row=1, column=2)

but_sign_chapter.bind("<Button-1>", open_chapter_signature_window)
but_mine_chapter.bind("<Button-1>", open_mining_window)
but_check_read.bind("<Button-1>", open_check_window)

window.mainloop()

# https://realpython.com/python-gui-tkinter/
# https://www.askpython.com/python-modules/tkinter/tkinter-text-widget-tkinter-scrollbar