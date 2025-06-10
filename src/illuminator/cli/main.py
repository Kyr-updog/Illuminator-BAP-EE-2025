"""
A CLI for running simulations in the Illuminator
By: M. Rom & M. Garcia Alvarez
"""

import typer
from typing_extensions import Annotated
import illuminator.engine as engine
from pathlib import Path
from illuminator.cluster import build_runshfile 
from illuminator.schema.simulation import load_config_file
from illuminator.engine import Simulation
import os, time


APP_NAME = "illuminator"
DEFAULT_PORT = 5123
RUN_PATH = './Desktop/illuminatorclient/configuration/runshfile/'
RUN_MODEL = '/home/illuminator/Desktop/Final_illuminator'
RUN_FILE = 'run.sh'

app = typer.Typer()
scenario_app = typer.Typer()
app.add_typer(scenario_app, name="scenario", help="Run simulation scenarios.")
cluster_app = typer.Typer()
app.add_typer(cluster_app, name="cluster", help="Utilities for a RaspberryPi cluster.")
demonstrator_app = typer.Typer()
app.add_typer(demonstrator_app, name="demonstrator", help="Run the demonstrator")
simulation:Simulation = None

@scenario_app.command("run")
def scenario_run(config_file: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    "Runs a simulation scenario using a YAML file."
    
    global simulation
    simulation = Simulation(config_file)
    simulation.run()
    
@demonstrator_app.command("run")#run for the demonstrator part of the illuminator
def scenario_run(config_file: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    "Runs a simulation scenario using a YAML file. Keep in mind that this only works on linux"
    
    #while True:
    file = open("data.csv", 'a')
    for _ in range(10):
        begin_time = time.time()
        os.system('src/illuminator/cli/starter.sh')
        time.sleep(30)
        makeSim = Simulation("src/illuminator/cli/starter.yaml") #the path to the startup simulation (is only 1 step)
        makeSim.run()
        file.write(str(time.time()-begin_time)+"\n")
        time.sleep(10)
        
        #os.system('./run.sh')
        #global simulation
        #simulation = Simulation('simulation.yaml')
        #simulation.run()

@cluster_app.command("build")
def cluster_build(config_file: Annotated[str, typer.Argument(help="Path to scenario configuration file.")] = "config.yaml"):
    """Builds the run.sh files for a cluster of Raspberry Pi's."""
    app_dir = typer.get_app_dir(APP_NAME)
    runsh_path: Path = Path(app_dir) / "runshfile"

    runsh_path.mkdir(parents=True, exist_ok=True)

    output_file = RUN_FILE
    data = load_config_file(config_file)
    
    if data:
        build_runshfile.process_models(data, output_file)
        print(f"Commands have been written to {output_file}")


if __name__ == "__main__":

    # import importlib.util

    # package_spec = importlib.util.find_spec("illuminator.models.Battery")
    # print(package_spec.origin)


    app()
