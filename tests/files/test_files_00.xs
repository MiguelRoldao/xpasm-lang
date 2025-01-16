
from "io.xs" import (@print -> @io_print);
from "math.xs" import (@add);

@main:0 () {
	/* this saves the label (address) */
	%s:@8 = @hello;
	call @io_print (%s);

	/* to get the value */
	%c:8 = [@hello];

	/* build a null terminated string */
	%cs:@8 = $8*2;
	[%cs] = %c;
	[%cs+1] = '\0';
	call @io_print (%cs);

}


@hello:8 = "Hello, World!";