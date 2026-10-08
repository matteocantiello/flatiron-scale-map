import sys
from pathlib import Path

# make `import scalemap` work when running pytest from the repo root without installing
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
