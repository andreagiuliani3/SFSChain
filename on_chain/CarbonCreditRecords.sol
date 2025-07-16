// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/// @title MyToken with User Registry and Fungible Tokens + Permit
/// @notice Manages user registration and fungible ERC20 tokens with Permit support and transfers between accounts
contract CarbonCreditRecords is ERC20, ERC20Burnable, ERC20Permit {

    /// @notice Structure for storing user information
    struct User {
        string name;
        string lastName;
        string userRole;
        bool isRegistered;
    }

    /// @notice Structure for storing operations performed by users 
    struct Operation{
        string actionType; 
        string description;
        uint256 timestamp; 
        uint256 co2emissions;
 }
    
    /// @notice Structure for storing green actions performed by users
    struct GreenAction{
        string description;
        uint256 timestamp; 
        uint256 co2Saved;
    } 

    /// @notice Address of the contract owner
    address public owner;

    mapping(address => User) public users;
    mapping(address => bool) public authorizedEditors;
    mapping(address => Operation[]) public operations;
    mapping(address => GreenAction[]) public greenActions;

    /// @notice Initial amount of tokens granted to a user upon registration
    uint256 public constant INITIAL_TOKENS_ON_REGISTRATION = 10;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event UserRegistered(address indexed user, string name, string lastName, string userRole);
    event UserUpdated(address indexed user, string name, string lastName, string userRole);
    event TokensTransferred(address indexed from, address indexed to, uint256 amount);
    event TokensAdded(address indexed to, uint256 amount);
    event TokensRemoved(address indexed from, uint256 amount);
    event OperationRegistered(address indexed user, string actionType, string description, uint256 timestamp, uint256 co2emissions);
    event GreenActionRegistered(address indexed user, string description, uint256 timestamp, uint256 co2Saved);

    /// @notice Constructor: Initializes the ERC20 token and sets the owner.
    constructor() ERC20("CarbonCredit", "CCT") ERC20Permit("CarbonCredit") {
        owner = msg.sender;
        authorizedEditors[msg.sender] = true;
    }

    // Modifiers

    /// @dev Limits access to the owner of the contract
    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    /// @dev Limits access to the owner or an authorized editor
    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedEditors[msg.sender], "Access denied: caller is not the owner or an authorized editor.");
        _;
    }

    // Owner management

    /// @notice Transfer ownership of the contract to a new address
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "New owner cannot be zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    /// @notice Authorizes a new editor
    function authorizeEditor(address editor) external onlyOwner {
        authorizedEditors[editor] = true;
    }

    /// @notice Revokes an editor's authorization
    function revokeEditor(address editor) external onlyOwner {
        authorizedEditors[editor] = false;
    }

    // Functional methods

    /// @notice Registers a new user with initial tokens (only owner)
    function addUser(address userAddress, string memory name, string memory lastName, string memory userRole ) public onlyOwner() {
        require(!users[userAddress].isRegistered, "User already registered");
        users[userAddress] = User(name, lastName, userRole, true);
        authorizedEditors[userAddress] = true;
        _mint(userAddress, INITIAL_TOKENS_ON_REGISTRATION);
        emit UserRegistered(userAddress, name, lastName, userRole);
        emit TokensAdded(userAddress, INITIAL_TOKENS_ON_REGISTRATION);
    }

    /// @notice Updates user information (only owner or authorized editor)
    function updateUser(string memory name, string memory lastName, string memory userRole) public onlyAuthorized {
        require(users[msg.sender].isRegistered, "User not registered");
        users[msg.sender].name = name;
        users[msg.sender].lastName = lastName;
        users[msg.sender].userRole = userRole;
        emit UserUpdated(msg.sender, name, lastName, userRole);
    }

    /// @notice Registers an operation and updates the user’s token balance and history (only owner or authorized editor)
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

    /// @notice Retrieves the operations performed by a user
    function getOperations(address user) external view returns (Operation[] memory) {
        return operations[user];
    }

    /// @notice Registers a green action, adds token credits, and stores the action in user history (only owner or authorized editor)
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

    /// @notice Retrieves the green actions performed by a user
    function getGreenActions(address user) external view returns (GreenAction[] memory) {
        return greenActions[user];
    }

    /// @notice Adds tokens (credits) to a registered account (only owner or authorized editor)
    function addToken(address user, uint256 amount) public onlyAuthorized {
        require(users[user].isRegistered, "Recipient not registered");
        require(user != msg.sender, "Cannot mint tokens to yourself"); /// Evita che un utente possa chiamare la funzione per aggiungere token a se stesso
        _mint(user, amount);
        emit TokensAdded(user, amount);
    }

    /// @notice Removes tokens (burns) from a registered account (only owner or authorized editor)
    function removeToken(address from, uint256 amount) public onlyAuthorized {
        require(users[from].isRegistered, "Account not registered");
        require(from != msg.sender, "Cannot burn your own tokens");
        _burn(from, amount);
        emit TokensRemoved(from, amount);
    }

    /// @notice Transfers tokens from the sender to another registered user
    function transferToken(address to, uint256 amount) public onlyAuthorized returns (bool) {
        require(users[msg.sender].isRegistered, "Sender not registered");
        require(users[to].isRegistered, "Receiver not registered");
        bool success = super.transfer(to, amount);
        emit TokensTransferred(msg.sender, to, amount);
        return success;
    }

    /// @notice Checks the balance of the sender (only owner or authorized editor)
    function checkBalance() public onlyAuthorized view returns (uint) {
         return balanceOf(msg.sender);
    }

    /// @notice Checks if the sender is registered (only owner or authorized editor)
    function isRegistered() public view returns (bool) {
        return users[msg.sender].isRegistered;
    }
}