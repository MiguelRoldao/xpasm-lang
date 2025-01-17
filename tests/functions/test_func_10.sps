
.. print declaration
import io {print : u8@ -> void};


hello : u8@ = "Hello, World!"; .. Using "" instead of '' appends \0 in the end */

id : u8 = 4;

main : argc u32 -> argv u8@[] -> void = {
	adr : u8@ = @(hello[id]);
	c : u8 = adr[0];

	..cs:@d8 = alloca <d8> 2;
	..cs[0] = c;
	..cs[1] = '\0'; 
	cs : d8[2];
	cs = [c, '\0'];
	print cs;
};


main : 0 -> 0 = hello[id] |> [, '\0'] |> print;

.. main : 0 -> 0 = print <| [, '\0'] hello[id];



