
from dataclasses import dataclass

import syntaxtree as ast
from exceptions import *
import context
from context import Context



#def checkTypeEqual(t1:ast.Type, t2:ast.Type):
#	if not type(t1) is type(t2):
#		return "different types"
#	elif isinstance(t1, ast.TypeData):
#		if t1.data_size.value != t2.data_size.value:
#			return "data size"
#	elif isinstance(t1, ast.TypeAddr):
#		if t1.chains.n != t2.chains.n:
#			return "chain depth"
#	elif isinstance(t1, ast.TypeDataAddr):
#		if t1.chains.n != t2.chains.n:
#			return "chain depth"
#		if t1.data_size.value != t2.data_size.value:
#			return "data size"
#	elif isinstance(t1, ast.TypeFunc):
#		s = checkTypeEqual(t1.ret, t2.ret)
#		if s:
#			return f"return types ({s})"
#		if len(t1.parameters.parameters) != len(t2.parameters.parameters):
#			return "Number of parameters"
#		for i in range(len(t1.parameters.parameters)):
#			s = checkTypeEqual(t1.parameters.parameters[i].type, t2.parameters.parameters[i].type)
#			if s:
#				return f"type of parameter {i} ({s})"
#			if t1.parameters.parameters[i].register.name.value != t2.parameters.parameters[i].register.name.value:
#				return f"name of register in parameter {i+1}"
#		return
#	else:
#		return f"$$ unknown ast types {t1.__class__.__name__} and {t1.__class__.__name__}"


# In this language, conventional typecheking makes no sense, as
# everything is "just" data :)
# There could be warnings, but to avoid these warnings, casts
# would be necessary and That is not desirablenecessity. Types in 
# XPASM are merely hints to aid good programming practices. To
# avoid human mistakes when declaring and defining data. 
# To make sure the codebase is uniform, with no discrepancies.

class Definition():
	type:ast.Type
	node:ast.Node
	def __init__(self, type:ast.Type, node:ast.Node) -> None:
		self.type = type
		self.node = node


class Definitions(Context):
	parents:list[str]
	def __init__(self) -> None:
		super().__init__()
		self.parents = []

	def getParentName(self) -> str:
		parentname = ""
		for name in self.parents:
			parentname += name + "."
		return parentname
	
	def push(self, name:str) -> None:
		self.parents.append(name)
	
	def pop(self) -> None:
		self.parents.pop()
	
	def insert(self, key:str, value:Definition) -> None:
		try:
			super().insert(self.getParentName() + key, value)
		except context.RedifinitionException as e:
			prev = self.get(key)
			if isinstance(prev.node, ast.ProgDecl):
				if type == prev.type:
					self.update(key, value)
				else:
					raise TwoSnippetsException(
						f"New type ({type}) for \"{key}\" doesn't match previous declaration with type {prev.type}",
						prev.node.meta,
						value.node.meta
					)
			else:
				raise TwoSnippetsException(
					f"\"{key}\" with type {type} was already defined as a {prev.type}",
					prev.node.meta,
					value.node.meta
				)
	
	def update(self, key:str, value:Definition) -> None:
		return super().update(self.getParentName() + key, value)
	
	def get(self, key:str) -> Definition:
		return super().get(self.getParentName() + key)
	
	def has(self, key:str) -> bool:
		return super().has(self.getParentName() + key)
	
	def clear(self): # u
		self.__init__() # i love




class TypeChecker():
	context:Context
	definitions:Definitions
	#declarations:dict
	
	const:bool
	signatures:dict
	usedLabels:dict
	labelStack:list
	type_aliases:dict[str,ast.Type]
	pointer_size:int = 64

	def __init__(self) -> None:
		self.context = Context()
		self.definitions = Definitions()
		#self.declarations = {}
		self.const = False
		self.signatures = {}
		self.usedLabels = {}
		self.labelStack = []

		self.type_aliases = {}



##### WHAT THE ACTUAL FUCK IS THIS??? #####
	def getAbsoluteType(definition:Definition, definitions:Definitions) -> Definition:
		if isinstance(definition.type, AliasT):
			alias_definition = definitions.get(definition.type.alias)
			if not isinstance(alias.definition, Type):
				raise TwoSnippetsException(
					f"\"{abs_t}\" is not defined as a type, hence it can't be used as a type alias",
					prev.node.meta,
					node.meta
				)
			definitions.update(var, abs_t)
			t = abs_t

		elif isinstance(t, ):
			pass

		else:
			return definition
	
	# resolves alias dependencies of types.
	# transforming relative types to abosolute types.
	# e.g. v:u u::t t::32 -> v:32 u::32 t::32
	# e.g. v:t t::32 -> v:32 t::32
	def resolveType(t:ast.Type, definitions:Definitions) -> ast.Type:
		if isinstance(t, ast.TypeAlias):
			name = t.name.value
			try:
				og = definitions.get(name)
			except context.UndefinedException as e:
				raise OneSnippetException(
					f"Undefined type name \"{name}\"",
					t.name.meta
				)
			t = TypeChecker.resolveType(og.type, definitions)
			return t
		# TODO: finish this ↑↓
		elif isinstance(t, MetaT):
			new_t = TypeChecker.resolveType(t.type, definitions)
			
		elif isinstance(t, ast.AddrT):
			resolved_t = TypeChecker.resolveType(t.type, definitions)
			if t != resolved_t:
				return ast.TypeAddr(t.meta, resolved_t)
			else:
				return t
		elif isinstance(t, ast.TypeFunc):
			resolved_ret_t = TypeChecker.resolveType(t.ret, definitions)
			resolved_params_t:list[ast.Parameter]
			for p_t in t.parameter_list.parameters:
				resolved_params_t.append(TypeChecker.resolveType(p_t, definitions))
			return ast.TypeFunc(
				t.meta,
				ast.ParameterList(
					t.parameter_list.meta,
					resolved_params_t
				),
				resolved_ret_t
			)
		elif isinstance(t, StructT):
			for m in t.members:
				TypeChecker.resolveType(t.members[m], definitions)
		else:
			return t

	def resolveAliasTypes(definitions:Definitions) -> None:
			# TODO: make sure this is how to iterate through a dictionary
			name:str
			definition:Definition
			for name, definition in definitions.ctx.items():
				if isinstance(definition.type, MetaT):
					
				if isinstance(definition.type, AliasT):
					definitions.
				elif isinstance(definition.type, FuncT):
					TypeChecker.resolveAliasType
				else:
					pass
###########################################


	def gatherDefinitions(self, node:ast.Node, definitions:Definitions) -> None:
		if isinstance(node, ast.File):
			for s in node.statements:
				self.gatherDefinitions(s, definitions)
			TypeChecker.resolveAliasTypes(definitions)

		elif isinstance(node, ast.TypeDef):
			n = node.name.value
			t = node.type
			definitions.insert(n, Definition(t, node))
			
		elif isinstance(node, ast.EnumDef):
			n = node.name.value
			t = node.type
			definitions.insert(n, Definition(t, node))
			definitions.push(n)
			for elem in node.elems:
				self.gatherDefinitions(elem, definitions)
			definitions.pop()
		
		elif isinstance(node, ast.EnumElem):
			n = node.name.value
			t = ast.TypeUnsized(node.meta)
			definitions.insert(n, Definition(t, node))
		
		elif isinstance(node, ast.ProgDecl):
			n = node.name.value
			t = node.type
			definitions.insert(n, Definition(t, node))
		
		elif isinstance(node, ast.ProgDef):
			n = node.name.value
			t = node.type
			definitions.insert(n, Definition(t, node))
			definitions.push(n)
			self.gatherDefinitions(node.exp, definitions)
			definitions.pop()
		
		elif isinstance(node, ast.Label):
			n = node.name.value
			t = ast.TypeProg(node.meta)
			definitions.insert(n, Definition(t, node))

	
	
	def infer(self, node:ast.Node) -> ast.Type:
		# TODO: what about functions that return functions?
		# I think checkin for FuncT is enough, but will need confirmation.
		if isinstance(node, ast.Call):
			self.check(node)
			address_type = self.infer(node.address)
			if isinstance(address_type, FuncT):
				return address_type.ret
			else:
				raise OneSnippetException(
					"Can't infer return type of a call operation to a memory address that is not a function type "
					"(Consider casting the function call address to the expected function type)",
					node.meta
				)
		elif isinstance(node, ast.Array):
			raise OneSnippetException(
				"Can't infer type of an anonymous array "
				"(Consider either casting the array to the expected pointer type, or declare it in the appropriate scope)",
				node.meta
			)
		elif isinstance(node, ast.Read):
			self.check(node)
			address_type = self.infer(node.address)
			if isinstance(address_type, AddrT):
				return address_type
			else:
				raise OneSnippetException(
					"Can't infer the type of a read operation from a memory address that is not a pointer type"
					"(Consider casting the read opeartion or the memory address to the pretended type)",
					node.meta
				)
		elif isinstance(node, ast.Cast):
			self.check(node)
			return self.ast2type(node.type)
		elif isinstance(node, ast.Attribute):
			self.check(node)
			parent_t = self.infer(node.parent)
			if isinstance(parent_t, StructT):
				return parent_t.members[node.name.value]
			elif isinstance(parent_t, EnumT):
				return UnsizedT
			else:
				# TODO: move this to check()
				if isinstance(node.parent, ast.Name):
					parent_name = node.parent.value
				elif isinstance(node.parent, ast.Attribute):
					parent_name = node.parent.name.value
				raise OneSnippetException(
					f"Variable {parent_name} of type {parent_t} has no attributes",
					node.parent.meta
				)
		elif isinstance(node, ast.BitNot):
			self.check(node)
			return self.infer(node.exp)
		elif isinstance(node, ast.LogicalNot):
			self.check(node)
			return SizedT(1)
		elif isinstance(node, ast.Alloc):
			self.check(node)
			return AddrT(VoidT)
		elif isinstance(node, ast.Math):
			self.check(node)
			t1 = self.infer(node.exp1)
			t2 = self.infer(node.exp2)

			if isinstance(t1, UnsizedT):
				return t2
			if isinstance(t2, UnsizedT):
				return t1
			
			if isinstance(t1, SizedT) and isinstance(t2, SizedT):
				return max(t1, t2)
			if isinstance(t1, SizedT) and isinstance(t2, AddrT):
				return AddrT(VoidT())
			if isinstance(t1, AddrT)  and isinstance(t2, SizedT):
				return AddrT(VoidT())
			if isinstance(t1, AddrT)  and isinstance(t2, AddrT):
				return AddrT(VoidT())
			
			raise OneSnippetException(
				f"Can't perform math operation '{node.op}' between values of type '{t1}' and '{t2}'",
				node.meta
			)
		elif isinstance(node, ast.Comp):
			self.check(node)
			return SizedT(1)
		elif isinstance(node, ast.Integer):
			return UnsizedT()
		elif isinstance(node, ast.Name):
			return self.context.get(node.value)
		elif isinstance(node, ast.Char):
			return SizedT(8)
		elif isinstance(node, ast.String):
			return AddrT(SizedT(8))
		else:
			raise CompilationException(
				"Typechecker.infer(): Undefined case for AST node class named: " + node.__class__.__name__
			)


	# TODO: redo check() according to the new standard. Using
	# the newly created infer() method

	# TODO: find a way to include type/enum directives from other files
	# 1: Define in every file. Tedious not efficient
	# 2: Add #include directive to merge files
	# 3: Undefined types are inherently correct in first pass. 
	#    Requiring another typecheck after linking.
	# 4: ... more brainstorm

	# check coherence between declarations and definitions
	# check labels and registers names are valid
	def check(self, node:ast.Node) -> None:
		
		if isinstance(node, ast.File):
			# add global variables to context
			self.gatherDefinitions(node, self.definitions)

			for statement in node.statements:
				self.check(statement)
			
			# TODO: I think this should go ...
			# check if all used labels were defined
			for used_label in self.usedLabels:
				if used_label not in self.signatures:
					raise OneSnippetException(
						f"Use of undefined label \"{used_label}\"",
						self.usedLabels[used_label].meta
					)

		elif isinstance(node, ast.TypeDef):
			name = node.name.value
			type = MetaT(self.ast2type(node.type))
			TypeChecker.addToContext(self.context, name, type, node)


		elif isinstance(node, ast.ProgDecl):
			name = node.name.value
			type = self.ast2type(node.type)
			TypeChecker.addToContext(self.context, name, type, node)

		elif isinstance(node, ast.ProgDef):
			name = node.name.value
			type = self.infer(node)
			TypeChecker.addToContext(self.context, name, type, node)

			if isinstance(node.type, ast.TypeFunc):
				self.context.push()
				for parameter in node.type.parameter_list.parameters:
					p_name = parameter.name.value
					p_type = self.ast2type(parameter.type)
					try:
						self.context.insert(p_name, Definition(p_type, parameter))
					except context.RedifinitionException as e:
						prev:Definition = self.context.get(p_name)
						raise TwoSnippetsException(
							f"Redefinition for parameter \"{name}\"",
							prev.node.meta,
							parameter.meta
						)
				if not isinstance(node.exp, ast.FuncBlock):
					raise TwoSnippetsException(
						f"A function definition must be followed by a function block",
						node.type.meta,
						node.exp.meta
					)
				else:
					for statement in node.exp.statements:
						self.check(statement)
					self.context.pop()
			else:
				self.const = True
				self.check(node.exp)
				self.const = False


		elif isinstance(node, ast.DefRegister):
			self.check(node.exp)
			try:
				self.context.insert(node.register.name.value, Definition(node.type, node.register))
			except context.RedifinitionException as e:
				prevdef:Definition = self.context.get(node.register.name.value)
				raise TwoSnippetsException(
					f"Redefinition for register %{node.register.name.value}",
					prevdef.node.meta,
					node.register.meta
				)

		elif isinstance(node, ast.Write):
			self.check(node.address)
			self.check(node.value)
		
		elif isinstance(node, ast.Goto):
			self.check(node.address)
		
		elif isinstance(node, ast.GotoIf):
			self.check(node.address)
			self.check(node.condition)

		elif isinstance(node, ast.ReturnValue):
			self.check(node.value)
		
		elif isinstance(node, ast.Tag):
			self.addSignature(node.label, ast.TypeFunc(None, ast.TypeData(None, 0), ast.Parameters(None, [])), node)

		elif isinstance(node, ast.Read):
			if self.const:
				raise OneSnippetException(
					"Can't read from memory in a constant definition",
					node.meta
				)
			self.check(node.address)

		elif isinstance(node, ast.Call):
			if self.const:
				raise OneSnippetException(
					"Can't call a function in a constant definition",
					node.meta
				)
			self.check(node.address)
			self.check(node.args)
		# [✓] TO DO: decide what to do with 
		# compare arguments with definition/declaration
		# Waring? Error?
		# only error if address is a label?
		# currently not checking
		# 
		# conclusion: no check. could only be possible on direct use
		# labels. This messes only with the way the call arguments are
		# prepared. Using mismatched arguments/parameters is undefined
		# behaviour.

		elif isinstance(node, ast.Array):
			for elem in node.elements:
				self.check(elem)
		
		elif isinstance(node, ast.Math):
			self.check(node.exp1)
			self.check(node.exp2)

		# TODO: Not and alloc
		
		elif isinstance(node, ast.Comp):
			self.check(node.exp1)
			self.check(node.exp2)
		
		elif isinstance(node, ast.Arguments):
			for arg in node.args:
				self.check(arg)
		
		elif isinstance(node, ast.Register):
			if self.const:
				raise OneSnippetException(
					"Can't use registers in a constant definition",
					node.meta
				)
			if not self.context.isDefined(node.name.value):
				raise OneSnippetException(
					f"Use of undefined register %{node.name.value}",
					node.meta
				)
		
		elif isinstance(node, ast.Label):
			if node.name.value not in self.usedLabels:
				self.usedLabels[node.name.value] = node

		else:
			raise CompilationException(
				"Typechecker.check(): Undefined case for AST node class named: " + node.__class__.__name__
			)
	
	def typecheck(self, node:ast.Node):
		self.gatherDefinitions(node)
		self.check(node)
		
	
		
			

			