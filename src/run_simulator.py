from dialog_agents import RestaurantAgent
from user_simulator import RuleSimulator
from dialog_simulator import *
import argparse

# Set up command line paraser
parser = argparse.ArgumentParser(description=
                                 'Socrates Sim, a user simulator to support task completion dialog. Use -h for help.')

parser.add_argument('-p', '--path', required=True,
                    help='Path to simulation configuration file.')

parser.add_argument('-t', '--type', required=True,
                    help='Simulation config file type. Supported file types: json, yaml')

parser.add_argument('-o', '--output_loc',
                    help='Output location to store simulated dialog histories.')


# Config File Validation
def validate_config(config: dict) -> bool:
    # Loop through config file and validate args. Replace missing args w/ None
    return True


# Setup dialog manager
def import_config(file_path: str, file_type: str)->dict:
    if file_type == "yaml":
        return import_yaml(file_path)
    else:
        return import_json(file_path)


def setup_agent(type_: str, domain: Domain)->'Agent':
    if type_ == "rules":
        return RestaurantAgent(domain)
    else:
        return None # replace w/ other options

def setup_usersim( type_: str, domain: Domain, goal_type: str, nlg_type: str, nlg_path: str, starting_goals_path: str,
                   nlu_path: str )->'UserSimulator':

    if type_ == "rules":
        # Load simulator
        usersim = RuleSimulator(domain, goal_type)

        # Load starting goals
        usersim.load_starting_goals(starting_goals_path, "yaml")

        # Load NLU and NLG models
        nlg_dict = yaml.safe_load(open(nlg_path))
        nlg_model = NLG("dict", nlg_dict)
        usersim.set_nlg(nlg_model)

        if nlu_path is None:
            usersim.set_nlu(None)
    return usersim


def load_dialog_manager(config: dict) -> DialogManager:

    # Load domain
    domain = import_domain_yaml(config.get("domain_config"))           # 1. Load domain
    domain.add_domain_kb(json.load(open("data/restaurants_kb.json")))  # 2. Load KB (replace w/ Domain obj)

    # Load Speakers
    agent = setup_agent(config.get("agent_type"), domain)
    usersim = setup_usersim(config.get("usersim_type"), domain, config.get("user_goal_type"),
                            config.get("nlg_type"), config.get("nlg_path"), config.get("starting_goal_path"),
                            None)

    dialog_manager = DialogManager(user_sim=usersim, agent=agent, domain=domain, max_turns=config.get("max_turns"),
                                   num_sim=config.get("simulation_rounds"), reward=config.get(("reward")))

    return dialog_manager


if __name__ == "__main__":
    args = parser.parse_args()

    # Check for valid file types
    if args.type not in ["json", "yaml"]:
        raise ValueError("Bad file type provided. Valid file types: json and yaml.")

    # Import config file
    config = import_config(args.path, args.type)

    # Load Dialog Manager with provided configuration settings
    dialog_manager = load_dialog_manager(config)

    # Run Dialog manager
    dialog_manager.run_simulations()



