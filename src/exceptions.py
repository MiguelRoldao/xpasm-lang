
from metatree import Meta


class CompilationException(Exception):...

def getCodeSnippet(file_lines:list[str], start_line:int, end_line:int) -> str:
	s = ""
	n_digits = len("%i" % end_line)
	for i in range(start_line-1, end_line):
		s += f"\t{(i+1):{n_digits}d} | {file_lines[i]}\n"
	return s

def getCodeSnippetWithCursor(file_lines:list[str], line:int, column:int) -> str:
	s = getCodeSnippet(file_lines, line, line)
	offset = len("%i" % line) + 3 + column
	cursor = ""
	for i in range(offset):
		if s[i] == '\t':
			cursor += '\t'
		else:
			cursor += ' '
	s += cursor + "^\n"
	return s


class OneSnippetException(CompilationException):
	def __init__(self, title:str, meta:Meta=None) -> None:
		self.title = title
		self.meta = meta
		self.code = getCodeSnippetWithCursor(meta.lines, meta.line, meta.column)

	def __str__(self) -> str:
		s = self.title + ".\n"
		s += f"In file \"{self.meta.path}\", line {self.meta.line}, column {self.meta.column}:\n{self.code}"
		return s

class TwoSnippetsException(CompilationException):
	def __init__(self, title:str, meta1:Meta, meta2:Meta) -> None:
		self.title = title
		self.meta1 = meta1
		self.meta2 = meta2
		self.code1 = getCodeSnippetWithCursor(meta1.lines, meta1.line, meta1.column)
		self.code2 = getCodeSnippetWithCursor(meta2.lines, meta2.line, meta2.column)

	def __str__(self) -> str:
		s = self.title + ".\n"
		s += f"In file \"{self.meta1.path}\", line {self.meta1.line}, column {self.meta1.column}:\n{self.code1}"
		s += f"In file \"{self.meta2.path}\", line {self.meta2.line}, column {self.meta2.column}:\n{self.code2}"
		return s
	