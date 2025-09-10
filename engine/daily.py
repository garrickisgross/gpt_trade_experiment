import os
from db.db import get_strategy
from prompt_generation.generate import generate_daily_prompt
from engine.history import write_to_csv
from models.models import Strategy
from typing import List

def daily_checkup_flow(arg: str) -> None:
    
    strats: List[Strategy] = []
    
    if arg == "all":
        dirs = os.listdir("output")
        for strat in dirs:
            x: Strategy = get_strategy(strat)
            strats.append(x)

    else:
        x: Strategy = get_strategy(arg)
        strats.append(x)

    

    
    for strategy in strats:
        directory = f"output/{strategy.name}"
        # make directory for storing prompt and CSV. 
        dirs = os.listdir(f"{directory}/daily_prompt")
        dirs = [int(i) for i in dirs]

        i = 1
        while True:
            if i in dirs:
                i += 1
                continue
            else: 
                break
        
        os.mkdir(f"{directory}/daily_prompt/{i}")
        
        # Generate Prompt and CSV, persist to file
        generate_daily_prompt(strategy,f"{directory}/daily_prompt/{i}/daily.md")

        # Write CSV file attachment w/history to same folder. 
        write_to_csv(strategy.position_history, f"{directory}/daily_prompt/{i}/history.csv")



    
