
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Token, Transformer, v_args
import lark.exceptions

from metatree import Meta
from exceptions import CompilationException


module_path = Path(__file__).parent
grammar_path = (module_path / "xpasm.lark").resolve()

with open(grammar_path,"r") as f:
	grammar = Lark(
		f.read(),
		start="file",
		parser="lalr",
		propagate_positions=True,
		maybe_placeholders=True
		# transformer=Ast.Cleaner()
		# lark: meta args not implemented for internal transformer
	)


def generateAST(file_path:str, file: str) -> str:
	try:
		ast_lark = grammar.parse(file)
		print(ast_lark)
	except lark.exceptions.UnexpectedCharacters as e:
		#print(f"\nParserError: Unexpected character '{e.char}' at line {e.line} col {e.column}:\n\n{e._context}\n{e.}")
		print("\nLexer error: " + str(e))
		return
	except lark.exceptions.UnexpectedToken as e:
		print(f"Parser error: {e}\n{e.get_context(file, 100)}")
		print(e._terminals_by_name)
		print(e.considered_rules)
		exit()

	print(ast_lark.pretty())
	
	cleaner = Cleaner()
	cleaner.path = file_path
	cleaner.lines = file.splitlines()
	ast:File = cleaner.transform(ast_lark)
	print(ast.dump())

	return ast

	# TODO: collect all compilation errors in a list, and then
	# print them all at once, instead of stopping in the first
	# error found. This can only be done for TYPECHECKING, for
	# syntax/lexical errors, one can't keep on analyzing if
	# there is a single error.

	# TODO: implement validator: 
	# Duplicate Names
	# Used Undefined Names
	# Type Checker

	# generate dictionary
	#generator = Generator()
	#ast = generator.transform(ast)
	#print(ast)

	#print(f"\nGenerated:\n{dict}")
	#print(json.dumps(dict, indent=2))
	return ast

@dataclass
class Node():
	meta:Meta

	def __eq__(self, __value: object) -> bool:
		return type(self) == type(__value)

	def dump(self, indent:str = ""):
		indent_char = "  "

		def valueToStr(value, indent):
			s = ""
			if isinstance(value, String) or isinstance(value, Char):
				s += "\n" + indent + value.__class__.__name__ + "\t" + str(value.value.encode())
			elif isinstance(value, Node):
				s += value.dump(indent)
			elif isinstance(value, tuple) or isinstance(value, list):
				for val in value:
					s += valueToStr(val, indent)
			else:
				s += "\t" + str(value)
			return s
			
		s = "\n" + indent + self.__class__.__name__
		for key in self.__dict__:
			if key != 'meta' and key != 'reference':
				value = self.__getattribute__(key)
				s += valueToStr(value, indent + indent_char)
		return s
	
	def traverse(self, f, topdown=True):
		if topdown:
			f(self)
		
		if isinstance(self, File):
			self.export.traverse(f, topdown)
			for i in self.imports:
				i.traverse(f, topdown)
			for s in self.statements:
				s.traverse(f, topdown)
		elif isinstance(self, SExport):
			for s in self.signatures:
				s.traverse(f, topdown)
		elif isinstance(self, SImport):
			self.name.traverse(f, topdown)
			if self.rename:
				self.rename.traverse(f, topdown)
			for s in self.signatures:
				s.traverse(f, topdown)
		
		elif isinstance(self, SEmpty): pass
		elif isinstance(self, SProg):
			self.signature.traverse(f, topdown)
			self.exp.traverse(f, topdown)
		elif isinstance(self, SBiop):
			self.sig1.traverse(f, topdown)
			self.sig2.traverse(f, topdown)
			self.ret.traverse(f, topdown)
			self.exp.traverse(f, topdown)
		elif isinstance(self, SType):
			self.name.traverse(f, topdown)
			self.type.traverse(f, topdown)
		elif isinstance(self, SEnum):
			self.name.traverse(f, topdown)
			for e in self.elems:
				e.traverse(f, topdown)
		elif isinstance(self, EnumElem):
			self.name.traverse(f, topdown)
			if self.exp:
				self.exp.traverse(f, topdown)

		elif isinstance(self, TAddr):
			self.type.traverse(f, topdown)
		elif isinstance(self, TAlias):
			self.name.traverse(f, topdown)
		elif isinstance(self, TVoid): pass
		elif isinstance(self, TSized):
			self.size.traverse(f, topdown)
		elif isinstance(self, TUnion):
			self.t1.traverse(f, topdown)
			self.t2.traverse(f, topdown)
		elif isinstance(self, TFunc):
			self.parameter.traverse(f, topdown)
			self.ret.traverse(f, topdown)
		elif isinstance(self, TNamedFunc):
			self.parameter.traverse(f, topdown)
			self.ret.traverse(f, topdown)
		elif isinstance(self, TStruct):
			for m in self.members:
				m.traverse(f, topdown)
		
		elif isinstance(self, Signature):
			self.name.traverse(f, topdown)
			self.type.traverse(f, topdown)
		
		elif isinstance(self, SWrite):
			self.address.traverse(f, topdown)
			self.value.traverse(f, topdown)
		elif isinstance(self, SIgnore):
			self.exp.traverse(f, topdown)
		elif isinstance(self, SWhile):
			self.condition.traverse(f, topdown)
			self.body.traverse(f, topdown)
		elif isinstance(self, SDo):
			self.condition.traverse(f, topdown)
			self.body.traverse(f, topdown)
		elif isinstance(self, SReturn):
			if self.value:
				self.value.traverse(f, topdown)
		elif isinstance(self, SContinue): pass
		elif isinstance(self, SBreak): pass

		elif isinstance(self, EApp):
			self.func.traverse(f, topdown)
			self.arg.traverse(f, topdown)
		elif isinstance(self, EBlock):
			for s in self.statements:
				s.traverse(f, topdown)
		elif isinstance(self, EPipe):
			self.input.traverse(f, topdown)
			self.output.traverse(f, topdown)
		elif isinstance(self, ELambda):
			self.type.traverse(f, topdown)
			self.body.traverse(f, topdown)
		elif isinstance(self, EMember):
			self.parent.traverse(f, topdown)
			self.member.traverse(f, topdown)
		elif isinstance(self, ERead):
			self.address.traverse(f, topdown)
		elif isinstance(self, EIf):
			self.condition.traverse(f, topdown)
			self.exp1.traverse(f, topdown)
			self.exp2.traverse(f, topdown)
		elif isinstance(self, EArray):
			for e in self.elements:
				e.traverse(f, topdown)

		elif isinstance(self, Integer): pass
		elif isinstance(self, Name): pass
		elif isinstance(self, Char): pass
		elif isinstance(self, String): pass
		else:
			raise CompilationException(
				"Undefined AST node class for Ast.traverse named: " + self.__class__.__name__
			)

		if not topdown:
			f(self)


@dataclass
class Type(Node): pass

@dataclass
class Stmt(Node): pass

@dataclass
class Exp(Node): pass

@dataclass
class Terminal(Exp): pass

@dataclass
class String(Terminal):
	value:str

@dataclass
class Char(Terminal):
	value:str

@dataclass
class Name(Terminal):
	value:str

@dataclass
class Integer(Terminal):
	value:int

@dataclass
class EArray(Exp):
	elements:list[Exp]

@dataclass
class EIf(Exp):
	condition:Exp
	etrue:Exp
	efalse:Exp

@dataclass
class ERead(Exp):
	address:Exp

@dataclass
class EMember(Exp):
	parent:Node
	member:Name

@dataclass
class ELambda(Exp):
	type:Type
	body:Exp

@dataclass
class EPipe(Exp):
	input:Exp
	output:Exp

@dataclass
class EBlock(Exp):
	statements:list[Stmt]|tuple[Stmt]

@dataclass
class EApp(Exp):
	func:Exp
	arg:Exp

@dataclass
class SBreak(Stmt): pass

@dataclass
class SContinue(Stmt): pass

@dataclass
class SReturn(Stmt):
	value:Exp|None

@dataclass
class SDo(Stmt):
	condition:Exp
	body:Exp

@dataclass
class SWhile(Stmt):
	condition:Exp
	body:Exp

@dataclass
class SIgnore(Stmt):
	exp:Exp

@dataclass
class SWrite(Stmt):
	address:Exp
	value:Exp


@dataclass
class Signature(Node):
	name:Name
	type:Type


@dataclass
class TStruct(Type):
	members:list[Signature]
	def __eq__(self, __value: object) -> bool:
		if not super().__eq__(__value):
			return False
		if len(self.members) != len(__value.members):
			return False
		m1:Signature
		m2:Signature
		for m1, m2 in zip(self.members, __value.members):
			if m1.type != m2.type:
				return False
		return True

@dataclass
class TNamedFunc(Type):
	parameter:Signature
	ret:Type

@dataclass
class TFunc(Type):
	parameter:Type
	ret:Type

@dataclass
class TUnion(Type):
	t1:Type
	t2:Type

@dataclass
class TSized(Type):
	size:Integer

@dataclass
class TVoid(Type): pass

@dataclass
class TAlias(Type):
	name:Name

@dataclass
class TAddr(Type):
	type:Type


@dataclass
class EnumElem(Node):
	name:Name
	exp:Integer|None
	value:int = 0

@dataclass
class SEnum(Stmt):
	name:Name
	elems:list[EnumElem]
	def __init__(self, meta:Meta, name:Name, elems:list[EnumElem]):
		self.meta = meta
		self.name = name

		previous_value:int = 0
		for elem in elems:
			if elem.exp:
				previous_value = elem.exp.value
			elem.value = previous_value
			previous_value += 1 if previous_value >= 0 else -1
		self.elems = elems

@dataclass
class SType(Stmt):
	name:Name
	type:Type

@dataclass
class SBiop(Stmt):
	sig1:Signature
	sig2:Signature
	ret:Type
	exp:Exp

@dataclass
class SProg(Stmt):
	signature:Signature
	exp:Exp

@dataclass
class SEmpty(Stmt): pass


@dataclass
class SImport(Node):
	name:Name
	rename:Name|None
	signatures:list[Signature]

@dataclass
class SExport(Node):
	signatures:list[Signature]

@dataclass
class File(Node):
	export:SExport
	imports:list[SImport]
	statements:list[Node]



# Transforms lark tree, into object tree
@v_args(inline=True, meta=True)
class Cleaner(Transformer):
	path:str = ""
	lines:list[str] = []

	def obj(self, meta):
		return Meta(meta, lines=self.lines, path=self.path)
		
	# start of file
	def file(self, meta, export, imports, *statements):
		return File(self.obj(meta), export, imports, statements)

	# exports/imports
	def s_export(self, meta, *signatures):
		return SExport(self.obj(meta), signatures)
	
	def s_import(self, meta, name, rename, *signatures):
		return SImport(self.obj(meta), name, rename, signatures)
	
	# global statements
	def s_empty(self, meta):
		return SEmpty(self.obj(meta))
	
	def s_prog(self, meta, signature, exp):
		return SProg(self.obj(meta), signature, exp)

	def s_biop(self, meta, sig1, sig2, type, exp):
		return SBiop(self.obj(meta), sig1, sig2, type, exp)

	def s_type(self, meta, name, type):
		return SType(self.obj(meta), name, type)
	
	def s_enum(self, meta, name, *elements):
		return SEnum(self.obj(meta), name, elements)
	
	def enum_elem(self, meta, name, value):
		return EnumElem(self.obj(meta), name, value)

	#types
	def t_addr(self, meta, type):
		TAddr(self.obj(meta), type)
	
	def t_alias(self, meta, name):
		return TAlias(self.obj(meta), name)
	
	def t_sized(self, meta, size:Integer):
		if size.value == 0:
			return TVoid(self.obj(meta))
		else:
			return TSized(self.obj(meta), size)
	
	def t_union(self, meta, t1, t2):
		return TUnion(self.obj(meta), t1, t2)

	def t_func(self, meta, param, ret):
		return TFunc(self.obj(meta), param, ret)
	
	def t_named_func(self, meta, param, ret):
		return TNamedFunc(self.obj(meta), param, ret)
	
	def t_struct(self, meta, *members):
		return TStruct(self.obj(meta), members)
	
	# signature
	def signature(self, meta, name, type):
		return Signature(self.obj(meta), name, type)
	
	# attributes
	
	# statements
	def s_write(self, meta, address, value):
		return SWrite(self.obj(meta), address, value)
	
	def s_ignore(self, meta, exp):
		return SIgnore(self.obj(meta), exp)
	
	def s_while(self, meta, cond, body):
		return SWhile(self.obj(meta), cond, body)
	
	def s_do(self, meta, cond, body):
		return SDo(self.obj(meta), cond, body)
	
	def s_ret(self, meta, exp):
		return SReturn(self.obj(meta), exp)
	
	def s_continue(self, meta):
		return SContinue(self.obj(meta))
	
	def s_break(self, meta):
		return SBreak(self.obj(meta))
	
	# expressions
	def e_app(self, meta, func, arg):
		return EApp(self.obj(meta), func, arg)

	def e_block(self, meta, *statements):
		return EBlock(self.obj(meta), statements)
	
	def e_pipe(self, meta, input, output):
		return EPipe(self.obj(meta), input, output)
	
	def e_lambda(self, meta, type, body):
		return ELambda(self.obj(meta), type, body)
	
	def e_member(self, meta, parent, member):
		return EMember(self.obj(meta), parent, member)

	def e_read(self, meta, exp):
		return ERead(self.obj(meta), exp)
	
	def e_if(self, meta, cond, e_true, e_false):
		return EIf(self.obj(meta), cond, e_true, e_false)
	
	def e_array(self, meta, *data_list):
		return EArray(self.obj(meta), data_list)

	# terminals
	def DECIMAL(self, tkn):
		value = int(tkn.value)
		return Integer(self.obj(tkn), value)
	
	def HEX(self, tkn):
		value = int(tkn.value.replace("0x", ""), 16)
		return Integer(self.obj(tkn), value)
	
	def BIN(self, tkn):
		value = int(tkn.value.replace("0b", ""), 2)
		return Integer(self.obj(tkn), value)
	
	def NAME(self, tkn:Token):
		return Name(self.obj(tkn), tkn.value)
	
	def SYMBOL(self, tkn:Token):
		return Name(self.obj(tkn), tkn.value)
	
	def STRING(self, tkn:Token):
		v = bytes(tkn.value[1:-1], "utf-8").decode("unicode_escape")
		return String(self.obj(tkn), v)

	def CHAR(self, tkn:Token):
		v = bytes(tkn.value[1:-1], "utf-8").decode("unicode_escape")
		return Char(self.obj(tkn), v)
	

