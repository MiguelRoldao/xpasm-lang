


?@print:0 (%str:@8);



@main:0 () {
	// to get the value
	%c:8 = [@hello + @id];

	// build a null terminated string
	%cs:@8 = $2;
	[%cs] = %c;
	[%cs+1] = '\0';
	call @print(%cs);
};

!@id:8 = 3;
@hello:8 = "Hello, World!\0";
