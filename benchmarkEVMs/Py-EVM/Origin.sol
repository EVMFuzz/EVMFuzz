pragma solidity ^0.4.18;
contract Origin {
  address public owner;
  /** 
   * @dev The Ownable constructor sets the original `owner` 
   * of the contract to the sender account.
   */
  function Origin() {
    owner = msg.sender;
  }
}

