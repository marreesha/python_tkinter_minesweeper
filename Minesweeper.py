import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
from datetime import time, date, datetime

colors = {
    1: '#1235e3',
    2: '#07b504',
    3: '#e63127',
    4: '#1005ab',
    5: '#7a1b04',
    6: '#02a88a',
    7: '#db04cd',
    8: '#d19719'
}


class MyButton(tk.Button):
    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.is_open = False
        self.is_flag = False
        self.count_bomb = 0

    def __repr__(self):
        return f'MyButton {self.x} {self.y} {self.number} {self.is_mine}'


class MineSwepper:
    window = tk.Tk()
    # default values
    ROW = 10
    COLUMNS = 10
    MINES = 15

    def __init__(self):
        self.buttons = []
        for i in range(MineSwepper.ROW + 2):
            temp = []
            for j in range(MineSwepper.COLUMNS + 2):
                btn = MyButton(MineSwepper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind('<Button-3>', self.right_click)
                temp.append(btn)
            self.buttons.append(temp)

        MineSwepper.IS_FIRST_CLICK = True
        MineSwepper.END_GAME = False
        MineSwepper.FLAG = MineSwepper.MINES
        MineSwepper.OPEN_CELLS = 0
        MineSwepper.TIME = '00:00:00'

        lbl = tk.Label(self.window, text=f'🚩 {MineSwepper.FLAG} ', font='Calibri 15 bold')
        lbl.grid(column=1, row=0, columnspan=2, padx=10, pady=10)
        lbl_time = tk.Label(self.window, text=MineSwepper.TIME, font='Calibri 15 bold')
        lbl_time.grid(row=0, column=MineSwepper.COLUMNS//2, columnspan=2)

        self.startTime = None
        self.updateTimer()

    def updateTimer(self):
        if self.startTime and not MineSwepper.END_GAME:
            delta = datetime.now() - self.startTime
            MineSwepper.TIME = str(delta).split('.')[0] # drop ms
            if delta.total_seconds() < 36000:
                MineSwepper.TIME = '0' + MineSwepper.TIME

        lbl_time = tk.Label(self.window, text=MineSwepper.TIME, font='Calibri 15 bold')
        lbl_time.grid(row=0, column=MineSwepper.COLUMNS // 2, columnspan=2)
        self.window.after(100, self.updateTimer)

    def right_click(self, event):
        cur_btn = event.widget
        if not MineSwepper.IS_FIRST_CLICK:
            if cur_btn['state'] == 'normal':
                cur_btn['state'] = 'disabled'
                cur_btn['text'] = '🚩'
                cur_btn['disabledforeground'] = '#d15508'
                MineSwepper.FLAG -= 1
                btn = self.buttons[cur_btn.x][cur_btn.y]
                btn.is_flag = True
            else:
                if cur_btn['text'] == '🚩':
                    cur_btn['state'] = 'normal'
                    cur_btn['text'] = ''
                    MineSwepper.FLAG += 1
                    btn = self.buttons[cur_btn.x][cur_btn.y]
                    btn.is_flag = False

        lbl = tk.Label(self.window, text=f'🚩 {MineSwepper.FLAG} ', font='Calibri 15 bold')
        lbl.grid(column=1, row=0, columnspan=2, padx=10, pady=10)

    def click(self, clicked_button: MyButton):
        if MineSwepper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            MineSwepper.IS_FIRST_CLICK = False
            self.startTime = datetime.now()

        if clicked_button.is_mine:
            clicked_button.config(text='💣', disabledforeground='black')
            clicked_button.is_open = True
            MineSwepper.END_GAME = True
            self.open_all_buttons()
            showinfo('Game over', 'You Lose! Play again?')
        else:
            color = colors.get(clicked_button.count_bomb, 'black')
            if clicked_button.count_bomb:
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
                MineSwepper.OPEN_CELLS += 1
            else:
                self.breadth_first_search(clicked_button)
        clicked_button.config(state='disabled')
        clicked_button.config(relief=tk.SUNKEN)

        if MineSwepper.OPEN_CELLS == MineSwepper.ROW*MineSwepper.COLUMNS - MineSwepper.MINES:
            self.open_all_buttons()
            MineSwepper.END_GAME = True
            showinfo('Game over', 'You Win! Play again?')

    def breadth_first_search(self, btn: MyButton):
        queue = [btn]
        while queue:
            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')

            if not cur_btn.is_flag:
                if cur_btn.count_bomb:
                    cur_btn.config(text=cur_btn.count_bomb, disabledforeground=color)
                else:
                    cur_btn.config(text=' ', disabledforeground=color)
                cur_btn.is_open = True
                cur_btn.config(state='disabled')
                cur_btn.config(relief=tk.SUNKEN)
                MineSwepper.OPEN_CELLS += 1

            if not cur_btn.count_bomb:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= MineSwepper.ROW and \
                                1 <= next_btn.y <= MineSwepper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

    def create_widgets(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='restart', command=self.reload)
        settings_menu.add_command(label='settings', command=self.create_settings_window)
        settings_menu.add_command(label='exit', command=self.window.destroy)
        menubar.add_cascade(label='options', menu=settings_menu)

        count = 1
        for i in range(1, MineSwepper.ROW + 1):
            for j in range(1, MineSwepper.COLUMNS + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='NWES')
                count += 1


        for i in range(1, MineSwepper.ROW + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
        for i in range(1, MineSwepper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

    def open_all_buttons(self):
        for i in range(1, MineSwepper.ROW + 1):
            for j in range(1, MineSwepper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text='💣', background='#f5b99f')
                else:
                    if btn.count_bomb > 0:
                        btn.config(text=btn.count_bomb)

                btn.config(state='disabled')

    def insert_mines(self, number: int):
        index_mines = self.get_mines_places(number)
        for i in range(1, MineSwepper.ROW + 1):
            for j in range(1, MineSwepper.COLUMNS + 1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
        for i in range(1, MineSwepper.ROW + 1):
            for j in range(1, MineSwepper.COLUMNS + 1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neigbor = self.buttons[i+row_dx][j+col_dx]
                            if neigbor.is_mine:
                                count_bomb += 1
                btn.count_bomb = count_bomb

    @staticmethod
    def get_mines_places(exclude_number: int):
        indexes = list(range(1, MineSwepper.COLUMNS * MineSwepper.ROW + 1))
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:MineSwepper.MINES]

    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.start()

    def change_settings(self, row: tk.Entry, columns: tk.Entry, mines: tk.Entry):
        try:
            int(row.get()), int(columns.get()), int(mines.get())
        except ValueError:
            showerror('Error', 'ValueError')
            return
        MineSwepper.ROW = int(row.get())
        MineSwepper.COLUMNS = int(columns.get())
        MineSwepper.MINES = int(mines.get())
        self.reload()

    def create_settings_window(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Settings')

        tk.Label(win_settings, text='Lines number').grid(row=0, column=0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0,MineSwepper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)

        tk.Label(win_settings, text='Colums number').grid(row=1, column=0)
        columns_entry = tk.Entry(win_settings)
        columns_entry.insert(0, MineSwepper.COLUMNS)
        columns_entry.grid(row=1, column=1, padx=20, pady=20)

        tk.Label(win_settings, text='Mines number').grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, MineSwepper.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)

        save_btn = tk.Button(win_settings, text='Apply',
                  command=lambda: self.change_settings(row_entry, columns_entry, mines_entry))
        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

    def start(self):
        self.create_widgets()
        MineSwepper.window.mainloop()


MineSwepper.window.title("Minesweeper")
game = MineSwepper()
game.start()

