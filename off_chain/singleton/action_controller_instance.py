from controllers.action_controller import ActionController

"""
This script initializes an instance of the ActionController class,
which is responsible for managing actions related to carbon credit records.
It checks if the contract is loaded, and if not, it deploys and initializes the contract.
"""


action_controller_instance = ActionController()

if not action_controller_instance.load_contract():
    action_controller_instance.deploy_and_initialize('../../on_chain/CarbonCreditRecords.sol')