
local prettyfile = {}

function prettyfile.simple(str, pos)
	local start_pos = pos
	while start_pos > 1 and string.sub(str, start_pos-1, start_pos-1) ~= "\n" do
		start_pos = start_pos - 1
	end

	local end_pos = pos
	while end_pos < #str and string.sub(str, end_pos+1, end_pos+1) ~= "\n" do
		end_pos = end_pos + 1
	end

	local line_number = 1
	for i = 1,pos do
		if string.sub(str, i, i) == "\n" then
			line_number = line_number + 1
		end
	end

	local line = string.sub(str, start_pos, end_pos)
	local padding = string.match(line, "%s*")

	return string.format(
		"\27[31m%d |\27[0m %s\n\27[31m%s |\27[31m %s\27[1m^\27[0m",
		line_number,
		line,
		string.rep(" ", tostring(line_number):len()),
		padding .. string.rep(" ", pos - start_pos - #padding)
	)
end

return prettyfile
