import os
from db.db import get_strategy
from models.models import Strategy

def generate_daily_prompt(strategy: Strategy) -> None:
    pass

def daily_checkup_flow(arg: str) -> None:
    
    strats = []
    
    if arg == "all":
        dirs = os.listdir("output")
        for strat in dirs:
            strats.append(get_strategy(strat))

    else:
        strats.append(get_strategy(arg))

    
    for strategy in strats:
        generate_daily_prompt(strategy)

    
