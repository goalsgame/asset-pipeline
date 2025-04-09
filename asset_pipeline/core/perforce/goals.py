from enum import Enum
import contextlib
import P4

import asset_pipeline.core.perforce.common as common
import asset_pipeline.core.logging as logging

logger = logging.get_logger(__name__)
logging.setup_logging(level="DEBUG")


class Depot(Enum):
    GAME_SOURCE_CONTENT = "//GameSourceContent/"
    GAME = "//Game/"


@contextlib.contextmanager
def connection(depot: Depot):
    """
    Context manager that connects to Perforce, ensures a workspace exists for the specified depot,
    and sets the correct workspace.

    :param depot: A Depot enum value representing the desired depot.
    :yield: An active P4 connection.
    :raises ConnectionError: If connection to Perforce fails.
    :raises ValueError: If no valid workspace is found.
    :raises P4.P4Exception: If other Perforce operations fail.
    """
    p4 = P4.P4()
    try:
        try:
            p4.connect()
        except P4.P4Exception as e:
            logger.error(f"Failed to connect to Perforce: {e}")
            raise ConnectionError(f"Failed to connect to Perforce: {e}") from e

        workspace_spec = common.find_workspace_by_depot(p4, depot.value)
        if not workspace_spec:
            logger.error(f"No valid workspace found for depot '{depot.value}'")
            raise ValueError(f"No valid workspace found for depot '{depot.value}'")

        p4.client = workspace_spec["Client"]
        logger.debug("Using workspace '%s' for depot '%s'", p4.client, depot.value)
        yield p4  # Proceed with processing

    finally:
        try:
            if p4.connected():
                p4.disconnect()
        except Exception as e:
            logger.warning("Error disconnecting from Perforce: %s", e)


def main():
    with connection(Depot.GAME_SOURCE_CONTENT) as p4:
        # Perforce is ready, proceed with logic
        changelist = retrieve_changelist_by_keyword(p4, "AssetPipeline Update")
        logger.info("Changelist to use: %s", changelist)

        # Further processing (e.g., adding files, syncing, etc.)
        # ...

if __name__ == "__main__":
    main()