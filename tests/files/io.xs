import "math.xs" @add;
export @print;


?@print:0 (%str:@8);

@double:16 (%a:16) {
	%res = call @add (%a, %a);
	return %res;
}