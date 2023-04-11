from pathlib import Path

import pandas as pd
from loguru import logger
from omegaconf import DictConfig

import hydra


@hydra.main(version_base=None, config_path="hydra", config_name="config")
def main(cfg: DictConfig):
    output_dir = Path.cwd() / "51job_output"
    output_dir.mkdir(exist_ok=True)

    datadir = Path(hydra.utils.get_original_cwd()) / cfg.datadir

    # Load data
    df = pd.read_csv(datadir / f"{cfg.keyword}.csv")
    logger.info(df.shape)


if __name__ == "__main__":
    main()
