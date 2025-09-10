from db.db import get_strategy, update
from models.models import Position
from pydantic import ValidationError
import json
from engine.history import get_history

def conflict_menu() -> str:
    inp = None
    while True:
        print(f"\n\nA position with this ticker already exists in this strategy, update instead?")
        print(f"\t 1. Yes, Update this position.")
        print(f"\t 2. No, a mistake was made.\n")
        inp = input("Input Choice: ")
        if inp == '1' or inp == '2':
            return inp

def new_pos(path_to_json: str) -> Position:
    """Validates a new position from provided JSON, raises ValidationError if invalid JSON | OSError if path not found"""
    
    data = ""
    
    try:
        
        with open(path_to_json) as f:
            data = f.read()
        pos = Position.model_validate_json(data)
        return pos 
    
    except ValidationError as v:
        print(f"Unable to validate JSON against Position model \n\n {json.dumps(data, indent=4)} \n\n")
        print(f"Schema: \n\n {Position.model_json_schema()}")
        raise v
    
    except OSError as e:
        print(f"Unable to open provided path ({path_to_json}). Please check path and try again.")
        raise e


def create_new_position_flow(json_path: str) -> None:
    try:
        pos = new_pos(json_path)

    except:
        print(f"Failed to create Position from JSON in path {json_path}")
        return
    

    # Get associated strategy from db
    strategy = get_strategy(pos.strategy_name)

    # Check if ticker already in positions, if so, ask if they want to update or cancel
    idx = None
    for i, position in enumerate(strategy.positions):
        if position.name == pos.name:
            idx = i

    if idx != None:
        inp = conflict_menu()

        if inp == "1":
            update_position(json_path)
            return

        if inp == "2":
            return
        
    # pos doesn't exist, add new one to the strategy, then persist to db
    strategy.positions.append(pos)


    # update history for position
    tickers = [i.name for i in strategy.positions if i.status == "active"]
    hist = get_history(tickers)
    strategy.position_history = hist

    # Persist to DB
    update(strategy)

    


    
        
        



        







    

def update_position(json_path: str) -> None:
    pass