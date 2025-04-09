import P4

import asset_pipeline.core.logging as logging

logger = logging.get_logger(__name__)


def is_new_file(p4: P4, depot_path: str) -> bool:
    """
    Returns True if the file is new (not yet added to Perforce), avoiding exceptions.
    """
    fstat_info = p4.run("fstat", "-T", "headRev", depot_path)
    return not fstat_info  # If empty, the file does not exist in Perforce


def is_file_checked_out(p4: P4, depot_path: str) -> bool:
    """
    Returns True if the file is already checked out by someone else.
    """
    result = p4.run("opened", "-a", depot_path)  # -a checks all users
    return bool(result)  # If output is non-empty, someone has it checked out


def is_file_up_to_date(p4: P4, depot_path: str) -> bool:
    """
    Returns True if the local file version is up to date.
    """
    # Get the latest revision in the depot
    fstat_info = p4.run("fstat", "-T", "headRev", depot_path)
    latest_revision = int(fstat_info[0]["headRev"]) if fstat_info else None
    # Get the revision you have locally
    have_info = p4.run("have", depot_path)
    local_revision = int(have_info[0]["haveRev"]) if have_info else None
    return local_revision == latest_revision  # True if up to date


def create_new_changelist(p4: P4, description: str):
    new_cl = p4.fetch_change()
    new_cl["Description"] = description
    new_cl['Files'] = []
    result = p4.save_change(new_cl)
    new_cl_number = result[0].split()[1]
    logger.debug(f"Created new empty changelist {new_cl_number}")
    return new_cl_number


def get_pending_changelists(p4: P4):
    pending_changelists = p4.run("changes", "-u", p4.user, "-s", "pending")
    return pending_changelists


def add_files_to_changelist(p4: P4, changelist_number, *file_path):
    p4.run("edit", "-c", changelist_number, *file_path)


def find_workspace_by_depot(p4: P4, depot_path: str):
    user_workspaces = p4.run("clients", "-u", p4.user)
    for ws in user_workspaces:
        client_spec = p4.fetch_client(ws["client"])
        view_mappings = client_spec.get("View", [])
        if any(mapping.startswith(depot_path) for mapping in view_mappings):
            logger.debug("Workspace '%s' explicitly maps to depot '%s'", ws["client"], depot_path)
            return client_spec
    return None


def retrieve_changelist_by_keyword(p4: P4, keyword: str):
    pending_cls = get_pending_changelists(p4)
    for cl in pending_cls:
        cl_number = cl["change"]
        cl_spec = p4.fetch_change(cl_number)
        if keyword in cl_spec.get("Description", ""):
            logger.debug(f"Found existing changelist {cl_number} with matching keyword [{keyword}]")
            return cl_number

    logger.debug(f"Changelist with keyword {[keyword]} not found. Creating a new changelist")
    return create_new_changelist(p4, keyword)
