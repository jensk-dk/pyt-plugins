import sys
from pathlib import Path

# myapp/ is a script directory, not an installed package — expose it flat
sys.path.insert(0, str(Path(__file__).parent.parent / "myapp"))
