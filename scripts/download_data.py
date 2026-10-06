import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "src"))
from airbnb.io import load_config
from airbnb.download import download
cfg, root = load_config(sys.argv[1] if len(sys.argv)>1 else root / "configs/toronto.yaml")
download(cfg, root)
