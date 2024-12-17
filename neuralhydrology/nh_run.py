#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
import torch

# make sure code directory is in path, even if the package is not installed using the setup.py
sys.path.append(str(Path(__file__).parent.parent))
from neuralhydrology.evaluation.evaluate import start_evaluation
from neuralhydrology.training.train import start_training
from neuralhydrology.utils.config import Config
from neuralhydrology.utils.logging_utils import setup_logging


def _get_args() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=["train", "continue_training", "finetune", "evaluate"])
    parser.add_argument('--config-file', type=str)
    parser.add_argument('--run-dir', type=str)
    parser.add_argument('--epoch', type=int, help="Epoch, of which the model should be evaluated")
    parser.add_argument('--period', type=str, choices=["train", "validation", "test"], default="test")
    parser.add_argument('--gpu', type=int,
                        help="GPU id to use. Overrides config argument 'device'. Use a value < 0 for CPU.")
    parser.add_argument('--device', type=str, choices=["cpu", "cuda", "mps"], 
                        help="Device to use for training/evaluation: 'cpu', 'cuda', or 'mps'.")
    args = vars(parser.parse_args())

    if (args["mode"] in ["train", "finetune"]) and (args["config_file"] is None):
        raise ValueError("Missing path to config file")

    if (args["mode"] == "continue_training") and (args["run_dir"] is None):
        raise ValueError("Missing path to run directory file")

    if (args["mode"] == "evaluate") and (args["run_dir"] is None):
        raise ValueError("Missing path to run directory")

    return args

def _resolve_device(config_device: str, gpu: int = None, cli_device: str = None) -> str:
    """
    Resolve the device to use based on CLI device, GPU option, and config file.

    Parameters
    ----------
    config_device : str
        Device specified in the config file ('cuda', 'mps', or 'cpu').
    gpu : int, optional
        GPU id from command-line arguments. Overrides config file.
    cli_device : str, optional
        Device specified via the --device argument. Highest priority.

    Returns
    -------
    str
        Device string to use ('cuda:X', 'mps', or 'cpu').
    """
    # CLI --device takes the highest priority
    if cli_device:
        if cli_device == "mps" and torch.backends.mps.is_available():
            return "mps"
        elif cli_device.startswith("cuda") and torch.cuda.is_available():
            return cli_device
        elif cli_device == "cpu":
            return "cpu"

    # GPU argument (fallback when --device not specified)
    if gpu is not None:
        if gpu >= 0 and torch.cuda.is_available():
            return f"cuda:{gpu}"
        elif gpu < 0:
            return "cpu"

    # Fallback to config file device
    if config_device:
        if config_device.lower() == "mps" and torch.backends.mps.is_available():
            return "mps"
        elif config_device.lower().startswith("cuda") and torch.cuda.is_available():
            return config_device
        elif config_device.lower() == "cpu":
            return "cpu"

    # Automatic fallback
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

def _main():
    args = _get_args()
    if (args["run_dir"] is not None) and (args["mode"] == "evaluate"):
        setup_logging(str(Path(args["run_dir"]) / "output.log"))

    if args["mode"] == "train":
        start_run(config_file=Path(args["config_file"]), gpu=args["gpu"], device=args["device"])
    elif args["mode"] == "continue_training":
        continue_run(run_dir=Path(args["run_dir"]),
                     config_file=Path(args["config_file"]) if args["config_file"] is not None else None,
                     gpu=args["gpu"], device=args["device"])
    elif args["mode"] == "finetune":
        finetune(config_file=Path(args["config_file"]), gpu=args["gpu"], device=args["device"])
    elif args["mode"] == "evaluate":
        eval_run(run_dir=Path(args["run_dir"]), period=args["period"], epoch=args["epoch"],
                 gpu=args["gpu"], device=args["device"])
    else:
        raise RuntimeError(f"Unknown mode {args['mode']}")


def start_run(config_file: Path, gpu: int = None, device: str = None):
    """Start training a model.
    
    Parameters
    ----------
    config_file : Path
        Path to a configuration file (.yml), defining the settings for the specific run.
    gpu : int, optional
        GPU id to use. Will override config argument 'device'. A value smaller than zero indicates CPU.

    """

    config = Config(config_file)
    config.device = _resolve_device(config_device=config.device, gpu=gpu, cli_device=device)
    print(f"Using device: {config.device}")
    start_training(config)


def continue_run(run_dir: Path, config_file: Path = None, gpu: int = None, device: str = None):
    """Continue model training.
    
    Parameters
    ----------
    run_dir : Path
        Path to the run directory.
    config_file : Path, optional
        Path to an additional config file. Each config argument in this file will overwrite the original run config.
    gpu : int, optional
        GPU id to use. Will override config argument 'device'. A value smaller than zero indicates CPU.

    """
    # load config from base run and overwrite all elements with an optional new config
    base_config = Config(run_dir / "config.yml")

    if config_file is not None:
        base_config.update_config(config_file)

    base_config.is_continue_training = True

    # check if a GPU has been specified as command line argument. If yes, overwrite config
    base_config.device = _resolve_device(config_device=base_config.device, gpu=gpu, cli_device=device)

    start_training(base_config)


def finetune(config_file: Path = None, gpu: int = None, device: str = None):
    """Finetune a pre-trained model.

    Parameters
    ----------
    config_file : Path, optional
        Path to an additional config file. Each config argument in this file will overwrite the original run config.
        The config file for finetuning must contain the argument `base_run_dir`, pointing to the folder of the 
        pre-trained model, as well as 'finetune_modules' to indicate which model parts will be trained during
        fine-tuning.
    gpu : int, optional
        GPU id to use. Will override config argument 'device'. A value smaller than zero indicates CPU.

    """
    # load finetune config and check for a non-empty list of finetune_modules
    temp_config = Config(config_file)
    if not temp_config.finetune_modules:
        raise ValueError("For finetuning, at least one model part has to be specified by 'finetune_modules'.")

    # extract base run dir, load base run config and combine with the finetune arguments
    config = Config(temp_config.base_run_dir / "config.yml")
    config.update_config({'run_dir': None, 'experiment_name': None})
    config.update_config(config_file)
    config.is_finetuning = True

    # if the base run was a continue_training run, we need to override the continue_training flag from its config.
    config.is_continue_training = False

    # check if a GPU has been specified as command line argument. If yes, overwrite config
    config.device = _resolve_device(config_device=config.device, gpu=gpu, cli_device=device)

    start_training(config)


def eval_run(run_dir: Path, period: str, epoch: int = None, gpu: int = None, device: str = None):
    """Start evaluating a trained model.
    
    Parameters
    ----------
    run_dir : Path
        Path to the run directory.
    period : {'train', 'validation', 'test'}
        The period to evaluate.
    epoch : int, optional
        Define a specific epoch to use. By default, the weights of the last epoch are used.  
    gpu : int, optional
        GPU id to use. Will override config argument 'device'. A value less than zero indicates CPU.

    """
    config = Config(run_dir / "config.yml")

    config.device = _resolve_device(config_device=config.device, gpu=gpu, cli_device=device)

    start_evaluation(cfg=config, run_dir=run_dir, epoch=epoch, period=period)


if __name__ == "__main__":
    _main()
