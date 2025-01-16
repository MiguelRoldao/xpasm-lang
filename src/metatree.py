
from lark import Token
from lark.tree import Meta as LarkMeta


class Meta():
	line:int
	column:int
	start_pos:int
	end_line:int
	end_column:int
	end_pos:int
	lines:list[str]
	path:str
	def __init__(self, line=1, column=1, start_pos=0, end_line=1, end_column=1, end_pos=0, lines="", path="") -> None:
		if isinstance(line, LarkMeta) or isinstance(line, Token):
			self.line = line.line
			self.column = line.column
			self.start_pos = line.start_pos
			self.end_line = line.end_line
			self.end_column = line.end_column
			self.end_pos = line.end_pos
			self.lines = lines
			self.path = path
		else:
			self.line = line
			self.column = column
			self.start_pos = start_pos
			self.end_line = end_line
			self.end_column = end_column
			self.end_pos = end_pos
			self.lines = lines
			self.path = path