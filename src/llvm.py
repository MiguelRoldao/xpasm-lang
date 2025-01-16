
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

	def __init__(self) -> None:
		self.ll_type:list[str] = ["void"]
		self.ptr_size = 64

		self.dependency = ""
		self.register_names:list[str] = []
		self.next_register:int = 0
		self.code_block_register:int = 0

		self.register_types = {}
		self.label_types = {}
	
	def popDependency(self):
		dep = self.dependency
		self.dependency = ""
		return dep
	
	def uniqueNumber(self) -> int:
		i = self.next_register
		self.next_register += 1
		return i
	
	def uniqueRegister(self) -> str:
		return "%" + str(self.uniqueNumber())
	
	def resetUniqueRegister(self):
		self.register_names = []
		self.next_register = 0
	
	def typesEquivalent(self, t1:str, t2:str):
		val = False
		if t1 == t2:
			val = True
		elif t1[-1] == "*" and t2[-1] == "*":
			val = True
		elif t1[-1] == "*" and t2 == "ptr":
			val = True
		elif t1 == "ptr" and t2[-1] == "*":
			val = True
		return val

	def isPointer(self, t:str):
		return t == "ptr" or t[-1] == "*"
	
	def generateCast(self, val, t, cast_t) -> (str, str):
		res_reg = self.uniqueRegister()

		if self.isPointer(t) and not self.isPointer(cast_t):
			s = f"  {res_reg} = ptrtoint {t} {val} to {cast_t}\n"
		elif not self.isPointer(t) and self.isPointer(cast_t):
			s = f"  {res_reg} = inttoptr {t} {val} to {cast_t}\n"
		elif t[0] == 'i' and cast_t[0] == 'i':
			size1 = int(t[1:])
			size2 = int(cast_t[1:])
			if size1 > size2:
				s = f"  {res_reg} = trunc {t} {val} to {cast_t}\n"
			else:
				s = f"  {res_reg} = zext {t} {val} to {cast_t}\n"
		else:
			raise CompilationException(
				f"Unplanned cast from \"{t}\" to \"{cast_t}\""
			)
		self.dependency += s
		return res_reg, cast_t

	def get_ll_type (self, type:Ast.Node) -> str:
		if isinstance(type, Ast.TypeData):
			size = type.data_size.value
			if size == 0:
				return "void"
			else:
				return "i" + str(size)
		elif isinstance(type, Ast.TypeAddr):
			return "i8" + "*" * type.chains.n
		elif isinstance(type, Ast.TypeFunc):
			return self.get_ll_type(type.ret)
		elif isinstance(type, Ast.TypeDataAddr):
			size = type.data_size.value
			size = 8 if size == 0 else size
			return "i" + str(size) + "*" * type.chains.n

	
	def generate(self, ast:Ast.Node) -> (str, str):
		if not ast:
			pass
		
		elif isinstance(ast, Ast.Integer):
			s = f"{ast.value}"
			t = self.ll_type[-1]
			if self.isPointer(t):
				s, t = self.generateCast(s, 'i' + str(self.ptr_size), t)
			
			return s, t
		
		elif isinstance(ast, Ast.String):
			t = f"[{len(ast.value)} x i8]"
			s = f"c\"{str2literal(ast.value)}\""
			return s, t
		
		elif isinstance(ast, Ast.Char):
			t = "i8"
			s = bytes(ast.value, "utf-8")[0]
			return s, t
		
		elif isinstance(ast, Ast.Label):
			t = "ptr" #self.label_types[ast.name.value]
			s = "@" + ast.name.value
			return s, t

		elif isinstance(ast, Ast.Register):
			name = "%" + ast.name.value
			t = self.register_types[name]
			return name, t
		
		elif isinstance(ast, Ast.Array):
			n = len(ast.elements)
			type = f"[{n} x {self.ll_type[-1]}]"
			s = f"["
			for i, member in enumerate(ast.elements):
				if i != 0:
					s += ", "
				val, t = self.generate(member)
				s += t + " " + val
			s += "]"
			return s, type
		
		elif isinstance(ast, Ast.Parameter):
			t = self.get_ll_type(ast.type)
			return f"%{ast.register.name.value}", t

		elif isinstance(ast, Ast.Comp):
			val1, t1 = self.generate(ast.exp1)
			val2, t2 = self.generate(ast.exp2)
			if ast.op == "EQ":
				if not self.typesEquivalent(t1, t2):
					val2, t2 = self.generateCast(val2, t2, t1)
				reg = self.uniqueRegister()
				s = f"  {reg} = icmp eq {t1} {val1}, {val2}\n"
			self.dependency += s
			return reg, "i1"
		
		elif isinstance(ast, Ast.Math):
			t = self.c_type[-1]
			val1, t1 = self.generate(ast.exp1)
			if not self.typesEquivalent(t1, self.ll_type[-1]):
				val1, t1 = self.generateCast(val1, t1, self.ll_type[-1])
			val2, t2 = self.generate(ast.exp2)
			if not self.typesEquivalent(t2, self.ll_type[-1]):
				val2, t2 = self.generateCast(val2, t2, self.ll_type[-1])
			reg = self.uniqueRegister()
			if ast.op == "ADD":
				s = f"  {reg} = add {t1} {val1}, {val2}\n"
			self.dependency += s
			return reg, self.ll_type[-1]
		
		elif isinstance(ast, Ast.Alloc):			
			t = self.ll_type[-1][:-1]
			
			self.ll_type.append('i' + str(self.ptr_size))
			n, n_t = self.generate(ast.exp)
			self.ll_type.pop()

			reg = self.uniqueRegister()
			s = f"  {reg} = alloca {t}, {n_t} {n}\n"
			self.dependency += s

			return reg, self.ll_type[-1]

		elif isinstance(ast, Ast.Read):
			# TODONOT: shouldnt i append "ptr"?
			# NO! Can't perform pointer arithmetic on type "ptr"
			self.ll_type.append('i' + str(self.ptr_size))
			adr, adr_t = self.generate(ast.address)
			self.ll_type.pop()
			if not self.isPointer(adr_t):
				adr, adr_t = self.generateCast(adr, adr_t, adr_t + "*")

			reg = self.uniqueRegister()
			s = f"  {reg} = load {self.ll_type[-1]}, ptr {adr}\n"
			self.dependency += s
			return reg, self.ll_type[-1]
		
		elif isinstance(ast, Ast.Call):
			if not isinstance(ast.address, Ast.Label):
				raise OneSnippetException(
					"A \"call\" statement can only call a label, when generating llvm",
					ast.address.meta
				)
			
			name = ast.address.name.value
			type = self.label_types[name]
			
			s = f"call {type} @{name} ("
			for i, arg in enumerate(ast.args.args):
				if i != 0:
					s += ", "
				val, t = self.generate(arg)
				s += t + " " + val
			s += ")\n"

			if type == "void":
				reg = ""
				s = f"  " + s
			else:
				reg = self.uniqueRegister()
				s = f"  {reg} = " + s
			
			self.dependency += s

			return reg, type

		
		elif isinstance(ast, Ast.Tag):
			name = ast.label.name.value
			s =  f"  br label %{name}\n"
			s += f"{name}:\n"
			self.dependency += s

			return "", ""

		elif isinstance(ast, Ast.IgnoreRes):
			val, t = self.generate(ast.exp)
			return "", ""
		
		elif isinstance(ast, Ast.DefRegister):
			t = self.get_ll_type(ast.type)
			name = "%" + ast.register.name.value
			self.register_types[name] = t

			self.ll_type.append(t)
			
			val, val_t = self.generate(ast.exp)

			if not self.typesEquivalent(val_t, t):
				val, val_t = self.generateCast(val, val_t, t)	

			self.dependency += f"  {name} = bitcast {t} {val} to {t}\n"
			self.ll_type.pop()
			return "", ""

		elif isinstance(ast, Ast.Write):
			val, val_t = self.generate(ast.value)
			self.ll_type.append('i' + str(self.ptr_size))
			adr, adr_t = self.generate(ast.address)
			self.ll_type.pop()
			if not self.isPointer(adr_t):
				adr, adr_t = self.generateCast(adr, adr_t, adr_t + "*")

			s = f"  store {val_t} {val}, ptr {adr}\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.GotoIf):
			if not isinstance(ast.address, Ast.Label):
				raise OneSnippetException(
					"The \"goto\" statement can only have a label as its argument, when generating llvm",
					ast.address.meta
				)
			self.ll_type.append("i1")
			cond, cond_t = self.generate(ast.condition)
			self.ll_type.pop()

			label_reg = self.uniqueRegister()
			s =  f"  br {cond_t} {cond}, label %{ast.address.name.value}, label {label_reg}\n"
			s += f"{label_reg[1:]}:\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.Goto):
			if not isinstance(ast.address, Ast.Label):
				raise OneSnippetException(
					"The \"goto\" statement can only have a label as its argument, when generating llvm",
					ast.address.meta
				)
			s = f"  br label %{ast.address.name.value}\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.ReturnValue):
			t = self.ll_type[-1]
			val, t = self.generate(ast.value)
			s = f"  ret {t} {val}\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.Return):
			self.dependency += "  ret void\n"
			return "", ""
		
		elif isinstance(ast, Ast.DefData):
			name = ast.label.name.value
			self.ll_type.append(self.get_ll_type(ast.type))
			definition, t = self.generate(ast.data)
			self.ll_type.pop()
			s = f"@{name} = constant {t} {definition}\n"
			self.dependency += s
			return "", ""
		
		elif isinstance(ast, Ast.DefFunc):
			# Because no function will have numbered registers
			# i can put this here up top
			self.code_block_register = self.uniqueRegister()
			ret_t = self.get_ll_type(ast.type)
			self.ll_type.append(ret_t)

			name = ast.label.name.value
			s = f"define {ret_t} @{name}("
			for i, param in enumerate(ast.type.parameters.parameters):
				if i != 0:
					s += ", "
				val, t = self.generate(param)
				s += t + " " + val
				self.register_types[val] = t
			s += ") {\n"
			for stat in ast.block.statements:
				self.generate(stat)
				s += self.popDependency()
			last_stat = ast.block.statements[-1]
			if not isinstance(last_stat, Ast.Return) and not isinstance(last_stat, Ast.ReturnValue):
				s += "  ret void\n"
			s += "}\n"

			self.dependency += s
			self.ll_type.pop()
			self.resetUniqueRegister()
			return "", ""
		
		elif isinstance(ast, Ast.Declaration):
			if isinstance(ast.type, Ast.TypeFunc):
				ret_t = self.get_ll_type(ast.type)

				name = ast.label.name.value
				s = f"declare {ret_t} @{name}("
				for i, param in enumerate(ast.type.parameters.parameters):
					if i != 0:
						s += ", "
					val, t = self.generate(param)
					s += t + " " + val
				s += ")\n"
				self.dependency += s
				return "", ""
			else:
				raise CompilationException(
					f"Don't know how to generate a declaration of type \"{ast.type.__class__.__name__}\" in llvm"
				)

		
		elif isinstance(ast, Ast.File):
			for s in ast.statements:
				self.label_types[s.label.name.value] = self.get_ll_type(s.type)
			prog = ""
			for s in ast.statements:
				self.generate(s)
				#self.dependency += "helo?"
				prog += self.popDependency() + "\n"
			print(prog)
			return

		
		raise CompilationException(
			"Unknown ast class to generate llvm code: " + ast.__class__.__name__
		)