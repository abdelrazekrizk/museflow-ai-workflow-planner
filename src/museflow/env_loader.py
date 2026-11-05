"""Load project environment variables without overriding the active shell."""

from pathlib import Path
from typing import Optional, Union

from dotenv import load_dotenv


def load_env(env_file: Optional[Union[str, Path]] = None) -> bool:
    """Load .env values without replacing existing process environment values.

    By default, search the project root and then the working directory.
    ``env_file`` can be supplied explicitly, for example by tests.
    """
    if env_file is None:
        project_root = Path(__file__).resolve().parents[2]
        candidate = project_root / ".env"
        if not candidate.is_file():
            candidate = Path.cwd() / ".env"
    else:
        candidate = Path(env_file)

    if not candidate.is_file():
        return False

    load_dotenv(dotenv_path=candidate, override=False)
    return True


if __name__ == "__main__":
    if load_env():
        print("Loaded .env values; existing shell values were preserved.")
    else:
        print("No .env file found.")
