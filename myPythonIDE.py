from tkinter import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter.messagebox import askyesno
import subprocess
import sys
import keyword
import re
import threading

compiler = Tk()
compiler.title('Python IDE for Competitive Programming')
file_path = ''

# Dark color scheme
background_color = '#2b2b2b'
text_color = '#ffffff'
highlight_color = '#404040'

# Syntax highlighting patterns and colors
syntax_highlighting = {
    'keywords': keyword.kwlist,
    'strings': ['"', "'", '"""', "'''"],
    'comments': ['#'],
    'numbers': r'\b\d+(\.\d+)?\b',
}
syntax_colors = {
    'keywords': '#ff9d00',
    'strings': '#abe338',
    'comments': '#808080',
    'numbers': '#eda756',
}

# Undo stack
undo_stack = []

def set_file_path(path):
    global file_path
    file_path = path

def open_file():
    if check_unsaved_changes():
        return
    path = askopenfilename(filetypes=[('Python Files', '*.py')])
    if path:
        with open(path, 'r') as file:
            code = file.read()
            editor.delete('1.0', END)
            editor.insert('1.0', code)
            set_file_path(path)

def save_file():
    if file_path == '':
        path = asksaveasfilename(filetypes=[('Python Files', '*.py')])
    else:
        path = file_path
    if path:
        with open(path, 'w') as file:
            code = editor.get('1.0', END)
            file.write(code)
            set_file_path(path)

def check_unsaved_changes():
    if editor.edit_modified():
        save_prompt = askyesno('Unsaved Changes', 'Do you want to save the changes before proceeding?')
        if save_prompt:
            save_file()
        else:
            return True
    return False

def run():
    if check_unsaved_changes():
        return
    if file_path == '':
        error_prompt = Toplevel(compiler)
        text = Label(error_prompt, text='Please save your code')
        text.pack()
        return

    command = [sys.executable, file_path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    code_output.delete('1.0', END)
    code_output.insert('1.0', output.decode())
    code_output.insert('1.0', error.decode())

def clear_output():
    code_output.delete('1.0', END)

def debug():
    if check_unsaved_changes():
        return
    if file_path == '':
        error_prompt = Toplevel(compiler)
        text = Label(error_prompt, text='Please save your code')
        text.pack()
        return

    def run_debug():
        command = [sys.executable, '-m', 'pdb', file_path]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate(input=b'continue\n')
        code_output.delete('1.0', END)
        code_output.insert('1.0', output.decode())
        code_output.insert('1.0', error.decode())

    # Run the debugging process in a separate thread to prevent freezing the GUI
    threading.Thread(target=run_debug).start()

def undo():
    if undo_stack:
        text = undo_stack.pop()
        editor.delete('1.0', END)
        editor.insert('1.0', text)

def exit_app():
    if check_unsaved_changes():
        return
    compiler.quit()


# Configure theme colors
compiler.configure(bg=background_color)
compiler.option_add('*background', background_color)
compiler.option_add('*foreground', text_color)
compiler.option_add('*highlightBackground', highlight_color)
compiler.option_add('*highlightColor', text_color)

# Create menu bar
menu_bar = Menu(compiler)

# File menu
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label='Open', command=open_file)
file_menu.add_command(label='Save', command=save_file)
file_menu.add_command(label='Save As', command=save_file)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=exit_app)
menu_bar.add_cascade(label='File', menu=file_menu)

# Run menu
run_menu = Menu(menu_bar, tearoff=0)
run_menu.add_command(label='Run', command=run)
run_menu.add_command(label='Debug', command=debug)
run_menu.add_command(label='Clear Output', command=clear_output)
menu_bar.add_cascade(label='Run', menu=run_menu)

# Edit menu
edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label='Undo', command=undo)
menu_bar.add_cascade(label='Edit', menu=edit_menu)

# Set menu bar
compiler.config(menu=menu_bar)

# Editor
editor = Text(compiler, bg=background_color, fg=text_color, undo=True)
editor.pack(fill=BOTH, expand=True)

# Code output
code_output = Text(compiler, height=10, bg=background_color, fg=text_color)
code_output.pack(fill=BOTH, expand=True)

# Terminal interface for debugging
debug_terminal = Text(compiler, height=5, bg=background_color, fg=text_color)
debug_terminal.pack(fill=BOTH, expand=True)

# Scrollbars for editor and code output
scrollbar = Scrollbar(compiler)
scrollbar.pack(side=RIGHT, fill=Y)
editor.config(yscrollcommand=scrollbar.set)
code_output.config(yscrollcommand=scrollbar.set)
debug_terminal.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lambda *args: scroll(*args))

# Function to handle scrollbar scrolling
def scroll(*args):
    editor.yview(*args)
    code_output.yview(*args)
    debug_terminal.yview(*args)

# Configure editor font and appearance
editor.config(font=('Courier', 12))
editor.tag_configure('keyword', foreground=syntax_colors['keywords'])
editor.tag_configure('string', foreground=syntax_colors['strings'])
editor.tag_configure('comment', foreground=syntax_colors['comments'])
editor.tag_configure('number', foreground=syntax_colors['numbers'])

# Syntax highlighting function
def highlight_syntax(event=None):
    editor.tag_remove('keyword', '1.0', END)
    editor.tag_remove('string', '1.0', END)
    editor.tag_remove('comment', '1.0', END)
    editor.tag_remove('number', '1.0', END)

    for pattern, tags in syntax_highlighting.items():
        for tag in tags:
            start = '1.0'
            end = 'end'
            editor.tag_remove(pattern, start, end)
            while True:
                start = editor.search(tag, start, END, nocase=1, stopindex='end')
                if not start:
                    break
                end = f'{start}+{len(tag)}c'
                editor.tag_add(pattern, start, end)

    # Highlight numbers
        for match in re.finditer(r'\b\d+(\.\d+)?\b', editor.get('1.0', 'end')):
            start = '1.0' + f'+{match.start()}c'
            end = '1.0' + f'+{match.end()}c'
            editor.tag_add('number', start, end)

# Bind syntax highlighting to editor changes
editor.bind('<<Modified>>', highlight_syntax)

# Bind keyboard shortcuts
compiler.bind('<Control-o>', lambda event: open_file())
compiler.bind('<Control-s>', lambda event: save_file())
compiler.bind('<Control-r>', lambda event: run())
compiler.bind('<Control-d>', lambda event: debug())
compiler.bind('<Control-z>', lambda event: undo())
compiler.bind('<Control-e>', lambda event: exit_app())

# Set initial syntax highlighting
highlight_syntax()

compiler.mainloop()

