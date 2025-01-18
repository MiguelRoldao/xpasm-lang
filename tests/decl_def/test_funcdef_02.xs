.. valid function declaration doesn't clash with function definition. As
.. the funtion parts are part of their signature

import m {
	same : u8 (a u8);
};

same : u16 (a u8) {
	ret a :> u16;
};



