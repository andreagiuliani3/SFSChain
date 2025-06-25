from controllers.action_controller import ActionController

action_controller_instance = ActionController()

# If the contract is not loaded, deploy and initialize it
if not action_controller_instance.load_contract():
    action_controller_instance.deploy_and_initialize('../../on_chain/CarbonCreditRecords.sol')