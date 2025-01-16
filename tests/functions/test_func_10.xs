


print:(str:@1) = {
	<-;
};



main:() = {
	// to get the value
	adr:@ = hello + [id];
	c:1 = [adr];

	// build a null terminated string
	cs:@1 = $2;
	[cs] = c;
	[cs+1] = '\0';
	print(cs);
	<-;
};


// declare constant
my_const:1 = 4;
// will be optimized out of rom most certainly

// declare byte on rom
!id:@1 = {3};

// declare byte on ram: Can't!!!
// Need to reserve 1 byte in ram and initialize
// somewhere in code!
// this is a global, prefer local if possible!
ram:@1 = $1;

hello:@1 = "Hello, World!\0";
