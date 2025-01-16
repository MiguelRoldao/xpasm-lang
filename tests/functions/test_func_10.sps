
.. print declaration
import io as io {print : a:8 -> 0};


hello : @d8 = "Hello, World!"; -[ Using "" instead of '' appends \0 in the end */ --]

id : d8 = 4;

main : argc:32 -> argv:@@8 -> 0 = {
	adr:@ = hello[id];
	c:d8 = adr[0];

	..cs:@d8 = alloca <d8> 2;
	..cs[0] = c;
	..cs[1] = '\0'; 
	cs:[2]d8;
	cs = [c, '\0'];
	print cs;
};


main : 0 -> 0 = hello[id] |> [, '\0'] |> print;

.. main : 0 -> 0 = print <| [, '\0'] hello[id];



