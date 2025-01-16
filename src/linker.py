
import syntaxtree as Ast
from typechecker import checkTypeEqual, TwoSnippetsException, OneSnippetException, CompilationException

class Linker():
	def link(self, asts:list[Ast.File]) -> Ast.File:
		print("### Linking ###")

		all_definitions = {}
		main_ast = None

		# check for Label redefinitions
		for ast in asts:
			for signature in ast.exports.signatures:
				name = signature.label.name.value
				if name in all_definitions:
					raise TwoSnippetsException(
						f"Redefinition for label \"{name}\"",
						all_definitions[name].meta,
						signature.meta
					)
				if name == "main":
					main_ast = ast
				all_definitions[name] = signature
		
		if main_ast == None:
			print ("No defined 'main' function")
			#raise CompilationException ("No defined 'main' function")
		
		all_declarations = {}
		# check for mistyped declarations
		for ast in asts:
			signature:Ast.Signature
			for signature in ast.imports.signatures:
				name = signature.label.name.value
				if name in all_declarations:
					error = checkTypeEqual(signature.type, all_declarations[name].type)
					if error:
						raise TwoSnippetsException(
							f"Two declarations for the label \"{name}\" have different types ({error})",
							all_declarations[name].meta,
							signature.meta
						)
				else:
					all_declarations[name] = signature
		
		# remove defined declarations
		for ast in asts:
			for statement in ast.statements:
				if isinstance(statement, Ast.Declaration):
					if statement.label.name.value in all_definitions:
						ast.statements.remove(statement)
		
		# typecheck declarations vs definitions
		for declaration_name in all_declarations:
			# declarations unresolved at link time must be resolved during compilation 
			if declaration_name in all_definitions:
				declaration:Ast.Signature = all_declarations[declaration_name]
				definition:Ast.Signature = all_definitions[declaration_name]
				error = checkTypeEqual(declaration.type, definition.type)
				if error:
					raise TwoSnippetsException(
						f"The declaration type for the label @{name} differs from its definition type ({error})",
						declaration.meta,
						definition.meta
					)
		
		# declarations defined outside link space, must be include through a file with the correct 
		# declarations. So even if they are undefined, they can be typecheked

		linked_ast = Ast.File(None, [])
		for ast in asts:
			for statement in ast.statements:
				linked_ast.statements.append(statement)
		
		return linked_ast
