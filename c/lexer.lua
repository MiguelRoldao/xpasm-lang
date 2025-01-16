local lexer = {}

local prettyfile = require "prettyfile"
local Token = require "token"

-- token list
lexer.terminals = {
	{"{", "%{"},
	{"}", "%}"},
	{"[", "%["},
	{"]", "%]"},
	{"(", "%("},
	{")", "%)"},
	{".", "%."},
	{",",  ","},
	{":",  ":"},
	{";",  ";"},
	{"@",  "@"},

	{"DECIMAL", "[1-9][0-9]*"},
	{"HEX", "0x[0-9a-fA-F]+"},
	{"BIN", "0b[01]+"},
	{"OCT", "0[0-7]+"},
	{"ZERO", "0"},

	{"STRING", "\"[%S ]\""},
	{"CHAR", "\'[%S ]\'"},

	{"NAME", "[_%l%u][_%w]*"},
	{"SYMBOL", "[^%w%s%(%)%{%}%[%]%.,:;@]+"},
}

lexer.ignore = {
	{"LINE_COMMENT",  "%.%.[^\n]*"},
	{"BLOCK_COMMENT", "%[%.%..-%.%.%]"},
	{"SEPARATOR",     "[%s]+"},
}


function lexer.tokenize(str)
	local tokens = {}
	local pos = 1
	local line = 1
	local column = 1
	local match = nil

	::loop::

	-- check for end of file
	if #str < pos then
		return tokens, string.format(
			"\27[34m\27[1mINFO:\27[0m "..
			"Reached EOF after processing %d tokens.",
			#tokens
		)
	end

	-- ignore comments and white space
	for _,tt in ipairs(lexer.ignore) do
		local exp = tt[2]

		match = string.match(str, "^"..exp, pos)
		if match then
			for char in match:gmatch(".") do
				if char == "\n" then
					line = line + 1
					column = 1
				else
					column = column + 1
				end
			end
			pos = pos + #match
			goto loop
		end
	end

	-- if not ignoreable, generate token for keywords
	for _,tt in ipairs(lexer.terminals) do
		local name = tt[1]
		local exp = tt[2]

		match = string.match(str, "^"..exp, pos)
		if match then
			table.insert(tokens, Token.new(name, match, line, column, str, pos))
			print("Token:", name, match, line, column)
			for _ in match:gmatch(".") do
				column = column + 1
			end
			pos = pos + #match
			goto loop
		end
	end

	return nil, string.format(
		"\27[31m\27[1mLEXICAL ERROR:\27[0m Can't process token (line %d, column %s):\n%s\nPrevious token: \"%s\" (%s)",
		line, column,
		prettyfile.simple(str, pos),
		tokens[#tokens].value,
		tokens[#tokens].id
	)
end

return lexer
