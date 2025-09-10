from models.models import Strategy
from pydantic import ValidationError
import json
import os
import shutil
from db.db import get_strategy_names, update, insert
from prompt_generation.generate import generate_initial_prompt


def new_strategy(path_to_json: str) -> Strategy:
    """Validates a new strategy from provided JSON, raises ValidationError if invalid JSON | OSError if path not found"""
    
    with open(path_to_json) as f:
        data = f.read()

    
    try:
        strategy = Strategy.model_validate_json(data)
        return strategy
    
    except ValidationError as v:
        print(f"Unable to validate JSON against Strategy Model \n\n {json.dumps(data, indent=4)} \n\n")
        print(f"Schema: \n\n {Strategy.model_json_schema()}")
        raise v
    
    except OSError as e:
        print(f"Unable to open provided path ({path_to_json}). Please check path and try again.")
        raise e

def exists_menu() -> None:
    print(f"\n\nStrategy with this name already exists: \n\n",
                "\t 1: Add new strategy with unique name \n",
                "\t 2: Exit \n\n " \
                "If you would prefer to update existing strategy, adjust its config locally then run:\n\n" \
                "\t python main.py --update <strategy-name> \n\n")

def strategy_flow(path: str) -> None:
    """ Delegates the creation of new strategies"""
    
    # Try to create a strategy
    try:

        strategy = new_strategy(path)

    except:
        print(f"Failed to create Strategy from JSON in path {path}")
        return

    curr_strats = get_strategy_names()

    curr_strats = [i[0] for i in curr_strats]

    print(curr_strats)

    # No need to run duplicate strategies, unless specified by the user
    if strategy.name in curr_strats:
        
        while True:
            exists_menu()
            inp = input("Input Choice: ")
            if inp == '1' or inp == '2':
                break

        match inp:
            case '1':
                i = 1
                name = strategy.name + f"_{i}"
                while name in curr_strats:
                    i += 1
                    name = strategy.name + f"_{i}"

                strategy.name = name
            case '2':
                return 


    # Put that thang in the DB
    insert(strategy)

    #Make necessary subdirectories in the output folder. 
    subdirs = ["performance_reports", "daily_prompt", "weekly_prompt"]
    os.mkdir(f"output/{strategy.name}")
    for dir in subdirs:
        os.mkdir(f"output/{strategy.name}/{dir}")

    # make a copy of json config and put in the directory (easy updating)
    shutil.copy(path, f"output/{strategy.name}")

    # Generate the Initial Deep Research Prompt
    generate_initial_prompt(strategy)






