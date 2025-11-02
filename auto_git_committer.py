#!/usr/bin/env python3
"""Automate committing and pushing multiple Git repositories.

This tool scans local directories (including Docker-oriented projects),
initializes repositories if needed, commits pending changes, and pushes
to GitHub under the ``mvallarautomations`` account.

Usage example::

    python auto_git_committer.py --roots . ~/projects \
        --token-env MVALLARAUTOMATIONS_TOKEN --create-missing

Key features
------------

* Finds existing Git repositories under the provided roots.
* Optionally initializes Git repositories for directories containing a
  ``Dockerfile`` or ``docker-compose`` file.
* Stages all changes, creates commits, and pushes to GitHub.
* Can automatically create remote repositories in the target account.

Environment
-----------

Provide a GitHub personal access token via the ``--token-env`` flag.
The token needs the ``repo`` scope and must belong to the
``mvallarautomations`` account (or an account with permission to push to
that namespace).
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import requests
except ImportError as exc:  # pragma: no cover - requirements should include requests
    raise SystemExit(
        "The 'requests' package is required. Please install requirements.txt"
    ) from exc


# ---------------------------------------------------------------------------
# Utility helpers


def run(
    cmd: Sequence[str],
    cwd: Path,
    *,
    check: bool = True,
    capture: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    """Run a shell command inside *cwd*.

    Args:
        cmd: Command tokens (without shell=True).
        cwd: Working directory.
        check: When True, raise on non-zero exit codes.
        capture: When True, capture stdout/stderr.

    Returns:
        ``subprocess.CompletedProcess`` instance.
    """

    stdout = subprocess.PIPE if capture else None
    stderr = subprocess.PIPE if capture else None
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=stdout,
        stderr=stderr,
        text=True,
        env=env,
    )
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def git_available() -> bool:
    """Ensure Git is installed."""

    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def mask_secret(secret: str, *, visible: int = 4) -> str:
    """Return a masked representation of a secret string."""

    if not secret:
        return ""
    visible = max(0, visible)
    if len(secret) <= visible:
        return "*" * len(secret)
    return f"{'*' * (len(secret) - visible)}{secret[-visible:]}"


def collect_git_repos(roots: Iterable[Path]) -> List[Path]:
    """Discover Git repositories under *roots* (non-recursive into nested repos)."""

    repos: List[Path] = []
    seen: set[Path] = set()

    for root in roots:
        root = root.resolve()
        if not root.exists():
            continue

        for dirpath, dirnames, filenames in os.walk(root):
            dirpath_path = Path(dirpath)

            if (dirpath_path / ".git").is_dir():
                repo_root = dirpath_path.resolve()
                if repo_root not in seen:
                    repos.append(repo_root)
                    seen.add(repo_root)
                # Avoid walking into nested repositories
                dirnames[:] = []
                continue

            # Optimisation: don't descend into .git directories
            if ".git" in dirnames:
                dirnames.remove(".git")

    return sorted(repos)


def collect_docker_projects(roots: Iterable[Path]) -> List[Path]:
    """Find directories containing Docker artefacts."""

    docker_dirs: set[Path] = set()

    docker_files = {"docker-compose.yml", "docker-compose.yaml", "Dockerfile"}

    for root in roots:
        root = root.resolve()
        if not root.exists():
            continue

        for dirpath, dirnames, filenames in os.walk(root):
            dirpath_path = Path(dirpath)
            if any(d in filenames for d in docker_files):
                docker_dirs.add(dirpath_path.resolve())

            # Skip Git internals early
            if ".git" in dirnames:
                dirnames.remove(".git")

    return sorted(docker_dirs)


def inside_any_repo(path: Path, repos: Sequence[Path]) -> bool:
    """Check whether *path* is inside any repository listed in *repos*."""

    for repo in repos:
        try:
            path.resolve().relative_to(repo)
            return True
        except ValueError:
            continue
    return False


def default_commit_message(repo: Path) -> str:
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"Automated sync for {repo.name} ({timestamp})"


def ensure_main_branch(repo_path: Path) -> None:
    """Ensure newly initialised repositories use ``main``."""

    try:
        run(["git", "symbolic-ref", "HEAD", "refs/heads/main"], repo_path, check=True)
    except subprocess.CalledProcessError:
        # Git 2.28+ supports --initial-branch; if not available, ignore.
        pass


# ---------------------------------------------------------------------------
# GitHub interactions


class GitHubClient:
    """Minimal GitHub REST client for repo discovery/creation."""

    def __init__(self, token: Optional[str], *, owner: str):
        self.owner = owner
        self.session = requests.Session()
        self.api_base = "https://api.github.com"
        self.token = token
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["Accept"] = "application/vnd.github+json"

    def repo_exists(self, name: str) -> bool:
        url = f"{self.api_base}/repos/{self.owner}/{name}"
        response = self.session.get(url, timeout=15)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        raise RuntimeError(f"GitHub API error ({response.status_code}): {response.text}")

    def _owner_type(self) -> str:
        url = f"{self.api_base}/users/{self.owner}"
        response = self.session.get(url, timeout=15)
        if response.status_code != 200:
            raise RuntimeError(f"Cannot resolve GitHub owner '{self.owner}': {response.text}")
        data = response.json()
        return data.get("type", "User")

    def ensure_repo(self, name: str, *, private: bool = False) -> None:
        if self.repo_exists(name):
            return

        owner_type = self._owner_type()
        if owner_type == "Organization":
            url = f"{self.api_base}/orgs/{self.owner}/repos"
        else:
            url = f"{self.api_base}/user/repos"

        payload = {"name": name, "private": private, "auto_init": False}
        response = self.session.post(url, json=payload, timeout=15)
        if response.status_code not in {200, 201}:
            raise RuntimeError(
                f"Failed to create GitHub repo '{self.owner}/{name}': {response.status_code} {response.text}"
            )


# ---------------------------------------------------------------------------
# Core processor


@dataclass
class ProcessResult:
    path: Path
    committed: bool = False
    pushed: bool = False
    skipped_reason: Optional[str] = None
    initialized: bool = False
    branch: Optional[str] = None
    commit_message: Optional[str] = None


@dataclass
class RepoProcessor:
    owner: str
    token: Optional[str]
    commit_message: Optional[str]
    dry_run: bool
    create_missing: bool
    init_docker: bool
    include_clean: bool
    roots: List[Path]
    github: GitHubClient = field(init=False)

    def __post_init__(self) -> None:
        self.github = GitHubClient(self.token, owner=self.owner)

    # -- discovery -----------------------------------------------------------------

    def discover(self) -> Tuple[List[Path], List[Path]]:
        repo_roots = collect_git_repos(self.roots)

        docker_projects = collect_docker_projects(self.roots)
        docker_targets = [
            path
            for path in docker_projects
            if not inside_any_repo(path, repo_roots)
        ]

        return repo_roots, docker_targets

    # -- initialisation ------------------------------------------------------------

    def initialise_repo(self, path: Path) -> bool:
        if (path / ".git").is_dir():
            return False

        if self.dry_run:
            print(f"[DRY-RUN] git init {path}")
            return True

        path.mkdir(parents=True, exist_ok=True)

        try:
            run(["git", "init", "--initial-branch", "main"], path, check=True)
        except subprocess.CalledProcessError:
            # Fallback for older git versions
            run(["git", "init"], path, check=True)
            ensure_main_branch(path)

        return True

    # -- processing ----------------------------------------------------------------

    def process_repo(self, repo_path: Path, *, initialized: bool = False) -> ProcessResult:
        result = ProcessResult(path=repo_path, initialized=initialized)

        try:
            branch = self._current_branch(repo_path)
        except subprocess.CalledProcessError:
            result.skipped_reason = "Failed to read branch"
            return result

        if not branch or branch == "HEAD":
            result.skipped_reason = "Detached HEAD"
            return result

        result.branch = branch

        if not self.include_clean and not self._is_dirty(repo_path):
            result.skipped_reason = "Clean repository"
            return result

        message = self.commit_message or default_commit_message(repo_path)
        result.commit_message = message

        if self.dry_run:
            print(f"[DRY-RUN] Would commit in {repo_path} with message: {message}")
            result.committed = True
        else:
            self._stage_all(repo_path)
            if not self._has_staged(repo_path):
                result.skipped_reason = "No staged changes"
                return result
            self._commit(repo_path, message)
            result.committed = True

        if self.create_missing and self.token:
            repo_name = repo_path.name
            if self.dry_run:
                print(f"[DRY-RUN] Would ensure GitHub repo {self.owner}/{repo_name}")
            else:
                self.github.ensure_repo(repo_name)

        push_success = self._push(repo_path, branch)
        result.pushed = push_success
        if not push_success and result.skipped_reason is None:
            result.skipped_reason = "Push failed"

        return result

    # -- git helpers ----------------------------------------------------------------

    def _is_dirty(self, repo_path: Path) -> bool:
        result = run(["git", "status", "--porcelain"], repo_path, capture=True, check=True)
        return bool(result.stdout.strip())

    def _stage_all(self, repo_path: Path) -> None:
        run(["git", "add", "-A"], repo_path, check=True)

    def _has_staged(self, repo_path: Path) -> bool:
        result = run(["git", "diff", "--cached", "--quiet"], repo_path, check=False)
        return result.returncode != 0

    def _commit(self, repo_path: Path, message: str) -> None:
        env = os.environ.copy()
        env.setdefault("GIT_COMMITTER_NAME", "Automation Bot")
        env.setdefault("GIT_COMMITTER_EMAIL", "automation@mvallarautomations")
        env.setdefault("GIT_AUTHOR_NAME", env["GIT_COMMITTER_NAME"])
        env.setdefault("GIT_AUTHOR_EMAIL", env["GIT_COMMITTER_EMAIL"])

        run(["git", "commit", "-m", message], repo_path, check=True, env=env)

    def _current_branch(self, repo_path: Path) -> str:
        result = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_path, capture=True, check=True)
        return result.stdout.strip()

    def _ensure_remote(self, repo_path: Path) -> str:
        desired_url = f"https://github.com/{self.owner}/{repo_path.name}.git"

        # Check existing remote
        existing_url = None
        try:
            result = run(["git", "remote", "get-url", "origin"], repo_path, capture=True, check=True)
            existing_url = result.stdout.strip()
        except subprocess.CalledProcessError:
            existing_url = None

        if existing_url and self.owner in existing_url:
            return desired_url

        if self.dry_run:
            action = "set-url" if existing_url else "add"
            print(f"[DRY-RUN] git remote {action} origin {desired_url}")
            return desired_url

        if existing_url:
            run(["git", "remote", "set-url", "origin", desired_url], repo_path, check=True)
        else:
            run(["git", "remote", "add", "origin", desired_url], repo_path, check=True)

        return desired_url

    def _push(self, repo_path: Path, branch: str) -> bool:
        try:
            remote_url = self._ensure_remote(repo_path)
        except subprocess.CalledProcessError:
            return False

        push_url = remote_url
        if self.token:
            from urllib.parse import quote

            quoted = quote(self.token, safe="")
            push_url = f"https://{quoted}:x-oauth-basic@github.com/{self.owner}/{repo_path.name}.git"

        cmd = ["git", "push", push_url, f"HEAD:{branch}"]

        if self.dry_run:
            print(f"[DRY-RUN] {' '.join(cmd[:-1])} {cmd[-1]}")
            return True

        env = os.environ.copy()
        env.setdefault("GIT_TERMINAL_PROMPT", "0")

        try:
            subprocess.run(cmd, cwd=str(repo_path), check=True, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except subprocess.CalledProcessError as exc:
            sys.stderr.write(
                f"[ERROR] Failed to push {repo_path} (branch {branch}): {exc.stderr or exc.stdout}\n"
            )
            return False


# ---------------------------------------------------------------------------
# CLI


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate commits across multiple repositories")

    parser.add_argument(
        "--roots",
        nargs="+",
        default=["."],
        help="Root directories to scan for repositories",
    )

    parser.add_argument(
        "--owner",
        default="mvallarautomations",
        help="GitHub account (user or organisation) that will receive the pushes",
    )

    parser.add_argument(
        "--token-env",
        default="MVALLARAUTOMATIONS_TOKEN",
        help="Environment variable containing a GitHub token",
    )

    parser.add_argument(
        "--commit-message",
        "-m",
        help="Commit message to use (defaults to an auto-generated message per repo)",
    )

    parser.add_argument(
        "--create-missing",
        action="store_true",
        help="Automatically create repositories on GitHub when they do not exist",
    )

    parser.add_argument(
        "--include-clean",
        action="store_true",
        help="Commit even when repositories appear clean (useful right after init)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without executing them",
    )

    parser.add_argument(
        "--init-docker",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Initialise Git repositories for Docker project directories",
    )

    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    if not git_available():
        sys.stderr.write("git is required but was not found on PATH\n")
        return 2

    args = parse_args(argv)

    token = os.environ.get(args.token_env)
    if not token:
        sys.stderr.write(
            f"[WARN] No token found in environment variable '{args.token_env}'. Pushes may fail.\n"
        )

    roots = [Path(p).expanduser().resolve() for p in args.roots]

    processor = RepoProcessor(
        owner=args.owner,
        token=token,
        commit_message=args.commit_message,
        dry_run=args.dry_run,
        create_missing=args.create_missing,
        init_docker=args.init_docker,
        include_clean=args.include_clean,
        roots=roots,
    )

    repo_roots, docker_dirs = processor.discover()

    print(f"Discovered {len(repo_roots)} existing Git repositories")
    print(f"Discovered {len(docker_dirs)} Docker project directories outside Git repos")

    to_process: List[Tuple[Path, bool]] = [(path, False) for path in repo_roots]

    if args.init_docker:
        for docker_dir in docker_dirs:
            initialised = processor.initialise_repo(docker_dir)
            to_process.append((docker_dir, initialised))

    results: List[ProcessResult] = []
    for repo_path, initialised in to_process:
        try:
            result = processor.process_repo(repo_path, initialized=initialised)
        except Exception as exc:
            sys.stderr.write(f"[ERROR] Unexpected failure in {repo_path}: {exc}\n")
            continue
        results.append(result)

    committed = sum(1 for r in results if r.committed)
    pushed = sum(1 for r in results if r.pushed)

    print("\nSummary:")
    print(f"  Repositories processed: {len(results)}")
    print(f"  Commits created:      {committed}")
    print(f"  Push successes:       {pushed}")

    failures = [r for r in results if (r.committed and not r.pushed) or (r.skipped_reason and not r.committed)]
    if failures:
        print("\nDetails:")
        for res in failures:
            reason = res.skipped_reason or "Unknown"
            print(f"  - {res.path}: {reason}")

    return 0 if pushed == committed else 1


if __name__ == "__main__":
    sys.exit(main())
