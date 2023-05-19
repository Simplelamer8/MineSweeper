import tkinter as tk 
from random import shuffle
from tkinter.messagebox import showinfo, showerror
import winsound

colors = {
	1: 'blue',
	2: 'green',
	3: 'red',
	4: 'violet',
}

class MyButton (tk.Button):



	def __init__(self, master, x, y, number = 0, *args, **kwargs):
		super(MyButton, self).__init__(master, *args, **kwargs)
		self.x = x
		self.y = y 
		self.is_mine = False
		self.number = number
		self.count_bomb = 0
		self.is_open = False

	def __repr__(self):
		return 'MyButton'


class MineSweeper:
	window = tk.Tk()
	ROW = 8
	COLUMNS = 8
	MINES = 8
	Clicked_buttons = 0
	WON = False
	GAME_OVER = False
	FIRST_CLICK = True

	def __init__(self):
		self.flag_count = 0
		self.buttons = []
		for i in range(MineSweeper.ROW + 2):
			temp = []
			for j in range(MineSweeper.COLUMNS + 2):
				btn = MyButton(MineSweeper.window, x = i, y = j, width = 3, font = 'Calibri 15 bold')
				btn.config(command=lambda button = btn: self.click(button))
				btn.bind('<Button-3>', self.right_click)
				temp.append(btn)
			self.buttons.append(temp)

	def right_click(self, event):
		if MineSweeper.WON:
			return
		if MineSweeper.GAME_OVER:
			return
		cur_btn = event.widget
		if cur_btn['state'] == 'normal' and self.flag_count >= self.MINES:
			showinfo('Warning', 'The number of flags is exceeding the number of mines!')
		if cur_btn['state'] == 'normal':
			cur_btn['state'] = 'disabled'
			cur_btn['text'] = '🚩'
			self.flag_count += 1
		elif cur_btn['text'] == '🚩':
			cur_btn['text'] = ''
			cur_btn['state'] = 'normal'
			self.flag_count -= 1

	def click(self, clicked_btn:MyButton):

		if MineSweeper.WON:
			return

		if MineSweeper.GAME_OVER:
			return

		if MineSweeper.FIRST_CLICK:
			self.insert_mines(clicked_btn.number)
			self.mine_neighbours()
			self.print_buttons()
			MineSweeper.FIRST_CLICK = False


		print(clicked_btn)
		if clicked_btn.is_mine:
			clicked_btn.config(text = "*", background="red", disabledforeground = "black")
			clicked_btn.is_open = True
			MineSweeper.GAME_OVER = True
			winsound.PlaySound("Explosion.wav", 0)
			showinfo('GAME OVER', 'You lose!')
			for i in range (1, MineSweeper.ROW + 1):
				for j in range (1, MineSweeper.COLUMNS + 1):
					btn = self.buttons[i][j]
					if btn.is_mine:
						btn['text'] = '*'
		else:
			if clicked_btn.count_bomb:
				if self.ROW * self.COLUMNS - self.MINES < self.Clicked_buttons + 1:
					self.WON = True
					winsound.PlaySound("WON.wav", 0)
					showinfo("Congratulations!!!", 'You win!!!')
					for i in range (1, MineSweeper.ROW + 1):
						for j in range (1, MineSweeper.COLUMNS + 1):
							btn = self.buttons[i][j]
							if btn.is_mine:
								btn['text'] = '*'
								btn.config(state=tk.DISABLED)
				clicked_btn.is_open = True
				color = colors.get(clicked_btn.count_bomb, 'black')
				clicked_btn.config(text = clicked_btn.count_bomb, disabledforeground = color)
			else:
				self.breadth_first_search(clicked_btn)
		clicked_btn.config(state = 'disabled')
		clicked_btn.config(relief = tk.SUNKEN)
		self.Clicked_buttons += 1

	def breadth_first_search(self, btn: MyButton):
		queue = [btn]
		while queue:
			self.Clicked_buttons += 1
			cur_btn = queue.pop()
			color = colors.get(cur_btn.count_bomb, 'black')
			if cur_btn.cget('state') != 'normal':
				self.flag_count -= 1;
			if cur_btn.count_bomb:
				cur_btn.config(text = cur_btn.count_bomb, disabledforeground = color)
			else:
				cur_btn.config(text = '', disabledforeground = color)
			cur_btn.is_open = True
			cur_btn.config(state = 'disabled')
			cur_btn.config(relief = tk.SUNKEN)

			if cur_btn.count_bomb == 0:
				x, y = cur_btn.x, cur_btn.y
				for ineighbour in [-1, 0, 1]:
					for jneighbour in [-1, 0, 1]:
						next_btn = self.buttons[x + ineighbour][y + jneighbour]
						if not next_btn.is_open and 1 <= next_btn.x <= MineSweeper.ROW and \
						 1 <= next_btn.y <= MineSweeper.COLUMNS and next_btn not in queue:
							queue.append(next_btn)

	def reload(self):
		MineSweeper.flag_count = 0
		[child.destroy() for child in self.window.winfo_children()]
		self.__init__()
		self.create_buttons()
		MineSweeper.FIRST_CLICK = True
		MineSweeper.GAME_OVER = False
		MineSweeper.WON = False

	def create_settings(self):
		win_settings = tk.Toplevel(self.window)
		win_settings.wm_title('Settings')
		tk.Label(win_settings, text = 'Number of rows').grid(row = 0, column = 0)
		row_entry = tk.Entry(win_settings)
		row_entry.insert(0, MineSweeper.ROW)
		row_entry.grid(row = 0, column = 1, padx = 20, pady = 20)
		tk.Label(win_settings, text = 'Number of columns').grid(row = 1, column = 0)
		column_entry = tk.Entry(win_settings)
		column_entry.insert(0, MineSweeper.COLUMNS)
		column_entry.grid(row = 1, column = 1, padx = 20, pady = 20)
		tk.Label(win_settings, text = 'Number of mines').grid(row = 2, column = 0)
		mines_entry = tk.Entry(win_settings)
		mines_entry.insert(0, MineSweeper.MINES)
		mines_entry.grid(row = 2, column = 1, padx = 20, pady = 20)
		save_btn = tk.Button(win_settings, text = 'Save', command = lambda:self.change_settings(row_entry, column_entry, mines_entry))
		save_btn.grid(row = 3, column = 0, columnspan = 2, padx = 20, pady = 20)

	def change_settings(self, row:tk.Entry, column:tk.Entry, mines:tk.Entry):
		try: 
			int(row.get()), int(column.get()), int(mines.get())
		except ValueError:
			showerror('Error!', 'You have entered wrong values!')
			return
		MineSweeper.ROW = int(row.get())
		MineSweeper.COLUMNS = int(column.get())
		MineSweeper.MINES = int(mines.get())
		self.reload()

	def display_number_of_flags(self):
		self.canvas.itemconfigure(self.text, text = f'Number of flags: {self.flag_count}')
		

	def create_buttons(self):
		menubar = tk.Menu(self.window)
		self.window.config(menu = menubar)
		submenu = tk.Menu(menubar, tearoff=0)
		submenu.add_command(label='Replay', command = self.reload)
		submenu.add_command(label='Settings', command = self.create_settings)
		submenu.add_command(label='Exit', command=self.window.destroy)
		menubar.add_cascade(label='File', menu=submenu)

		count = 1
		for i in range(1, MineSweeper.ROW + 1):
			for j in range(1, self.COLUMNS + 1):
				btn = self.buttons[i][j]
				btn.number = count
				btn.grid(row = i, column = j, stick='NWES')
				count += 1

		for i in range(1, MineSweeper.ROW + 1):
			tk.Grid.rowconfigure(self.window, i, weight = 1)

		for j in range(1, MineSweeper.COLUMNS + 1):
			tk.Grid.columnconfigure(self.window, j, weight = 1)



	def start(self):
		self.create_buttons()
		MineSweeper.window.mainloop()

	def print_buttons(self):
		for i in range (1, MineSweeper.ROW + 1):
			for j in range (1, MineSweeper.COLUMNS + 1):
				btn = self.buttons[i][j]
				if btn.is_mine:
					print('B', end = '')
				else:
					print(btn.count_bomb, end = '')
			print()

	def mine_neighbours (self):
		for i in range(1, MineSweeper.ROW + 1):
			for j in range(1, MineSweeper.COLUMNS + 1):
				btn = self.buttons[i][j]
				count_bomb = 0
				if not btn.is_mine:
					for ineighbour in [-1, 0, 1]:
						for jneighbour in [-1, 0, 1]:
							neighbour = self.buttons[i + ineighbour][j + jneighbour]
							if neighbour.is_mine:
								count_bomb += 1
				btn.count_bomb = count_bomb

	def mines_places(self, exclude_number:int):
		indexes = list(range(1, MineSweeper.COLUMNS * MineSweeper.ROW + 1))
		indexes.remove(exclude_number)
		shuffle(indexes)
		return indexes[:MineSweeper.MINES]

	def insert_mines(self, number:int):
		index_mines = self.mines_places(number)
		for i in range (1, MineSweeper.ROW + 1):
			for j in range (1, MineSweeper.COLUMNS + 1):
				btn = self.buttons[i][j]
				if btn.number in index_mines:
					btn.is_mine = True


game = MineSweeper()
game.start()