local p = {}

local Token = require "token"
local prettyfile = require "prettyfile"


local rules = {
	
}



-- rule*
function p.grammar_unrestricted(tokens, pos, rule) -- return {ast}
	local t = {}
	local ast
	local err = ""
	while true do
		ast, pos, err = rule(tokens, pos)
		if ast then
			table.insert(t, ast)
		else
			return t, pos, err
		end
	end
end

function p.grammar_or(tokens, pos, rules)
	local res, _pos, err
	local errs = {}

	for _,rule in ipairs(rules) do
		res, _pos, err = rule(tokens, pos)
		if res then
			return res, _pos, err
		else
			table.insert(errs, err)
		end
	end

	return nil, pos, errs
end

-- TKN
function p.rule_terminal(tokens, pos, id, value) -- return TKN
	local tkn = tokens[pos]
	local cond = tkn.id == id
	if value then cond = cond and tkn.value == value end
	if cond then
		return tkn, pos+1, ""
	else
		return nil, pos, string.format(
			"Expected '%s%s'",
			id,
			value and "("..value..")" or ""
		)
	end
end

function p.rule_list_of(tokens, pos, rule)
	local list = {id="list"}
	local res, err
	while true do
		res, pos, err = rule(tokens, pos)
		if res then
			table.insert(list, res)
			if p.rule_terminal(tokens, pos, ",") == nil then
				return list, pos, ""
			else
				pos = pos+1
			end
		else
			-- shouldn't end in anything other than a list element
			return nil, pos, string.format(err.." >> list")
		end
	end
end

-- rule_xxx: tokens -> pos -> (ast, error)
function p.rule_file(tokens, pos)
	local ast = {
		nil, -- export
		{}, -- imports
		{},  -- statements
		id="file",
		export=1,
		imports=2,
		statements=3
	}
	local res, err

	local next_tkn = tokens[pos]
	if next_tkn and next_tkn.id=="NAME" and next_tkn.value=="export" then
		ast[1], pos, err = p.rule_s_export(tokens, pos)
		if not ast[1] then return nil, pos, err end
		next_tkn = tokens[pos]
	end

	while next_tkn and next_tkn.id=="NAME" and next_tkn.value=="import" do
		res, pos, err = p.rule_s_import(tokens, pos)
		if not res then return nil, pos, err end

		table.insert(ast[2], res)
		next_tkn = tokens[pos]
	end

	ast[3], pos, err = p.grammar_unrestricted(tokens, pos, p.rule_global_stmt)

	-- check if reached EOF, error if not
	if pos > #tokens then
		return ast, pos, ""
	else
		return nil, pos, err
	end
end

function p.rule_s_export(tokens, pos)
	local ast = {
		{}, -- signatures
		id="s_export",
		signatures=1
	}
	local err_app = " >> export statement"
	local res, err

	res, pos, err = p.rule_terminal(tokens, pos, "NAME", "export")
	if not res then return nil, pos, err..err_app end
	res, pos, err = p.rule_terminal(tokens, pos, "{")
	if not res then return nil, pos, err..err_app end
	
	res, pos, err = p.rule_list_of(tokens, pos, p.rule_signature)
	if not res then return nil, pos, err.." of \"signature\""..err_app end
	ast[1] = res

	res, pos, err = p.rule_terminal(tokens, pos, "}")
	if not res then return nil, pos, err..err_app end
	res, pos, err = p.rule_terminal(tokens, pos, ";")
	if not res then return nil, pos, err..err_app end

	return ast, pos, ""
end

function p.rule_s_import(tokens, pos)
	local ast = {
		"", -- name
		"", -- rename
		{}, -- signatures
		id="s_import",
		name=1,
		rename=2,
		signatures=3
	}
	local err_app = " >> import statement"
	local res, err

	res, pos, err = p.rule_terminal(tokens, pos, "NAME", "import")
	if not res then return nil, pos, err..err_app end
	ast[ast.name], pos, err = p.rule_terminal(tokens, pos, "NAME")
	if not ast[ast.name] then return nil, pos, err..err_app end

	res, pos, err = p.rule_terminal(tokens, pos, "NAME", "as")
	if res then
		ast[ast.rename], pos, err = p.rule_terminal(tokens, pos, "NAME")
		if not ast[ast.rename] then return nil, pos, err.." >> module renaming"..err_app end
	end

	res, pos, err = p.rule_terminal(tokens, pos, "{")
	if not res then return nil, pos, err..err_app end

	ast[ast.signatures], pos, err = p.rule_list_of(tokens, pos, p.rule_signature)
	if not ast[ast.signatures] then return nil, pos, err.." of \"signature\""..err_app end

	res, pos, err = p.rule_terminal(tokens, pos, "}")
	if not res then return nil, pos, err..err_app end

	res, pos, err = p.rule_terminal(tokens, pos, ";")
	if not res then return nil, pos, err..err_app end

	return ast, pos, ""
end

function p.rule_global_stmt(tokens, pos)
	local res, err

	res, pos, err = p.grammar_or(tokens, pos, {
		p.s_empty,
		p.s_prog,
		p.s_biop,
		p.s_type,
		p.s_enum
	})
	if res then return res, pos, err end

	return nil, pos, string.format(
		"Expected a global statement (%s | %s | %s | %s | %s)",
		err[1] or "",
		err[2] or "",
		err[3] or "",
		err[4] or "",
		err[5] or ""
	)
end

function p.rule_s_empty(tokens, pos)
	local ast = {
		id="s_empty",
	}
	local err_app = " >> empty statement"
	local res, err

	res, pos, err = p.rule_terminal(tokens, pos, ";")
	if not res then return nil, pos, err..err_app end

	return ast, pos, ""
end


function p.rule_s_prog(tokens, pos)
	local ast = {
		nil, -- signature
		nil, -- exp
		id="s_prog",
		signature=1,
		exp=2,
	}
	local err_app = " >> program statement"
	local res, err

	ast[ast.signature], pos, err = p.rule_signature(tokens, pos)
	if not ast[ast.signature] then return nil, pos, err..err_app end
	res, pos, err = p.rule_terminal(tokens, pos, "SYMBOL", "=")
	if not res then return nil, pos, err..err_app end
	ast[ast.signature], pos, err = p.rule_signature(tokens, pos)
	if not ast[ast.signature] then return nil, pos, err..err_app end
	res, pos, err = p.rule_terminal(tokens, pos, ";")
	if not res then return nil, pos, err..err_app end

	return ast, pos, ""
end


function p.rule_silent_type(tokens, pos)
	local type, err1, err2
	local _pos = pos

	type, pos, err1 = p.rule_t_func(tokens, _pos)
	if type then return type, pos, err1 end
	-- TODO: implement type unions
	--type, pos, err = p.rule_t_union(tokens, pos)
	--if type then return type, pos, err end
	type, pos, err2 = p.rule_silent_basic_type(tokens, _pos)
	if type then return type, pos, err2 end

	return nil, pos, "Expected a type ("..(err1 or "").." | "..(err2 or "")..")"
end

function p.rule_t_func(tokens, pos)
	local ast = {
		nil, -- arg name
		nil, -- type1
		nil, -- type2
		id="t_func",
		arg=1,
		type1=2,
		type2=3,
	}
	local err_app = " >> func type"
	local res, err
	local _pos = pos

	ast[ast.arg], pos, err = p.rule_silent_id(tokens, pos)
	res, pos, err = p.rule_terminal(tokens, pos, "SYMBOL", ":")
	if not ast[ast.arg] or not res then
		ast[ast.arg] = ""; pos = _pos
	end

	ast[ast.type1], pos, err = p.rule_silent_basic_type(tokens, pos)
	if not ast[ast.type1] then return nil, pos, err..err_app end
	res, pos, err = p.rule_terminal(tokens, pos, "SYMBOL", "->")
	if not res then return nil, pos, err..err_app end
	ast[ast.type2], pos, err = p.rule_silent_type(tokens, pos)
	if not ast[ast.type2] then return nil, pos, err..err_app end

	return ast, pos, ""
end

function p.rule_silent_basic_type(tokens, pos)
	local type, err1, err2, err3
	local _pos = pos

	type, pos, err1 = p.rule_t_addr(tokens, _pos)
	if type then return type, pos, err1.."_1" end
	-- TODO: implement structs
	--type, pos, err = p.rule_t_struct(tokens, pos)
	--if type then return type, pos, err end
	type, pos, err2 = p.rule_t_alias(tokens, _pos)
	if type then return type, pos, err2.."_2" end
	type, pos, err3 = p.rule_t_sized(tokens, _pos)
	if type then return type, pos, err3.."_3" end

	return nil, pos, "Expected a basic type ("..(err1 or "").." | "..(err2 or "").." | "..(err3 or "")..")"
end

function p.rule_t_addr(tokens, pos)
	local ast = {
		nil, -- addressed type
		id="t_addr",
		type=1,
	}
	local err_app = " >> address type"
	local res, err

	res, pos, err = p.rule_terminal(tokens, pos, "@")
	if not res then return nil, pos, err..err_app end
	ast[ast.type], pos, err = p.rule_silent_type(tokens, pos)
	if not res then return nil, pos, err..err_app end

	return ast, pos, ""
end

function p.rule_t_alias(tokens, pos)
	local ast = {
		"", -- name
		id="t_alias",
		name=1
	}
	local err

	ast[ast.name], pos, err = p.rule_silent_id(tokens, pos)
	if not ast[ast.name] then return nil, pos, err.." >> alias type" end

	return ast, pos, ""
end

function p.rule_t_sized(tokens, pos)
	local ast = {
		-1, --size
		id="t_sized",
		size=1
	}
	local err

	ast[ast.size], pos, err = p.rule_silent_int_lit(tokens, pos)
	if not ast[ast.size] then return nil, pos, err.." >> sized type" end

	return ast, pos, ""
end


function p.rule_signature(tokens, pos)
	local ast = {
		nil, -- name
		{}, -- type
		id="signature",
		name=1,
		type=2,
	}
	local err_app = " >> signature"
	local res, err

	ast[ast.name], pos, err = p.rule_silent_id(tokens, pos)
	if not ast[ast.name] then return nil, pos, err..err_app end
	res, pos, err = p.rule_terminal(tokens, pos, "SYMBOL", ":")
	if not res then return nil, pos, err..err_app end
	ast[ast.type], pos, err = p.rule_silent_type(tokens, pos) -- TODO: p.rule_super_type
	if not ast[ast.type] then return nil, pos, string.format(
		"%s%s named \"%s\"",
		err, err_app,
		ast[ast.name]["value"] or "nil"
	) end

	return ast, pos, ""
end

function p.rule_silent_id(tokens, pos)
	local terminal = tokens[pos]
	if terminal.id ~= "NAME" and terminal.id ~= "SYMBOL" then
		return nil, pos, string.format(
			"Expected NAME or SYMBOL but got '%s'",
			terminal.id
		)
	end

	return terminal, pos+1, ""
end

function p.rule_silent_int_lit(tokens, pos)
	local lit = tokens[pos]
	if lit.id == "DECIMAL" or
	   lit.id == "HEX" or
	   lit.id == "BIN" or
	   lit.id == "OCT" or
	   lit.id == "ZERO"
	then
		return lit, pos+1, ""
	end
	
	return nil, pos, "Expected INTEGER"
end



function p.parse(tokens)
	local ast, pos, err = p.rule_file(tokens, 1)
	if not ast then
		local bad_tkn = tokens[pos]
		return nil, string.format(
			"\27[31m\27[1mSYNTAX ERROR:\27[0m %s (line %d, column %s):\n%s",
			err,
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
			if ast.id then
				str = string.rep(ind_s, indent) .. ast.id .. ":\n"
				indent = indent + 1
			end
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