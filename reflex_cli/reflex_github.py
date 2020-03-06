"""Holder of template generation logic"""
import base64
import logging
import os

import github
import hcl

LOGGER = logging.getLogger("reflex_cli")


class ReflexGithub:
    """Discovers rules by querying github remotes."""

    def __init__(self):
        self.github_organizations = ["cloudmitigator"]

        token = os.environ.get("REFLEX_GITHUB_TOKEN")
        self.github_client = github.Github(token)

    def get_repos(self):
        """Iterates over github org and collects repos that match rules."""
        for organization in self.github_organizations:  # pragma: no cover
            LOGGER.debug("Collecting repos for %s", organization)
            org_api = self.github_client.get_organization(organization)
            return org_api.get_repos()

    def get_remote_version(self, remote):
        """Calls github API for remote to get latest release."""
        try:  # pragma: no cover
            repo = self.github_client.get_repo(remote)
        except github.GithubException:  # pragma: no cover
            LOGGER.debug("No remote resource found at github.com/%s", remote)
            return None
        try:  # pragma: no cover
            latest_release = repo.get_latest_release()
        except github.GithubException:  # pragma: no cover
            LOGGER.debug("No releases found for %s", remote)
            return None
        return latest_release.tag_name

    def get_rule_mode(self, remote):
        """
        Calls GitHub API and determines if the specified rule has different modes

        If no modes are available, returns None. If modes are available, returns "remediate"
        """
        try:  # pragma: no cover
            repo = self.github_client.get_repo(remote)
        except github.GithubException:  # pragma: no cover
            LOGGER.warning("No remote resource found at github.com/%s", remote)
            return None

        try:
            contents = repo.get_contents("variables.tf")
            content_string = base64.b64decode(contents.content).decode('ascii')
            content_dict = hcl.loads(content_string)
            if "mode" in content_dict["variables"]:
                LOGGER.debug("Found 'mode' variable in %s", remote)
                return "remediate"
            return None
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.warning("Something went wrong when trying to determine mode for %s", remote)
            LOGGER.exception(exception)
            return None
