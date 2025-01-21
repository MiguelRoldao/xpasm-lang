
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
	print(ast_lark)
	
	cleaner = Cleaner()
	cleaner.path = file_path
	cleaner.lines = file.splitlines()
	ast:File = cleaner.transform(ast_lark)
	print(ast.json())
	print("This was ast.json()")

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
	
	def json(self, dump_meta:bool=False, indent:str = ""):
		indent_char = "  "

		def objToJson(obj, indent):
			if isinstance(obj, String) or isinstance(obj, Char):
				return f'"str(obj.value.encode())"'
			elif isinstance(obj, Node):
				return obj.json(dump_meta, indent)
			elif isinstance(value, tuple) or isinstance(value, list):
				if (len(value) == 0):
					return '[]'
				s = f'[\n{indent+indent_char}'
				for elem in value:
					a = objToJson(elem, indent+indent_char)
					s += f'{a},\n'
				return f'{s[:-2]}\n{indent}]'
			elif isinstance(value, int):
				return f'{value}'
			elif value == None:
				return 'null'
			else:
				return f'"{value}"'

		indented = indent + indent_char
		s = f'{{\n{indented}"class": "{self.__class__.__name__}",\n'
		for key in self.__dict__:
			if (key != 'meta' or dump_meta) and key != 'reference':
				value = self.__getattribute__(key)
				a = objToJson(value, indented)
				s += f'{indented}"{key}": {a},\n'
		return f'{s[:-2]}\n{indent}}}'
	
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

# Dataclasses for building the AST
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
class Symbol(Terminal):
	value:str

@dataclass
class Integer(Terminal):
	value:int

@dataclass
class EAt(Exp):
	addr:Exp

@dataclass
class EAddr(Exp):
	obj:Exp

@dataclass
class EArray(Exp):
	elements:list[Exp]

@dataclass
class ERecep(Exp): pass

@dataclass
class EIf(Exp):
	condition:Exp
	etrue:Exp
	efalse:Exp

@dataclass
class EMember(Exp):
	name:Name
	child:Node

@dataclass
class Block(Node):
	statements:list[Stmt]

@dataclass
class ELambda(Exp):
	type:Type|None
	block:Block

@dataclass
class ECall(Exp):
	func:Name|EMember
	args:list[Exp]

@dataclass
class EPrefix(Exp):
	id:Symbol
	arg:Exp

@dataclass
class ESuffix(Exp):
	id:Symbol
	arg:Exp

@dataclass
class EInfix(Exp):
	id:Symbol
	arg1:Exp
	arg2:Exp

@dataclass
class EIndex(Exp):
	obj:Exp
	index:Exp

@dataclass
class EAssign(Exp):
	obj:Exp
	value:Exp

@dataclass
class EPipe(Exp):
	obj:Exp
	value:Exp

@dataclass
class SBreak(Stmt): pass

@dataclass
class SCont(Stmt): pass

@dataclass
class SRet(Stmt):
	value:Exp|None

@dataclass
class STail(Stmt):
	call:ECall

@dataclass
class SDo(Stmt):
	condition:Exp
	block:Block

@dataclass
class SWhile(Stmt):
	condition:Exp
	block:Block

@dataclass
class SIf(Stmt):
	condition:Exp
	if_block:Block
	else_block:Block

@dataclass
class SComp(Stmt):
	exp:Exp

@dataclass
class Signature(Node):
	name:Name|Symbol
	attr:Name|None
	type:Type

@dataclass
class TArray(Type):
	type:Type
	size:Integer|None

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
class TFunc(Type):
	parameters:list[Signature]
	ret:Type|None

@dataclass
class TFix(Type):
	parameters1:list[Signature]
	parameters2:list[Signature]
	ret:Type|None

@dataclass
class TAlias(Type):
	name:Name

@dataclass
class TAddr(Type):
	type:Type


@dataclass
class EnumElem(Node):
	name:Name
	tag:Integer|None

@dataclass
class SEnum(Stmt):
	name:Name
	elems:list[EnumElem]

@dataclass
class SType(Stmt):
	name:Name
	type:Type

@dataclass
class SFunc(Stmt):
	signature:Signature
	block:Block

@dataclass
class SData(Stmt):
	signature:Signature
	exp:Exp

@dataclass
class SDecl(Stmt):
	signature:Signature

@dataclass
class SNop(Stmt): pass


@dataclass
class SImport(Node):
	name:Name|None
	rename:Name|None
	signatures:list[Signature]

@dataclass
class SExport(Node):
	name:Name
	signatures:list[Signature]

@dataclass
class File(Node):
	export:SExport|None
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

	def import_list(self, meta, *imports):
		return list(imports)

	# exports/imports
	def s_export(self, meta, name, *signatures):
		return SExport(self.obj(meta), name, signatures)
	
	def s_import(self, meta, name, rename, *signatures):
		return SImport(self.obj(meta), name, rename, signatures)
	
	# global statements
	def s_nop(self, meta):
		return SNop(self.obj(meta))
	
	def s_decl(self, meta, signature):
		return SDecl(self.obj(meta), signature)
		
	def s_data(self, meta, signature, exp):
		return SData(self.obj(meta), signature, exp)

	def s_func(self, meta, signature, block):
		return SFunc(self.obj(meta), signature, block)

	def s_type(self, meta, name, type):
		return SType(self.obj(meta), name, type)
	
	def s_enum(self, meta, name, *elements):
		return SEnum(self.obj(meta), name, elements)
	
	def enum_elem(self, meta, name, value):
		return EnumElem(self.obj(meta), name, value)
	
	# signature
	def signature(self, meta, name, attr, type):
		return Signature(self.obj(meta), name, attr, type)
	
	# block
	def block(self, meta, *statements):
		return Block(self.obj(meta), statements)

	#types
	def t_func(self, meta, ret, param):
		return TFunc(self.obj(meta), param, ret)
	
	def t_fix(self, meta, ret, param1, param2):
		return TFix(self.obj(meta), param1, param2, ret)

	def param_list(self, meta, *params):
		return list(params)

	def t_alias(self, meta, name):
		return TAlias(self.obj(meta), name)
	
	def t_addr(self, meta, type):
		TAddr(self.obj(meta), type)
		
	def t_struct(self, meta, *members):
		return TStruct(self.obj(meta), members)

	def t_array(self, meta, type, size):
		return TArray(self.obj(meta), type, size)
	
	# statements
	def s_comp(self, meta, exp):
		return SComp(self.obj(meta), exp)
	
	def e_if(self, meta, cond, b_true, b_false):
		return SIf(self.obj(meta), cond, b_true, b_false)

	def s_while(self, meta, cond, block):
		return SWhile(self.obj(meta), cond, block)
	
	def s_do(self, meta, block, cond):
		return SDo(self.obj(meta), cond, block)
	
	def s_tail(self, meta, exp):
		return STail(self.obj(meta), exp)
	
	def s_ret(self, meta, exp):
		return SRet(self.obj(meta), exp)
	
	def s_continue(self, meta):
		return SCont(self.obj(meta))
	
	def s_break(self, meta):
		return SBreak(self.obj(meta))

	# expressions
	def e_pipe(self, meta, e_from, e_to):
		return EPipe(self.obj(meta), e_from, e_to)

	def e_assign(self, meta, obj, val):
		return EAssign(self.obj(meta), obj, val)

	def e_index(self, meta, obj, id):
		return EIndex(self.obj(meta), obj, id)

	def e_if(self, meta, cond, e_true, e_false):
		return EIf(self.obj(meta), cond, e_true, e_false)

	def e_prefix(self, meta, id, exp):
		return EPrefix(self.obj(meta), id, exp)
	
	def e_suffix(self, meta, exp, id):
		return ESuffix(self.obj(meta), id, exp)

	def e_infix(self, meta, e1, id, e2):
		return EInfix(self.obj(meta), id, e1, e2)

	def e_array(self, meta, *exps):
		return EArray(self.obj(meta), exps)

	def e_call(self, meta, func, *args):
		return ECall(self.obj(meta), func, args)

	def e_member(self, meta, name, child):
		return EMember(self.obj(meta), name, child)

	def e_recep(self, meta):
		return ERecep(self.obj(meta))

	def e_lambda(self, meta, type, block):
		return ELambda(self.obj(meta), type, block)

	def e_at(self, meta, addr):
		return EAt(self.obj(meta), addr)
	
	def e_addr(self, meta, obj):
		return EAddr(self.obj(meta), obj)
	
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
	

