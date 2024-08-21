import os
import ast
import time
import tomllib
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Training arguments for myosuite", add_help=False)
    parser.add_argument("-c", "--config", default="config.toml")
    parser.add_argument(
        "-e",
        "--env-name",
        type=str,
        default="Ant-v4",
        help="Name of specific environment to run",
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="sweep-carbs",
        choices="train eval evaluate sweep-carbs autotune profile".split(),
    )
    parser.add_argument("--eval-model-path", type=str, default=None)
    parser.add_argument(
        "--baseline", action="store_true", help="Pretrained baseline where available"
    )
    parser.add_argument(
        "--vec",
        "--vector",
        "--vectorization",
        type=str,
        default="serial",
        choices=["serial", "multiprocessing"],
    )
    parser.add_argument(
        "--exp-id", "--exp-name", type=str, default=None, help="Resume from experiment"
    )
    parser.add_argument("--wandb-project", type=str, default="mujoco")
    parser.add_argument("--wandb-group", type=str, default=None)
    parser.add_argument("--track", action="store_true", help="Track on WandB")
    parser.add_argument("--capture-video", action="store_true", help="Capture videos")

    args = parser.parse_known_args()[0]

    # Load config file
    if not os.path.exists(args.config):
        raise Exception(f"Config file {args.config} not found")
    with open(args.config, "rb") as f:
        config = tomllib.load(f)

    for section in config:
        for key in config[section]:
            argparse_key = f"--{section}.{key}".replace("_", "-")
            parser.add_argument(argparse_key, default=config[section][key])

    # Override config with command line arguments
    parsed = parser.parse_args().__dict__
    args = {"env": {}, "policy": {}, "rnn": {}}
    env_name = parsed.pop("env_name")
    for key, value in parsed.items():
        next = args
        for subkey in key.split("."):
            if subkey not in next:
                next[subkey] = {}
            prev = next
            next = next[subkey]
        try:
            prev[subkey] = ast.literal_eval(value)
        except:  # noqa
            prev[subkey] = value

    run_name = f"{env_name}_{args['train']['seed']}_{int(time.time())}"

    return args, env_name, run_name


def init_wandb(args_dict, run_name, id=None, resume=True):
    import wandb

    wandb.init(
        id=id or wandb.util.generate_id(),
        project=args_dict["wandb_project"],
        group=args_dict["wandb_group"],
        allow_val_change=True,
        save_code=True,
        resume=resume,
        config=args_dict,
        name=run_name,
    )
    return wandb
