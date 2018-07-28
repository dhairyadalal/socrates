from sample_domains import RestaurantUserSim, RestaurantAgent
from dialog_simulator import *
import argparse
from pydoc import locate

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

parser.add_argument('-pd', '--print_dialog', action='store_true',
                    help='Print simulated dialog')



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


def setup_agent(agent_class: str,
                domain: Domain,
                nlg_type: str = None,
                nlg_path: str = None,
                nlu_type: str = None) ->'Agent':

    # Locate Agent and load
    agent = locate(agent_class)



    if type_ == "rules":
        agent = RestaurantAgent(domain)
        if nlu_type == "simple":
            nlu = NLUsimple(domain)
            agent.set_nlu(nlu)

        if nlg_type == "dict":
            nlg_dict = import_yaml(nlg_path)
            nlg_model = NLG(nlg_type, nlg_dict)
            agent.set_nlg(nlg_model)

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
        usersim = RestaurantUserSim(domain)

        # Load NLU and NLG models
        nlg_dict = import_yaml(nlg_path)
        nlg_model = NLG(nlg_type, nlg_dict)
        usersim.set_nlg(nlg_model)

        if nlu_type is not None:
            pass

        if nlu_path is None:
            usersim.set_nlu(None)
    return usersim


def load_dialog_manager(config: dict) -> 'DialogManager':

    # Load domain
    domain = import_domain_yaml(config.get("domain_config"))   # 1. Load domain
    domain_kb_type = config.get("domain_kb_type")
    domain_kb = None

    if domain_kb_type == "table":
        domain_kb_path = config.get("domain_kb_file_path")
        domain_kb_file_type = config.get("domain_kb_file_type")
        domain_kb = DomainKBtable(domain_kb_type, domain_kb_path, domain_kb_file_type)

    domain.add_domain_kb(domain_kb)  # 2. Load KB (replace w/ Domain obj)

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
                                   agent=agent,
                                   domain=domain,
                                   max_turns=config.get("max_turns"),
                                   num_sim=config.get("simulation_rounds"),
                                   reward=config.get(("reward")),
                                   first_speaker=config.get("first_speaker"))

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

    print_dialog_flag = False
    if args.print_dialog:
        print_dialog_flag = True


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
                                   print_dialog_flag,
                                   verbose_flag)
