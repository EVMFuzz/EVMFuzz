

contract MyContract{
	bool public flag;
	uint public money;

	constructor() public{
		flag = false;
		money = 0;
	}
	
	function multiPath(uint a, uint b) public returns (uint){
		uint d;
		if (a > b) {
			uint c1 = a + b;
			uint d1 = c1;
			assert(c1 != d1);
			d = d1;
		}
		if (a < b) {
			uint c2 = a - b;
			assert(c2 >= 0);
			d = c2;
		}
		if (a == b) {
			for (uint i = 0; i < 10; ++i) {
				a += b;
			}
			d = a;
		}
		if (a >= b) {
			uint c3 = a * b;
			uint d3 = 20;
			assert(c3 != d3);
			d = c3;
		}
		if (a <= b) {
			uint c4 = a / b;
			uint d4 = c4 - 1;
			assert(d4 > 10);
			d = d4;
		}
		if (a != b) {
			uint x;
			uint y;
			if (a > b) {
				x = b;
				y = a;
			}
			else {
				x = a;
				y = b;
			}
			
			d = x;
		}
		return d;
	}
}
