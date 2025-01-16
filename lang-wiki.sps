
main : ()
main = 



-- core types represent data size only
-- base operations for core types (eg. `+`, `&`) are implemetned natively
d0  -- void
d1  --  1 bit
d8  --  8 bit
d16 -- 16 bit
d24 -- 24 bit
d32 -- 32 bit
d64 -- 64 bit
@   -- ptr size of implementation


-- unsigned int type definition
type uint = d32;
-- type aliases still need definition of their own functions. Just because
-- d32 has a defined '+' function, the function '+' for the uint type still
-- needs to be implemented.


type String = {start:ptr len:int};


-- int type definition
type int = d32;

-- necessary. The type usage is very strict. The casts must be used.
-- the ` informs that the first argument is prefixed.
(+) :: (int:a, int:b) int = (a:d32 + b:d32):int


-- every type needs to define a cast operation if it so wishes to use casts
cast_inc :: (int) a = cast_inc_extend

-- core cast functions are
cast_no     -- casting is not allowed (default)
cast_extend -- bxxx -> bbbbbxxx
cast_zero   -- bxxx -> 0000bxxx





export {hello::int, bye::8};

type Character = {
	pos :: Vec2,
	sprite :: Image,
	script :: () d0
};


type MySession = ?Int -> !Int -> End;

-- enum elements act as literals of the type of var that they are being
-- assigned to.
enum STATE = {IDLE=0, ERROR=-1, RUN=2, DELAY};



-- casting an integer to a function:
-- although casts for int are not implemented, casts ARE implemented for functions.
-- here the cast is inferred. VERY UNSAFE.
add :: int -> int -> int = 0x4bff0080;