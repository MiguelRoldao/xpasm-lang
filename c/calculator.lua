

local tkn_symbol = "[^%w%s%(%)%{%}%[%],%.;@]"
local tkn_number = "[0-9]*"
local tkn_name = "[_%l%u][_%w]*"
local exp = "("..tkn_number..")".."("..tkn_symbol..")".."("..tkn_number..")"


local program = "3+2-1"


print (string.match(program, exp))