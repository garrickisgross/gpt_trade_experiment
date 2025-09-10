import argparse
from db.db import create_script
from engine.strategy import strategy_flow
from engine.daily import daily_checkup_flow
from engine.position import create_new_position_flow, update_position

class TupleAction(argparse.Action):
    """
    argparse action to store nargs=2 as a tuple.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) != 2: # type: ignore
            parser.error(f"argument {self.dest}: expected 2 arguments, got {len(values)}") # type: ignore
        setattr(namespace, self.dest, tuple(values)) # type: ignore

def main(args: argparse.Namespace):
    # Create DB (Okay to run with active DB)
    create_script()

    if args.strategy:
        strategy_flow(path=args.strategy)
    
    if args.daily_checkup:
        daily_checkup_flow(args.daily_checkup)

    if args.position:
        action, json_path = args.position

        if action == "add":
            create_new_position_flow(json_path)
        if action == "update":
            update_position(json_path)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="GPT Stock Trader",
                            description="A toolkit to experiment with GPT driven trades",
                            ) 
    
    # Parse Strategy Argument
    parser.add_argument("--strategy",
                        type=str,
                        help="New strategy from JSON file",
                        required=False,
                        metavar="[json_filepath]"
                        )

    # Daily Checkup on all strategies
    parser.add_argument("--daily_checkup", 
                        type=str,
                        default="all",
                        required= False,
                        help="Perform a daily checkup on active strategies",
                        metavar="[strategy | 'all'] "
                        )
    
    # Add/Edit Positions in strategy
    parser.add_argument("--position",
                        nargs=2,
                        action=TupleAction,
                        help="Appends a position to the strategy and updates available capital",
                        required=False,
                        metavar=("[update | add]", "[json_filepath]"))

    args = parser.parse_args()

    main(args)