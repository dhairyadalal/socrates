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

parser.add_argument('-s')



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


def setup_agent(agent_class: str, domain: Domain) ->'Agent':

    # Locate Agent and load
    agent = locate(agent_class)(domain)

    return agent

def setup_usersim(usersim_class: str,
                  domain: Domain,
                  nlg_class: str,
                  nlu_class: str=None)->'UserSimulator':

    # Locate and load usersim class
    usersim = locate(usersim_class)(domain)

    # locate and load nlg class
    nlg = locate(nlg_class)()
    usersim.set_nlg(nlg)

    if nlu_class is not None:
        nlu = locate(nlu_class)
        usersim.set_nlu(nlu)

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
    agent = setup_agent(agent_class=config.get("agent_class"),
                        domain=domain)

    usersim = setup_usersim(config.get("usersim_class"), domain,
                            config.get("nlg_class"))

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

    if args.s is not None:
        config["simulation_rounds"] = int(args.s)

    # Load Dialog Manager with provided configuration settings
    dialog_manager = load_dialog_manager(config)

    # Run Dialog manager
    dialog_manager.run_simulations(config.get("save_location"),
                                   config.get("save_history"),
                                   config.get("save_type"),
                                   print_dialog_flag,
                                   verbose_flag)
