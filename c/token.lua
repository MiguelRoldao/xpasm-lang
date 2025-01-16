local t = {}

function t.new(id, value, line, column, program, cursor)
	local tkn = {
		id = id or "",
		value = value or "",
		line = line or 0,
		column = column or 0,
		program = program or " ",
		cursor = cursor or 1,
	}

	return tkn
end

return t