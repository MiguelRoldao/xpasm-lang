?@add:16 (%a:16, %b:16);

!@main:8 () {
	%a:8 = 4;
	%b:8 = 5;
	%res:8 = call @add (%a, %b);
	:.@while;
		goto .@end if %res == 0;
		// nothing really
		goto .@while;
	:.@end;
	return %res;
};