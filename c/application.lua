local lexer  = require "lexer"
--local parser = require "parser"
local parser = require "parser-auto"
local pprint = require "pprint"


local program = [[
.. comment

export {hello:int, bye:8};

Character :: {
	pos : Vec2, ..[..
	sprite : Image,
..]
	script : 0 -> 0
};

a = 3;

.. MySession :: ?Int > !Int > End;
]]

local path = "../tests/includes/test_inc_04.sps"
local prog = io.open(path, "r")
if not prog then print ("Couldn't open file: "..path) return end
prog = prog:read("a")

print ("\27[33m\27[1mCompiling the following file:\27[0m")
print (prog)

print ("\n\27[33m\27[1mTokenizing:\27[0m")
local tokens, err = lexer.tokenize(prog)
print (err)
if tokens == nil then
	return
end

print ("\n\27[33m\27[1mParsing:\27[0m")
local ast, err = parser.parse(tokens)
if not ast then
	print(err)
	return
end

print(parser.dump_ast(ast))

print (string.format("\27[1mCompilation successful!\27[0m"))