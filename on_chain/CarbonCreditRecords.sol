// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/// @title MyToken with User Registry and Fungible Tokens + Permit
/// @notice Gestisce registrazione utenti e token ERC20 fungibili con supporto Permit e trasferimenti tra account
contract CarbonCreditRecords is ERC20, ERC20Burnable, ERC20Permit {
    struct User {
        string name;
        string lastName;
        bool isRegistered;
    }

    address public owner;
    mapping(address => User) public users;
    mapping(address => bool) public authorizedEditors;

    uint256 public constant INITIAL_TOKENS_ON_REGISTRATION = 10 * 10**18;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event UserRegistered(address indexed user, string name, string lastName);
    event UserUpdated(address indexed user, string name, string lastName);
    event TokensTransferred(address indexed from, address indexed to, uint256 amount);
    event TokensAdded(address indexed to, uint256 amount);
    event TokensRemoved(address indexed from, uint256 amount);

    /// @notice Imposta il deployer come owner e lo autorizza come editor
    event Debug(string tag);

    constructor()
        ERC20("CarbonCredit", "CCT")
        ERC20Permit("CarbonCredit")
    {
        emit Debug("ERC20 fatto");
        emit Debug("ERC20Permit fatto");

        owner = msg.sender;
        emit Debug("owner settato");

        authorizedEditors[msg.sender] = true;
        emit Debug("editor autorizzato");
    }

    // Modifiers

    /// @dev Limita l'accesso al solo proprietario
    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    /// @dev Limita l'accesso al proprietario o editor autorizzato
    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedEditors[msg.sender], "Access denied: caller is not the owner or an authorized editor.");
        _;
    }

    // Owner management

    /// @notice Trasferisce la proprietà a un nuovo indirizzo
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "New owner cannot be zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    /// @notice Autorizza un nuovo editor
    function authorizeEditor(address editor) external onlyOwner {
        authorizedEditors[editor] = true;
    }

    /// @notice Rimuove l'autorizzazione a un editor
    function revokeEditor(address editor) external onlyOwner {
        authorizedEditors[editor] = false;
    }

    // Functional methods

    /// @notice Registra un nuovo utente e assegna token iniziali
    function addUser(string calldata name, string calldata lastName) external {
        require(!users[msg.sender].isRegistered, "User already registered");
        users[msg.sender] = User(name, lastName, true);
        _mint(msg.sender, INITIAL_TOKENS_ON_REGISTRATION);
        emit UserRegistered(msg.sender, name, lastName);
        emit TokensAdded(msg.sender, INITIAL_TOKENS_ON_REGISTRATION);
    }

    /// @notice Aggiorna i dati di un utente registrato
    function updateUser(string calldata name, string calldata lastName) external {
        require(users[msg.sender].isRegistered, "User not registered");
        users[msg.sender].name = name;
        users[msg.sender].lastName = lastName;
        emit UserUpdated(msg.sender, name, lastName);
    }

    /// @notice Aggiunge token (crediti) a un account registrato (solo owner o editor autorizzato)
    function addTokens(address to, uint256 amount) external onlyAuthorized {
        require(users[to].isRegistered, "Recipient not registered");
        _mint(to, amount);
        emit TokensAdded(to, amount);
    }

    /// @notice Rimuove token (crediti) da un account registrato (solo owner o editor autorizzato)
    function removeTokens(address from, uint256 amount) external onlyAuthorized {
        require(users[from].isRegistered, "Account not registered");
        _burn(from, amount);
        emit TokensRemoved(from, amount);
    }

    /// @notice Trasferisce token tra account registrati
    function transferTokens(address to, uint256 amount) external returns (bool) {
        require(users[msg.sender].isRegistered, "Sender not registered");
        require(users[to].isRegistered, "Recipient not registered");
        bool success = super.transfer(to, amount);
        emit TokensTransferred(msg.sender, to, amount);
        return success;
    }
}
