pragma solidity >0.4.24;

contract Test {
  constructor() public { b = 0x12345678901234567890123456789012; }
  event Event(uint indexed a, bytes32 b);
  event Event2(uint indexed a, bytes32 b);
  function foo(uint a) public { emit Event(a, b); }
  bytes32 b;
}