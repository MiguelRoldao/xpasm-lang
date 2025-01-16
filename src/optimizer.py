

import copy

import syntaxtree as Ast
from exceptions import CompilationException


class Optimizer():
	
	def isConstant(self, ast:Ast.Node) -> bool:
		value = False
		if isinstance(ast, Ast.DefData):
			#value = isinstance(ast.visibility, Ast.Private)
			value = self.isConstant(ast.data)
			value = False # TODO: remove this
		elif isinstance(ast, Ast.DefRegister):
			value = self.isConstant(ast.exp)
		elif isinstance(ast, Ast.Arguments):
			val = True
			for arg in ast.args:
				val = val and self.isConstant(arg)
			value = val
		elif isinstance(ast, Ast.Array):
			val = True
			for elem in ast.elements:
				val = val and self.isConstant(elem)
			value = val
		elif isinstance(ast, Ast.Cast):
			value = self.isConstant(ast.exp)
		elif isinstance(ast, Ast.Not):
			value = self.isConstant(ast.exp)
		elif isinstance(ast, Ast.Register):
			value = getattr(ast, 'compile_time_value', False)
		elif isinstance(ast, Ast.Integer):
			value = True
		elif isinstance(ast, Ast.Label):
			value = self.isConstant(ast.reference)
		elif isinstance(ast, Ast.Char):
			value = True
		elif isinstance(ast, Ast.String):
			value = False

		return value
	
	
	def constantCleaner(self, ast:Ast.Node) -> Ast.Node:
		if isinstance(ast, Ast.File):
			news:list[Ast.Node] = []
			for s in ast.statements:
				news.append(self.constantCleaner(s))
			ast.statements = news
		
		elif isinstance(ast, Ast.Declaration):
			pass
		
		elif isinstance(ast, Ast.DefFunc):
			ast.block = self.constantCleaner(ast.block)
		
		elif isinstance(ast, Ast.DefData):
			ast.data = self.constantCleaner(ast.data)
		
		elif isinstance(ast, Ast.Block):
			news:list[Ast.Node] = []
			for s in ast.statements:
				news.append(self.constantCleaner(s))
			ast.statements = news
		
		elif isinstance(ast, Ast.DefRegister):
			ast.exp = self.constantCleaner(ast.exp)
			# TODO: clean any references to this register, if constant (clean constant registers)
		
		elif isinstance(ast, Ast.Write):
			ast.address = self.constantCleaner(ast.address)
			ast.value = self.constantCleaner(ast.value)
		
		elif isinstance(ast, Ast.Goto):
			ast.address = self.constantCleaner(ast.address)
		
		elif isinstance(ast, Ast.GotoIf):
			ast.address = self.constantCleaner(ast.address)
			ast.condition = self.constantCleaner(ast.condition)
		
		elif isinstance(ast, Ast.ReturnValue):
			ast.value = self.constantCleaner(ast.value)
		
		elif isinstance(ast, Ast.Return):
			pass
		
		elif isinstance(ast, Ast.IgnoreRes):
			ast.exp = self.constantCleaner(ast.exp)
		
		elif isinstance(ast, Ast.Tag):
			pass
		
		elif isinstance(ast, Ast.Read):
			ast.address = self.constantCleaner(ast.address)
			print("const cleaner read 1", ast.address.__class__.__name__)
			if self.isConstant(ast.address):
				print("const cleaner read 2")
				if isinstance(ast.address, Ast.Label):
					print("const cleaner read 3")
					label = ast.address
					if isinstance(label.reference, Ast.DefData):
						print("const cleaner read 4")
						ast = self.constantCleaner(label.reference.data)
		
		elif isinstance(ast, Ast.Call):
			ast.address = self.constantCleaner(ast.address)
			ast.args = self.constantCleaner(ast.args)
		
		elif isinstance(ast, Ast.Arguments):
			newargs:list[Ast.Node] = []	
			for arg in ast.args:
				newargs.append(self.constantCleaner(arg))
			ast.args = newargs
		
		elif isinstance(ast, Ast.Array):
			newelems:list[Ast.Node] = []	
			for elem in ast.elements:
				newelems.append(self.constantCleaner(elem))
			ast.elements = newelems
		
		elif isinstance(ast, Ast.Cast):
			if isinstance(ast.type, Ast.TypeData):
				mask = pow(2, ast.type.data_size.value) - 1
				print ("oop" + str(ast.exp))
				ast.exp = self.constantCleaner(ast.exp)
				ast = copy.deepcopy(ast.exp)
				ast.value = ast.value & mask

		
		elif isinstance(ast, Ast.Not):
			ast.exp = self.constantCleaner(ast.exp)
		
		elif isinstance(ast, Ast.Alloc):
			ast.exp = self.constantCleaner(ast.exp)

		elif isinstance(ast, Ast.Math):
			ast.exp1 = self.constantCleaner(ast.exp1)
			ast.exp2 = self.constantCleaner(ast.exp2)

			if self.isConstant(ast.exp1) and self.isConstant(ast.exp2):
				val1 = ast.exp1
				val2 = ast.exp2
				if isinstance(val1, Ast.Integer):
					if ast.op == "ADD":
						ast = Ast.Integer(ast.meta, val1.value + val2.value)
					elif ast.op == "SUB":
						ast = Ast.Integer(ast.meta, val1.value - val2.value)
					elif ast.op == "MUL":
						ast = Ast.Integer(ast.meta, val1.value * val2.value)
					elif ast.op == "DIV":
						ast = Ast.Integer(ast.meta, int(val1.value / val2.value))
					else:
						raise CompilationException(
							"UnknownOP: " + ast.op
						)
				
		
		elif isinstance(ast, Ast.Comp):
			ast.exp1 = self.constantCleaner(ast.exp1)
			ast.exp2 = self.constantCleaner(ast.exp2)

			if self.isConstant(ast.exp1) and self.isConstant(ast.exp2):
				# TODO: compute comparison operation
				pass
		
		elif isinstance(ast, Ast.Register):
			# if register_definition_is_constant:
				# TODO: replace with constant
				pass
		
		# TODO: maybe do something about these two?

		elif isinstance(ast, Ast.Integer):
			pass

		elif isinstance(ast, Ast.Label):
			pass
		
		elif isinstance(ast, Ast.Char):
			pass
		
		elif isinstance(ast, Ast.String):
			pass
		
		else:
			raise CompilationException(
				"Undefined AST node class for Compiler.constantCleaner named: " + ast.__class__.__name__
			)
		
		return ast
