
class RedifinitionException(Exception):
	pass

class UndefinedException(Exception):
	pass

class Context():
	ctx:list[dict]
	def __init__(self) -> None:
		self.ctx = [{}]
	
	# raise context level
	def push(self) -> None:
		self.ctx.append({})

	# lower context level
	def pop(self) -> None:
		self.ctx.pop()
	
	# insert new entry for key
	# if already defined, raise exception
	def insert(self, key, value) -> None:
		scope = self.ctx[-1]
		if key in scope:
			raise RedifinitionException()
		scope[key] = value;

	# update the entry for the key found first
	# if undefined, raise exception
	def update(self, key, value) -> None:
		for scope in reversed(self.ctx):
			if key in scope:
				scope[key] = value
				return
		raise UndefinedException()
	
	# get entry with key, in any context level
	# if undefined, raise exception
	def get(self, key):
		for scope in reversed(self.ctx):
			if key in scope:
				return scope[key]
		raise UndefinedException()
	
	# checks wether a key is defined in the upper levels
	def has(self, key, levels:int=None) -> bool:
		if not levels:
			levels = len(self.ctx)
		for scope in self.ctx[len(self.ctx)-levels:]:
			if key in scope:
				return True
		return False
	
	def clear(self):
		self.__init__()

