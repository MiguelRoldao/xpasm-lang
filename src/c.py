
import syntaxtree as Ast
from generatorbase import Generator as GeneratorBase
from typechecker import OneSnippetException, CompilationException

def str2literal(s:str) -> str:
	l = ""
	for c in s:
		i = ord(c)
		if i < 0x20 or i > 0x7e:
			l += f"\\{i:02x}"
		else:
			l += c
	return l

class Generator(GeneratorBase):
	headers = "" \
		"#include <stdint.h>\n" \
		"#include <alloca.h>\n" \
		"\n"

	def __init__(self) -> None:
		self.c_type:list[str] = ["void"]
		self.ptr_size = 64

		self.dependency = ""

		self.register_types = {}
		self.label_types = {}

		self.indent = ""
		self.indent_block = "    "
	
	
	def indent_push(self):
		self.indent += self.indent_block
	
	def indent_pop(self):
		self.indent = self.indent.replace(self.indent_block, "", 1)

	
	def popDependency(self):
		dep = self.dependency
		self.dependency = ""
		return dep

	def isPointer(self, t:str):
		return t[-1] == "*"
	
	def get_c_type_bytes (self, size:int) -> int:
		return (size / 8) + (size % 8)

	def get_c_type (self, type:Ast.Node) -> str:
		def size2type(size:int) -> str:
			t:str
			if size == 0:
				t = "void"
			elif size <= 8:
				t = "uint8_t"
			elif size <= 16:
				t = "uint16_t"
			elif size <= 32:
				t = "uint32_t"
			else:
				t = "uint64_t"
			return t

		if isinstance(type, Ast.TypeData):
			return size2type(type.data_size.value)
		elif isinstance(type, Ast.TypeAddr):
			return "void " + "*" * type.chains.n
		elif isinstance(type, Ast.TypeFunc):
			return self.get_c_type(type.ret)
		elif isinstance(type, Ast.TypeDataAddr):
			return size2type(type.data_size.value) + " " + "*" * type.chains.n

	def generate_declaration(self, ast:Ast.Node) -> str:
		def generate_function_declaration(ast:Ast.Node) -> str:
			ret_t = self.get_c_type(ast.type)

			name = ast.label.name.value
			s = f"{self.indent}{ret_t} {name}("
			for i, param in enumerate(ast.type.parameters.parameters):
				if i != 0:
					s += ", "
				s += self.get_c_type(param.type)
			s += ");\n"

			return s
		
		def generate_data_declaration(ast:Ast.Node) -> str:
			name = ast.label.name.value
			t = self.get_c_type(ast.type)
			s = f"{self.indent}{t} const {name};\n"
			return s

		if not ast:
			pass

		elif isinstance(ast, Ast.DefData):
			return generate_data_declaration(ast)

		elif isinstance(ast, Ast.DefFunc):
			return generate_function_declaration(ast)

		elif isinstance(ast, Ast.Declaration):
			if isinstance(ast.type, Ast.TypeFunc):
				return generate_function_declaration(ast)
			if isinstance(ast.type, Ast.TypeData):
				return generate_data_declaration(ast)
			else:
				raise CompilationException(
					f"Unimplemented: Don't know how to generate a declaration for an \"Ast.Declaration\" of type \"{ast.type.__class__.__name__}\" in c"
				)

		else:
			raise CompilationException(
				"Unimplemented: Unknown ast class to generate c code: " + ast.__class__.__name__
			)

	def generate(self, ast:Ast.Node) -> (str, str):
		if not ast:
			pass
		
		elif isinstance(ast, Ast.Integer):
			s = str(ast.value)
			t = self.c_type[-1]
			if self.isPointer(t):
				s = f"({t}){s}"
			return s, t
				
		elif isinstance(ast, Ast.String):
			t = "uint8_t const *"
			s = f"\"{ast.value}\""
			return s, t
		
		elif isinstance(ast, Ast.Char):
			t = "uint8_t"
			s = bytes(ast.value, "utf-8")[0]
			return s, t
		
		elif isinstance(ast, Ast.Label):
			t = self.label_types[ast.name.value] + " *"
			s = "&" + ast.name.value
			return s, t

		elif isinstance(ast, Ast.Register):
			name = ast.name.value
			t = self.register_types[name]
			return name, t
		
		elif isinstance(ast, Ast.Array):
			n = len(ast.elements)
			t = self.c_type[-1]
			s = "{"
			for i, member in enumerate(ast.elements):
				if i != 0:
					s += ", "
				val, val_t = self.generate(member)
				s += val
			s += "}"
			return s, t
		
		elif isinstance(ast, Ast.Parameter):
			t = self.get_c_type(ast.type)
			return ast.register.name.value, t

		elif isinstance(ast, Ast.Comp):
			t = self.c_type[-1]
			val1, t1 = self.generate(ast.exp1)
			val2, t2 = self.generate(ast.exp2)
			if ast.op == "EQ":
				s = f"({val1} == {val2})"
			else:
				raise CompilationException(
					"Unimplemented: Unknown comparison operation to generate c code: " + ast.__class__.__name__
				)
			return s, t
		
		elif isinstance(ast, Ast.Math):
			t = self.c_type[-1]
			self.c_type.append(f"uint{self.ptr_size}_t")
			val1, t1 = self.generate(ast.exp1)
			val2, t2 = self.generate(ast.exp2)
			self.c_type.pop()

			cast = f"({t})" if self.isPointer(t) else ""
			cast1 = f"(uint{self.ptr_size}_t)" if self.isPointer(t1) else ""
			cast2 = f"(uint{self.ptr_size}_t)" if self.isPointer(t2) else ""

			if ast.op == "ADD":
				s = f"{cast}({cast1}{val1} + {cast2}{val2})"
			else:
				raise CompilationException(
					"Unimplemented: Unknown math operation to generate c code: " + ast.__class__.__name__
				)
			return s, t
		
		elif isinstance(ast, Ast.Alloc):
			# TODO: make casts and expected type change this
			# @n : should allocate n blocks of infered size
			self.c_type.append("uint64_t")
			n_bits, n_t = self.generate(ast.exp)
			self.c_type.pop()

			s = f"alloca({n_bits}/8 + {n_bits}%8)"
			return s, self.c_type[-1]

		elif isinstance(ast, Ast.Read):
			# TODONOT: shouldnt i append "ptr"?
			# NO! Can't perform pointer arithmetic on type "ptr"
			t = self.c_type[-1]
			ptr_t = t + " *"
			self.c_type.append(ptr_t)
			adr, adr_t = self.generate(ast.address)
			self.c_type.pop()

			if adr_t == ptr_t:
				s = f"*{adr}"
			else:
				s = f"*({ptr_t}){adr}"
			return s, t
		
		elif isinstance(ast, Ast.Call):
			if not isinstance(ast.address, Ast.Label):
				raise OneSnippetException(
					"A \"call\" statement can only call a label, when generating c",
					ast.address.meta
				)
			
			name = ast.address.name.value
			
			type = self.label_types[name]
			
			s = f"{name}("
			for i, arg in enumerate(ast.args.args):
				if i != 0:
					s += ", "
				val, t = self.generate(arg)
				s += val
			s += ")"
			
			return s, type

		
		elif isinstance(ast, Ast.Tag):
			name = ast.label.name.value
			s = f"{name}:\n"
			self.dependency += s

			return "", ""

		elif isinstance(ast, Ast.IgnoreRes):
			val, t = self.generate(ast.exp)
			return "", ""
		
		elif isinstance(ast, Ast.DefRegister):
			t = self.get_c_type(ast.type)
			name = ast.register.name.value
			self.register_types[name] = t

			self.c_type.append(t)
			
			val, val_t = self.generate(ast.exp)

			self.dependency += f"{self.indent}{t} const {name} = {val};\n"
			self.c_type.pop()
			return "", ""

		elif isinstance(ast, Ast.Write):
			val, val_t = self.generate(ast.value)
			self.c_type.append(val_t)
			adr, adr_t = self.generate(ast.address)
			self.c_type.pop()
			if not self.isPointer(adr_t):
				destination = f"({adr_t} *)(uint{self.ptr_size}_t){adr}"
			else:
				destination = adr
			s = f"{self.indent}*{destination} = {val};\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.GotoIf):
			if not isinstance(ast.address, Ast.Label):
				val, t = self.generate(ast.address)
				destination = f"*(void *){val}"
				#raise OneSnippetException(
				#	"The \"goto\" statement can only have a label as its argument, when generating llvm",
				#	ast.address.meta
				#)
			else:
				destination = ast.address.name.value
			self.c_type.append("uint8_t")
			cond, cond_t = self.generate(ast.condition)
			self.c_type.pop()

			s =  f"{self.indent}if ({cond}) goto {destination};\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.Goto):
			if not isinstance(ast.address, Ast.Label):
				val, t = self.generate(ast.address)
				destination = f"*(void *){val}"
				#raise OneSnippetException(
				#	"The \"goto\" statement can only have a label as its argument, when generating llvm",
				#	ast.address.meta
				#)
			else:
				destination = ast.address.name.value
			s = f"{self.indent}goto {destination};\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.ReturnValue):
			t = self.c_type[-1]
			val, val_t = self.generate(ast.value)
			cast = f"({t})" if t != val_t else ""
			s = f"{self.indent}return {cast}{val};\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.Return):
			self.dependency += f"{self.indent}return;\n"
			return "", ""
		
		elif isinstance(ast, Ast.DefData):			#TODO : force constant
			name = ast.label.name.value
			t = self.get_c_type(ast.type)
			self.c_type.append(t)
			val, val_t = self.generate(ast.data)
			self.c_type.pop()
			
			s = f"{self.indent}{val_t} const {name} = {val};\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.DefFunc):
			# Because no function will have numbered registers
			# i can put this here up top
			#self.code_block_register = self.uniqueRegister()
			ret_t = self.get_c_type(ast.type)
			self.c_type.append(ret_t)

			name = ast.label.name.value
			s = f"{self.indent}{ret_t} {name}("
			for i, param in enumerate(ast.type.parameters.parameters):
				if i != 0:
					s += ", "
				val, t = self.generate(param)
				s += t + " " + val
				self.register_types[val] = t		#TODO: keep this?
			s += ") {\n"
			self.indent_push()
			for stat in ast.block.statements:
				self.generate(stat)
				s += self.popDependency()
			self.indent_pop()
			s += f"{self.indent}}}\n"

			self.register_types = {}

			self.dependency += s
			self.c_type.pop()
			return "", ""
		
		elif isinstance(ast, Ast.Declaration):
		#	if isinstance(ast.type, Ast.TypeFunc):
		#		ret_t = self.get_c_type(ast.type)
		#
		#		name = ast.label.name.value
		#		s = f"{self.indent}{ret_t} {name}("
		#		for i, param in enumerate(ast.type.parameters.parameters):
		#			if i != 0:
		#				s += ", "
		#			val, t = self.generate(param)
		#			s += t + " " + val
		#		s += ");\n"
		#		self.dependency += s
		#		return "", ""
		#	else:
		#		raise CompilationException(
		#			f"Unimplemented: Don't know how to generate a declaration of type \"{ast.type.__class__.__name__}\" in c"
		#		)
			return "",""
	

		elif isinstance(ast, Ast.File):
			prog = self.headers
			for s in ast.statements:
				self.label_types[s.label.name.value] = self.get_c_type(s.type)
				# generate c declarations
				prog += self.generate_declaration(s)
			prog += "\n"
			for s in ast.statements:
				self.generate(s)
				#self.dependency += "helo?"
				prog += self.popDependency() + "\n"
			print("### Generated code ###")
			print(prog)
			return

		raise CompilationException(
			"Unimplemented: Unknown ast class to generate c code: " + ast.__class__.__name__
		)