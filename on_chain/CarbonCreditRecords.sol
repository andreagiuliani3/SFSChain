// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

//Documentation for this contract written in NatSpec format
/**
 * @title Health Care Records System
 * @dev Manages healthcare records for patients, medics, and caregivers.
 * @notice This contract is intended for demonstration purposes and not for production use.
 */
contract HealthCareRecords {
    // Structs for every type of user
    struct Users {
        string name;
        string lastName;
        string role;
        bool isRegistered;
    }

    //Struct to log actions for every previous struct
    struct ActionLog {
        uint256 actionId;
        string actionType;
        address initiatedBy;
        uint256 timestamp;
        string details;
    }

    //State variables and mapping
    uint256 private actionCounter = 0;
    mapping(address  => Users) public users;
    mapping(uint256 => ActionLog) public actionLogs;
    mapping(address => bool) public authorizedEditors;
    address public owner;

    //Events for actions
    event EntityRegistered(string entityType, address indexed entityAddress);
    event EntityUpdated(string entityType, address indexed entityAddress);
    event ActionLogged(uint256 indexed actionId, string actionType, address indexed initiator, uint256 indexed timestamp, string details);

    /**
     * @dev Sets the contract owner as the deployer and initializes authorized editors.
     */
    constructor() {
        owner = msg.sender;
        authorizedEditors[owner] = true;
    }

    //Modifiers
    /**
     * @dev Restricts function access to the contract owner only.
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "This function is restricted to the contract owner.");
        _;
    }

    /**
     * @dev Restricts function access to either the contract owner or authorized editors.
     */
    modifier onlyAuthorized() {
        require(msg.sender == owner || authorizedEditors[msg.sender], "Access denied: caller is not the owner or an authorized editor.");
        _;
    }

    // Functions
    /**
     * @dev Authorizes a new editor to manage records.
     * @param _editor Address of the new editor to authorize.
     */
    function authorizeEditor(address _editor) public onlyOwner {
        authorizedEditors[_editor] = true;
    }

    /**
     * @dev Logs actions taken by users within the system for auditing purposes.
     * @param _actionType Type of action performed.
     * @param _initiator Address of the user who initiated the action.
     * @param _details Details or description of the action.
     */
    function logAction(string memory _actionType, address _initiator, string memory _details) internal {
        actionCounter++;
        actionLogs[actionCounter] = ActionLog(actionCounter, _actionType, _initiator, block.timestamp, _details);
        emit ActionLogged(actionCounter, _actionType, _initiator, block.timestamp, _details);
    }

    /**
     * @dev Adds a new medic record to the system.
     * @param name First name of the medic.
     * @param lastname Last name of the medic.
     * @param role Medical specialization of the medic.
     * @notice Only authorized users can add medic records.
     */
    function addUser(string memory name, string memory lastname, string memory role) public {
        require(!users[msg.sender].isRegistered, "User already registered");
        users[msg.sender] = Users(name, lastname, role, true);
        logAction("Create", msg.sender, "User added");
        emit EntityRegistered(role, msg.sender);
    }

}
