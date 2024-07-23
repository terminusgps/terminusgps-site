local function print_line(length)
	local line = {}
	for i = 1, length do
		line[i] = "*"
	end
	return line
end

print(for c=1 in print_line(8) do print(c) end)
