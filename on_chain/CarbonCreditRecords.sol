// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Documentation for this contract written in NatSpec format
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

    struct Report {
        uint256 reportId;
        address userAddress;
        string operation_date;
        string operation;
    }

    struct Operation {
        uint256 planId;
        address userAddress;
        string creation_date;
        string operation;
    }

    // Struct to log actions for every previous struct
    struct ActionLog {
        uint256 actionId;
        string actionType;
        address initiatedBy;
        uint256 timestamp;
        string details;
    }

    // State variables and mapping
    uint256 private actionCounter = 0;
    uint256 public operationCounter = 1;  // Counter for unique operation IDs
    mapping(address => Users) public users;
    mapping(uint256 => Operation) public operation;
    mapping(uint256 => Report) public report;
    mapping(uint256 => ActionLog) public actionLogs;
    mapping(address => bool) public authorizedEditors;
    address public owner;

    // Events for actions
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

    // Modifiers
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
    function addUser(string memory name, string memory lastname, string memory role) public onlyAuthorized {
        require(!users[msg.sender].isRegistered, "User already registered");
        users[msg.sender] = Users(name, lastname, role, true);
        logAction("Create", msg.sender, "User added");
        emit EntityRegistered(role, msg.sender);
    }

    /**
     * @dev Updates an existing user's information.
     * @param name First name of the medic.
     * @param lastname Last name of the medic.
     * @param role Medical specialization of the medic.
     * @notice Only authorized users can update medic records.
     */
    function updateUser(string memory name, string memory lastname, string memory role) public onlyAuthorized {
        require(users[msg.sender].isRegistered, "User not found");
        Users storage user = users[msg.sender];
        user.name = name;
        user.lastName = lastname;
        user.role = role;
        logAction("Update", msg.sender, "User updated");
        emit EntityUpdated("User", msg.sender);
    }

    /**
     * @dev Adds a new operation record.
     * @param creation_date Date when the operation was created.
     * @param operation_description Description of the operation.
     * @notice Only authorized users can add operation records.
     */
    function addOperation(string memory creation_date, string memory operation_description) public onlyAuthorized {
        uint256 operationId = operationCounter++;  // Increment the counter for unique operation ID
        operation[operationId] = Operation(operationId, msg.sender, creation_date, operation_description);
        logAction("Create", msg.sender, "Operation added");
    }

    /**
     * @dev Updates an existing operation record.
     * @param operationId ID of the operation to update.
     * @param creation_date New creation date of the operation.
     * @param operation_description New operation description.
     * @notice Only authorized users or the creator of the operation can update it.
     */
    function updateOperation(uint256 operationId, string memory creation_date, string memory operation_description) public onlyAuthorized {
        // Controllo che il chiamante sia l'owner o il creatore dell'operazione
        require(msg.sender == owner || msg.sender == operation[operationId].userAddress, "Unauthorized");

        // Aggiornamento dei campi
        operation[operationId].creation_date = creation_date;
        operation[operationId].operation = operation_description;

        // Log dell'azione
        logAction("Update", msg.sender, "Operation updated");
        emit EntityUpdated("Operation", msg.sender);
    }

    /**
     * @dev Adds a new report record.
     * @param operation_date Date of the operation the report refers to.
     * @param operation_description Description of the operation.
     * @notice Only authorized users can add report records.
     */
    function addReport(string memory operation_date, string memory operation_description) public onlyAuthorized {
        uint256 reportId = uint256(keccak256(abi.encodePacked(msg.sender, operation_date, operation_description, block.timestamp)));
        report[reportId] = Report(reportId, msg.sender, operation_date, operation_description);
        logAction("Create", msg.sender, "Report added");
    }

    /**
     * @dev Updates an existing report record.
     * @param reportId ID of the report to update.
     * @param operationDate New date of the operation.
     * @param operationDescription New description of the operation.
     * @notice Only authorized users or the creator of the report can update it.
     */
    function updateReport(uint256 reportId, string memory operationDate, string memory operationDescription) public onlyAuthorized {
        require(report[reportId].userAddress != address(0), "Report not found");
        require(msg.sender == owner || msg.sender == report[reportId].userAddress, "Unauthorized");

        report[reportId].operation_date = operationDate;
        report[reportId].operation = operationDescription;

        logAction("Update", msg.sender, "Report updated");
    }
}
