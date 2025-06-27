// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/// @title MyToken with User Registry and Fungible Tokens + Permit
/// @notice Gestisce registrazione utenti e token ERC20 fungibili con supporto Permit e trasferimenti tra account
contract CarbonCreditRecords is ERC20, ERC20Burnable, ERC20Permit {

    /// @notice Struttura per memorizzare le informazioni degli utenti
    struct User {
        string name;
        string lastName;
        string userRole;
        bool isRegistered;
    }

    /// @notice Struttura per memorizzare le operazioni 
    struct Operation{
        string actionType; 
        string description;
        uint256 timestamp; 
        uint256 co2emissions;
 }
    
    /// @notice Struttura per memorizzare le azioni verdi
    struct GreenAction{
        string description;
        uint256 timestamp; 
        uint256 co2Saved;
    } 

    address public owner;
    mapping(address => User) public users;
    mapping(address => bool) public authorizedEditors;
    mapping(address => uint256) public balance;
    mapping(address => Operation[]) public operations;
    mapping(address => GreenAction[]) public greenActions;


    uint256 public constant INITIAL_TOKENS_ON_REGISTRATION = 10;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event UserRegistered(address indexed user, string name, string lastName, string userRole);
    event UserUpdated(address indexed user, string name, string lastName, string userRole);
    event TokensTransferred(address indexed from, address indexed to, uint256 amount);
    event TokensAdded(address indexed to, uint256 amount);
    event TokensRemoved(address indexed from, uint256 amount);
    event OperationRegistered(address indexed user, string actionType, string description, uint256 timestamp, uint256 co2emissions);
    event GreenActionRegistered(address indexed user, string description, uint256 timestamp, uint256 co2Saved);
    
    /// @notice Imposta il deployer come owner e lo autorizza come editor
    event Debug(string tag);

    constructor() ERC20("CarbonCredit", "CCT") ERC20Permit("CarbonCredit") {
        owner = msg.sender;
        authorizedEditors[msg.sender] = true;
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
    function addUser(address userAddress, string memory name, string memory lastName, string memory userRole ) public onlyOwner() {
        require(!users[userAddress].isRegistered, "User already registered");
        users[userAddress] = User(name, lastName, userRole, true);
        authorizedEditors[userAddress] = true;
        _mint(userAddress, INITIAL_TOKENS_ON_REGISTRATION);
        emit UserRegistered(userAddress, name, lastName, userRole);
        emit TokensAdded(userAddress, INITIAL_TOKENS_ON_REGISTRATION);
    }

    /// @notice Aggiorna i dati di un utente registrato
    function updateUser(string memory name, string memory lastName, string memory userRole) public onlyAuthorized {
        require(users[msg.sender].isRegistered, "User not registered");
        users[msg.sender].name = name;
        users[msg.sender].lastName = lastName;
        users[msg.sender].userRole = userRole;
        emit UserUpdated(msg.sender, name, lastName, userRole);
    }

    function registerOperation(string memory actionType, string memory description, int256 delta, uint256 co2emissions) public onlyAuthorized {
        require(users[msg.sender].isRegistered, "User not registered");

        if (delta < 0) {
            uint256 amountToBurn = uint256(-delta);
            require(balanceOf(msg.sender) >= amountToBurn, "Insufficient credits to burn");
            _burn(msg.sender, amountToBurn);
            emit TokensRemoved(msg.sender, amountToBurn);
        } else if (delta > 0) {
            _mint(msg.sender, uint256(delta));
            emit TokensAdded(msg.sender, uint256(delta));
        }

        Operation memory newOperation = Operation({
            actionType: actionType,
            description: description,
            timestamp: block.timestamp,
            co2emissions: co2emissions
        });
        operations[msg.sender].push(newOperation);
        emit OperationRegistered(msg.sender, actionType, description, block.timestamp, co2emissions);
    }

    function getOperations(address user) external view returns (Operation[] memory) {
        return operations[user];
    }

    function registerGreenAction(string memory description, uint256 co2Saved) public onlyAuthorized {
    require(users[msg.sender].isRegistered, "User not registered");

    GreenAction memory newGreenAction = GreenAction({
        description: description,
        timestamp: block.timestamp,
        co2Saved: co2Saved 
    });
    greenActions[msg.sender].push(newGreenAction);
    emit GreenActionRegistered(msg.sender, newGreenAction.description, newGreenAction.timestamp, newGreenAction.co2Saved);

    uint256 creditsToAdd = co2Saved; 

    _mint(msg.sender, creditsToAdd);
    emit TokensAdded(msg.sender, creditsToAdd);
    }

    function getGreenActions(address user) external view returns (GreenAction[] memory) {
        return greenActions[user];
    }

    /// @notice Aggiunge token (crediti) a un account registrato (solo owner o editor autorizzato)
    function addToken(address user, uint256 amount) public onlyAuthorized {
        require(users[user].isRegistered, "Recipient not registered");
        require(user != msg.sender, "Cannot mint tokens to yourself"); /// Evita che un utente possa chiamare la funzione per aggiungere token a se stesso
        _mint(user, amount);
        emit TokensAdded(user, amount);
    }

    /// @notice Rimuove token (crediti) da un account registrato (solo owner o editor autorizzato)
    function removeToken(address from, uint256 amount) public onlyAuthorized {
        require(users[from].isRegistered, "Account not registered");
        require(from != msg.sender, "Cannot burn your own tokens");
        _burn(from, amount);
        emit TokensRemoved(from, amount);
    }

    /// @notice Trasferisce token tra account registrati
    function transferToken(address to, uint256 amount) public onlyAuthorized returns (bool) {
        require(users[msg.sender].isRegistered, "Sender not registered");
        require(users[to].isRegistered, "Receiver not registered");
        bool success = super.transfer(to, amount);
        emit TokensTransferred(msg.sender, to, amount);
        return success;
    }

    
    function checkBalance() public onlyAuthorized view returns (uint) {
         return balanceOf(msg.sender);
    }

    function isRegistered() public onlyAuthorized() view returns (bool) {
        return users[msg.sender].isRegistered;
    }
}
