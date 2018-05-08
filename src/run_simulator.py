from dialog_agents import RestaurantAgent
from user_simulator import RuleSimulator
from dialog_simulator import *
import yaml

def main():

    # 1. Load Domain
    print("Loading domain .... ")
    domain_manager = DomainManager()
    domain_manager.load_domains("data/")
    restaurant = domain_manager.get_domain("restaurant")
    print("\tLoaded: ", restaurant)

    # 2. Setup User sim
    print("Setting up user simulator .... ")
    usersim = RuleSimulator(restaurant, "random")
    goal_path = "data/sample_starting_goals.yaml"
    usersim.load_starting_goals(goal_path, "yaml")
    nlg_dict = yaml.safe_load(open("data/nlg_rules.yaml"))  # Load NLG model
    nlg_model = NLG("dict", nlg_dict)
    usersim.set_nlg(nlg_model)
    print("\tLoaded: ", usersim)

    # 3. Setup Agent
    print("Setting up user simulator .... ")
    agent = RestaurantAgent(restaurant)
    print("\tLoaded:", agent)

    # 4. Setup DialogManager
    dialog_manager = DialogManager(usersim, agent, restaurant, num_sim=10)
    dialog_manager.run_simulations()


if __name__ == "__main__":
    main()
