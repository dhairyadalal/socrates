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

parser.add_argument('-nv', '--non_verbose', action='store_true',
                    help='Show invocation and status for each simulated dialog')


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


def setup_agent(type_: str,
                domain: Domain,
                nlg_type: str = None,
                nlg_path: str = None,
                nlu_type: str = None) ->'Agent':
    if type_ == "rules":
        agent = RestaurantAgent(domain)
        if nlu_type == "simple":
            nlu = NLUsimple(domain)
            agent.set_nlu(nlu)
        return agent

    else:
        return None # replace w/ other options

def setup_usersim( type_: str,
                   domain: Domain,
                   nlg_type: str,
                   nlg_path: str = None,
                   nlu_type: str = None,
                   nlu_path: str = None)->'UserSimulator':

    if type_ == "rules":
        # Load simulator
        usersim = RuleSimulator(domain)

        # Load NLU and NLG models
        nlg_dict = yaml.safe_load(open(nlg_path))
        nlg_model = NLG(nlg_type, nlg_dict)

        if nlu_type is not None:
            pass

        usersim.set_nlg(nlg_model)

        if nlu_path is None:
            usersim.set_nlu(None)
    return usersim


def load_dialog_manager(config: dict) -> 'DialogManager':

    # Load domain
    domain = import_domain_yaml(config.get("domain_config"))   # 1. Load domain

    if config.get("domain_kb_type") == "json":
        domain_kb_path = config.get("domain_kb_path")
        domain.add_domain_kb(json.load(open(domain_kb_path)))  # 2. Load KB (replace w/ Domain obj)

    # Load Speakers
    agent = setup_agent(type_=config.get("agent_type"),
                        domain=domain,
                        nlg_type=config.get("agent_nlg_type"),
                        nlg_path=config.get("agent_nlg_path"),
                        nlu_type=config.get("agent_nlu_type"))

    usersim = setup_usersim(config.get("usersim_type"), domain,
                            config.get("usersim_nlg_type"),
                            config.get("usersim_nlg_path"),
                            None)

    dialog_manager = DialogManager(user_sim=usersim,
                                   user_goal_type=config.get("user_goal_type"),
                                   agent=agent, domain=domain,
                                   max_turns=config.get("max_turns"),
                                   num_sim=config.get("simulation_rounds"),
                                   reward=config.get(("reward")))

    # Load Starting Goals if present
    if config.get("starting_goal_path") is not None:
        starting_goals = import_yaml(config.get("starting_goal_path"))
        dialog_manager.set_starting_goals(starting_goals)

    return dialog_manager


if __name__ == "__main__":

    args = parser.parse_args()

    verbose_flag = True
    if args.non_verbose:
        verbose_flag = False

    # Check for valid file types
    if args.type not in ["json", "yaml"]:
        raise ValueError("Bad file type provided. Valid file types: json and yaml.")

    # Import config file
    config = import_config(args.path, args.type)

    # Load Dialog Manager with provided configuration settings
    dialog_manager = load_dialog_manager(config)

    # Run Dialog manager
    dialog_manager.run_simulations(config.get("save_location"),
                                   config.get("save_history"),
                                   config.get("save_type"),
                                   verbose_flag)
