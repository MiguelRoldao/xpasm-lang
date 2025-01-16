

?I:@;

$L5 = 0x23C;
$L6 = 0x250;
$Sub1 = 0x25C;
$Sub2 = 0x272;
$Sub3 = 0x284;
$Sub4 = 0x296;
$D1 = 0x2B4;
$Sub5 = 0x2B6;
$D2 = 0x2C4;
$Sub6 = 0x334;
$Sub7 = 0x340;
$Sub8 = 0x35E;
$Sub9 = 0x372;
$L13 = 0x390;
$L14 = 0x394;
$L15 = 0x3A6;
$Sub10 = 0x3C0;
$Sub11 = 0x3E6;
$D3 = 0x700;
$D4 = 0x804;

!main:() {
	[I] = D1;
	Sub11();
	Sub5();

		@loop1;
	[v0] = [v0] + 1;
	sprite(v0, v1, 1);
	-> loop1 if [v0] != 37;

		@loop2;
	[v0] = [v0] - 1;
	sprite(v0, v1, 1);
	[v0] = 26;
	sprite(v0, v1, 1);
	[v0] = 37;
	-> loop2 <> ([v1] != 0);

	-> L3;
};

L3 {
	@loop1;
	[v4] = random(0b1110000);
	-> loop1 if [v4] = 112;

	[v3] = random(0b11);
	[v0] = 30;
	[v1] = 3;
	Sub1();

	-> L4;
}

L4 {
	[delay] = [v5];
	<-;
}