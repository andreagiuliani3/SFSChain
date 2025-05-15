// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract CarbonCreditRecords is ERC20 {
    struct User {
        string name;
        string lastName;
        string role;
        string email;
        bool exists;
    }

    mapping(address => User) private users;

    event UserRegistered(address indexed userAddress, string name, string lastName, string role, string email);
    event UserUpdated(address indexed userAddress, string name, string lastName, string role, string email);
    event OperationExecuted(address indexed userAddress, string operationType, uint256 tokenAmount);

    constructor() ERC20("CarbonCreditToken", "CCT") {
        // Nessun owner, nessun admin
    }

    // Registrazione utente (register_entity)
    function registerUser(string memory name, string memory lastName, string memory role, string memory email) public {
        require(!users[msg.sender].exists, "User already registered");
        users[msg.sender] = User(name, lastName, role, email, true);
        emit UserRegistered(msg.sender, name, lastName, role, email);
    }

    // Aggiornamento dati utente
    function updateUser(string memory name, string memory lastName, string memory role, string memory email) public {
        require(users[msg.sender].exists, "User not registered");
        users[msg.sender] = User(name, lastName, role, email, true);
        emit UserUpdated(msg.sender, name, lastName, role, email);
    }

    // Lettura dati utente
    function getUser(address userAddress) public view returns (string memory, string memory, string memory, string memory) {
        require(users[userAddress].exists, "User not found");
        User memory u = users[userAddress];
        return (u.name, u.lastName, u.role, u.email);
    }

    // Lettura saldo token (get_token_balance)
    // Questa funzione è già ereditata da ERC20 come "balanceOf(address)"
    // ma la riscrivo per chiarezza
    function getTokenBalance(address userAddress) public view returns (uint256) {
        return balanceOf(userAddress);
    }

    // Trasferimento token (transfer_tokens)
    // Funzione "transfer" già esiste in ERC20, puoi chiamarla direttamente
    // Se vuoi, puoi fare un wrapper per chiarezza:
    function transferTokens(address to, uint256 amount) public returns (bool) {
        return transfer(to, amount);
    }

    // Burn token (burn_tokens)
    function burnTokens(uint256 amount) public {
        _burn(msg.sender, amount);
    }

    // Reward tokens (reward_tokens)
    function rewardUser(uint256 rewardAmount) public {
        require(users[msg.sender].exists, "User not registered");
        _mint(msg.sender, rewardAmount);
    }
}
