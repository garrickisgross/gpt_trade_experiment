from prompt_generation.render import Renderer
from models.models import Strategy
from datetime import datetime

def generate_initial_prompt(strat: Strategy):
    #Instantiate Renderer
    renderer = Renderer()
    data = {
        "strategy": strat,
        "date": datetime.now()
    }
    
    # Output to initial_prompt.md file
    renderer.render_to_file("initial.md.j2", f"output/{strat.name}/initial.md", data=data)