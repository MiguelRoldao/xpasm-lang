


import argparse

from exceptions import CompilationException, OneSnippetException, TwoSnippetsException
import syntaxtree as Ast
# from typechecker import TypeChecker
# from optimizer import Optimizer
# from linker import Linker

from generatorbase import Generator
import c

class Application():
	generator:Generator

	def compile(self, file_paths:list[str]):
		asts:list[Ast.Node] = []
		# generate asts
		for path in file_paths:
			ast:Ast.File
			with open(path,"r") as f:
				file = f.read()

				ast = Ast.generateAST (path, file)

				print(ast.pretty())
				return

				try:
					TypeChecker().check(ast)
				except OneSnippetException as e:
					raise CompilationException(f"TypeChecker: " + str(e))
				except TwoSnippetsException as e:
					raise CompilationException(f"TypeChecker: " + str(e))
				
				ast = Optimizer().constantCleaner(ast)
				

			# resolve imports, parse auxilary files and extract declarations
			asts.append(ast)
		
		# linking stage
		try:
			final_ast = Linker().link(asts)
		except CompilationException as e:
			raise CompilationException(f"Linker: " + str(e))
		
		# TODO: Optimize linked ast

		print(final_ast.dump())

		try:
			code = self.generator.generate(final_ast)
		except CompilationException as e:
			raise CompilationException(f"Generator: " + str(e))
		


	def main(self):
		argparser = argparse.ArgumentParser(
			description='Official compiler for the XPASM (eXtra Portable ASeMbly) lanuage. Outputs in the JSON format.'
		)

		argparser.add_argument(
			'-o',
			type=str,
			help='Output file name. If ignored, output is presented on screen.',
		)

		argparser.add_argument(
			'input_file',
			type=str,
			nargs='+',
			help='Required input file name.'
		)

		argparser.add_argument(
			'--compact',
			action='store_true',
			help='If specified, the output is void of whitespace for compactness.'
		)

		argparser.add_argument(
			'--syntax',
			action='store_true',
			help='If specified, only the parser and lexer are run. The ast is then printed.'
		)


		args = argparser.parse_args()


		input_files = args.input_file

		if args.syntax:
			mode = "syntax"
		else:
			mode = "normal"

		match (mode):
			case "syntax":
				try:
					for path in input_files:
						ast:Ast.File
						with open(path,"r") as f:
							file = f.read()

							ast = Ast.generateAST (path, file)

							print(ast.dump)
				except CompilationException as e:
					print("ERROR: " + str(e))

			case "normal":
				self.generator = c.Generator()

				try:
					self.compile(input_files)
				except CompilationException as e:
					print("ERROR: " + str(e))

			case _:
				raise Exception(f"Unknown compilation mode '{mode}'")

		

		return


if __name__ == "__main__":
	app = Application()
	app.main()