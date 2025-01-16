/* invalid: duplicate function definition */

same : a u16 -> u16 {
	ret a;
}

same : a u16 -> u16 {
	ret a;
}
