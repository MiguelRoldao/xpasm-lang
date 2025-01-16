local p = {}

local Token = require "token"
local prettyfile = require "prettyfile"

local parser_error = {}

function parser_error.new (rule, pos, error)
	if error then
		return {
			rule = rule or nil,
			pos = pos or 1,
			child = error or ""
		}
	else
		return nil
	end
end

function parser_error.dump (error)
	local str = ""

	if type (error.child) == "string" then
		str = error.child
	else
		str = parser_error.dump (error.child)
	end

	if not error.rule._silent or error.rule._error then
		str = str .. " >> " .. error.rule._name
	end

	return str
end

function parser_error.best_match (errors)
	if #errors < 1 then
		return
	end
	local best = errors[#errors]
	local best_pos = best.pos
	for _,error in ipairs(errors) do
		local error_pos = parser_error.get_leaf(error).pos
		if error_pos > best_pos then
			best = error
			best_pos = error_pos
		end
	end
	return best
end

function parser_error.get_leaf (error)
	if type(error.child) == "string" then
		return error
	else
		return parser_error.get_leaf(error.child)
	end
end

p.rules = {
	file = {
		_id = "file",
		_name = "file",
		{"?", "s_export"},
		{"*", "s_import"},
		{"*", "g_stmt"},
		{"$"},
	},
	s_export = {
		_id = "s_export",
		_name = "export statement",
		{" ", "NAME", "export"},
		{" ", "{"},
		{"!", "signature_list"},
		{" ", "}"},
		{" ", ";"},
	},
	s_import = {
		_id = "s_import",
		_name = "import statement",
		{" ", "NAME", "import"},
		{"#", "NAME"},
		{"?", "s_import_alias"},
		{" ", "{"},
		{"!", "signature_list"},
		{" ", "}"},
		{" ", ";"},
	},
	s_import_alias = {
		_id = "s_import_alias",
		_name = "import alias",
		{" ", "NAME", "as"},
		{"#", "NAME"},
	},
	signature_list = {
		_id = "signature_list",
		_name = "signature list",
		{"!", "signature"},
		{"*", "_signature_list_elem"},
	},
	_signature_list_elem = {
		_id = "_signature_list_elem",
		_name = "signature list element",
		_silent = true,
		{" ", ","},
		{"!", "signature"}
	},

	g_stmt = {
		_id = "g_stmt",
		_name = "global statement",
		_silent = true,
		{"|", "s_empty", "s_prog", "s_inline", "s_type", "s_enum"},
	},
	s_empty = {
		_id = "s_empty",
		_name = "empty statement",
		{" ", ";"},
	},
	s_prog = {
		_id = "s_prog",
		_name = "program statement",
		{"!", "meta_signature"},
		{" ", "SYMBOL", "="},
		{"!", "exp"},
		{" ", ";"},
	},
	s_type = {
		_id = "s_type",
		_name = "type statement",
		{"!", "id"},
		{" ", ":"}, {" ", ":"},
		{"!", "type"},
		{" ", ";"},
	},
	s_enum = {
		_id = "s_enum",
		_name = "enumerator statement",
		{"!", "id"},
		{" ", "SYMBOL", "#"},
		{" ", "{"},
		{"!", "enum_list"},
		{" ", "}"},
		{" ", ";"},
	},
	enum_list = {
		_id = "enum_list",
		_name = "enumerator list",
		{"#", "NAME"},
		{"*", "_enum_list_elem"},
	},
	_enum_list_elem = {
		_id = "_enum_list_elem",
		_name = "enumerator list element",
		_silent = true,
		{" ", ","},
		{"#", "NAME"}
	},

	type = {
		_id = "type",
		_name = "type",
		_silent = true,
		{"|", "t_union", "t_func", "basic_type"},
	},
	t_union = {
		_id = "t_union",
		_name = "union type",
		{"?", "t_union_id"},
		{"!", "basic_type"},
		{" ", "SYMBOL", "||"},
		{"!", "type"},
	},
	t_func = {
		_id = "t_func",
		_name = "function type",
		{"?", "t_func_id"},
		{"!", "basic_type"},
		{" ", "SYMBOL", "->"},
		{"!", "type"},
	},
	basic_type = {
		_id = "type",
		_name = "type",
		_silent = true,
		{"|", "t_struct", "t_addr", "t_sized", "t_alias"},
	},
	t_addr = {
		_id = "t_addr",
		_name = "address type",
		{" ", "@"},
		{"!", "type"},
	},
	t_struct = {
		_id = "t_struct",
		_name = "struct type",
		{" ", "{"},
		{"!", "type_list"},
		{" ", "}"},
	},
	t_alias = {
		_id = "t_alias",
		_name = "alias type",
		{"!", "id"},
	},
	t_sized = {
		_id = "t_sized",
		_name = "sized type",
		{"!", "intlit"},
	},
	type_list = {
		_id = "type_list",
		_name = "type list",
		{"!", "type"},
		{"*", "_type_list_elem"},
	},
	_type_list_elem = {
		_id = "_type_list_elem",
		_name = "type list element",
		_silent = true,
		{" ", ","},
		{"!", "type"}
	},

	meta_signature = {
		_id = "meta_signture",
		_name = "meta_signture",
		_silent = true,
		{"|", "inline_signature", "param_signature", "signature"},
	},
	signature = {
		_id = "signature",
		_name = "signature",
		{"!", "id"},
		{" ", ":"},
		{"!", "type"},
	},
	param_signature = {
		_id = "param_signature",
		_name = "parametrized signature",
		{"!", "id"},
		{"!", "param_list"},
		{" ", ":"},
		{"!", "type"},
	},
	inline_signature = {
		_id = "inline_signature",
		_name = "inline function signature",
		{" ", "("},
		{"!", "id"},
		{" ", ")"},
		{"!", "param_list"},
		{" ", ":"},
		{"!", "type"},
	},
	param_list = {
		_id = "param_list",
		_name = "parameter list",
		{"+", "id"},
	},

	-- terminal sets
	id = {
		_id = "id",
		_name = "identifier",
		_silent = true,
		_error = true,
		{"|", "symbol", "name"},
	},

	intlit = {
		_id = "intlit",
		_name = "intlit",
		_silent = true,
		_error = true,
		{"|", "hex", "bin", "oct", "zero", "decimal"},
	},

	-- terminal rules
	name = {
		_id = "name",
		_name = "name",
		_silent = true,
		{"#", "NAME"},
	},
	symbol = {
		_id = "name",
		_name = "name",
		_silent = true,
		{"#", "SYMBOL"},
	},
	decimal = {
		_id = "decimal",
		_name = "decimal",
		_silent = true,
		{"#", "DECIMAL"},
	},
	zero = {
		_id = "zero",
		_name = "zero",
		_silent = true,
		{"#", "ZERO"},
	},
	hex = {
		_id = "hex",
		_name = "hex",
		_silent = true,
		{"#", "HEX"},
	},
	bin = {
		_id = "bin",
		_name = "bin",
		_silent = true,
		{"#", "BIN"},
	},
	oct = {
		_id = "oct",
		_name = "oct",
		_silent = true,
		{"#", "OCT"},
	},

}


-- TKN
function p.rule_terminal(tokens, pos, id, value) -- return TKN
	if pos > #tokens then
		return nil, pos, string.format(
			"Reached EOF while looking for a '%s%s' token",
			id,
			value and "("..value..")" or ""
		)
	end
	local tkn = tokens[pos]
	local cond = tkn.id == id
	if value then cond = cond and tkn.value == value end
	if cond then
		return tkn, pos+1, nil
	else
		return nil, pos, string.format(
			"Unexpected token \"%s\"",
			tkn.value,
			id,
			value and "("..value..")" or ""
		)
	end
end

function p.rule(tokens, pos, rule)
	if not rule then
		print("RULE IS EMPTY")
		return nil, pos, "rule is nil"
	end

	--print ("Hi", rule._name)
	local ast = {}
	local errors = {}

	for i,m in ipairs(rule) do
		--print("matching", m[1], m[2])
		local res, _pos, error = nil, pos, nil
		if m[1] == " " then
			res, pos, error = p.rule_terminal(tokens, pos, m[2], m[3])
			if error then table.insert(errors, parser_error.new(rule, pos, error)) end
			if not res then
				ast=nil
				break
			end
		elseif m[1] == "#" then
			res, pos, error = p.rule_terminal(tokens, pos, m[2], m[3])
			if error then table.insert(errors, parser_error.new(rule, pos, error)) end
			if not res then
				ast=nil
				break
			end
			table.insert(ast, res)
		elseif m[1] == "!" then
			res, pos, error = p.rule(tokens, pos, p.rules[m[2]])
			if error then table.insert(errors, parser_error.new(rule, pos, error)) end
			if not res then
				ast=nil
				break
			end
			table.insert(ast, res)
		elseif m[1] == "?" then
			res, _pos, error = p.rule(tokens, pos, p.rules[m[2]])
			if error then table.insert(errors, parser_error.new(rule, pos, error)) end
			if res then
				table.insert(ast, res)
				pos = _pos
			end
		elseif m[1] == "|" then
			for _,opt in ipairs({table.unpack(m, 2)}) do
				res, _pos, error = p.rule(tokens, pos, p.rules[opt])
				if error then table.insert(errors, parser_error.new(rule, pos, error)) end
				if res then
					table.insert(ast, res)
					break
				end
			end
			if res then
				pos = _pos
			else
				ast=nil
				break
			end
		elseif m[1] == "*" then
			while true do
				res, _pos, error = p.rule(tokens, pos, p.rules[m[2]])
				if error then table.insert(errors, parser_error.new(rule, pos, error)) end
				if res then
					table.insert(ast, res)
					pos = _pos
				else
					break
				end
			end
		elseif m[1] == "$" then
			if pos <= #tokens then
				ast=nil
				table.insert(errors, parser_error.new(rule, pos, "Expected EOF"))
				break
			end
		else
			print ("Unimplemented grammar for \""..m[1].."\"")
			return nil, pos, ""
		end
	end

	--print ("Bye", rule._name, ast)

	-- return only the best matching error
	local error = parser_error.best_match (errors)
	
	if ast then
		if rule._silent then
			ast = ast[1]
			-- TODO: what about when asts are invisible and have more than
			-- one element? or none?
		else
			ast.id = rule._id
		end
	end

	return ast, pos, error

end

local function check_grammar()
	local error = false
	for _,rule in pairs(p.rules) do
		for _,step in ipairs(rule) do
			local rule_name = "not found"
			local op = step[1]

			if op == " " or op == "#" or op == "$" then
				goto continue
			elseif op == "!" or op == "?" or op == "*" then
				rule_name = step[2]
				if p.rules[rule_name] then
					goto continue
				end
			elseif op == "|" then
				for _,opt in ipairs({table.unpack(step, 2)}) do
					rule_name = opt
					if not p.rules[rule_name] then
						goto error
					end
				end
				goto continue
			end

			::error::
			print(string.format(
				"\27[31m\27[1mGRAMMAR ERROR:\27[0m Rule \"%s\" is not defined!",
				rule_name
			))
			error = true

			::continue::
			if error then return false end
		end
	end

	return true
end

function p.parse(tokens)
	if not check_grammar() then
		-- for debugging grammar only
		return nil
	end
	local ast, pos, err = p.rule(tokens, 1, p.rules.file)
	if not ast then
		local bad_tkn = tokens[parser_error.get_leaf(err).pos]
		return nil, string.format(
			"\27[31m\27[1mSYNTAX ERROR:\27[0m %s (line %d, column %s):\n%s",
			parser_error.dump(err),
			bad_tkn.line, bad_tkn.column,
			prettyfile.simple(bad_tkn.program, bad_tkn.cursor)
		)
	end
	return ast, ""
end

function p.dump_ast(ast, indent)
	local ind_s = "  "
	indent = indent or 0

	local str = ""
	if ast.id then
		if #ast > 0 then
			str = string.rep(ind_s, indent) .. ast.id .. ":\n"
			indent = indent + 1
			for i,v in ipairs(ast) do
				if not v then v = "nil" end
				str = str .. p.dump_ast(v, indent)
			end
		else
			local value = ast.value and ind_s .. ast.value or ""
			str = string.rep(ind_s, indent) .. ast.id .. value .. "\n"
		end
	else
		for i,v in ipairs(ast) do
			if not v then v = "nil" end
			str = str .. p.dump_ast(v, indent)
		end
	end

	return str
end

return p