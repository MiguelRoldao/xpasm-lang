
import {
	var I : a => a@;
	var v0 : u16;
	var v1 : u16;
	var v2 : u16;
	var v3 : u16;
	var v4 : u16;
	var v5 : u16;
};

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

const main : () {
	@I = D1;
	Sub11;
	Sub5;

	do {
		v0 = v0 + 1;
		sprite v0 v1 1;
	} while (v0 != 37);

	do {
		v0 = v0 - 1;
		sprite v0 v1 1;
		v0 = 26;
		sprite v0 v1 1;
		v0 = 37;
	} while (v0 != 37);

	tail L3;
};

L3 : () {
	do {
		v4 = random 0b1110000;
	} while (v4 == 112);

	v3 = random 0b11;
	v0 = 30;
	v1 = 3;
	Sub1;

	tail L4;
};

L4 {
	[delay] = [v5];
	<-;
}