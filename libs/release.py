import re
import platform
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import libs.utility as Util

# Only import Windows-specific modules when needed
if re.search("windows", platform.system(), re.IGNORECASE):
    import urllib3
    import requests


class ReleaseInfo:
    """Data class to store release information."""

    def __init__(self, folder_name: str = "", release_name: str = "",
                 release_link: str = "", revision_num: int = 0,
                 release_date: str = "20051104"):
        self.folder_name = folder_name
        self.release_name = release_name
        self.release_link = release_link
        self.revision_num = revision_num
        self.release_date = release_date
        self.release_date_num = int(release_date) if release_date.isdigit() else 20051104


class FulsimRelease:
    """Main class for handling Fulsim releases."""

    # Class constants
    WINDOWS_BASE_URLS = {
        'cobalt': 'https://gfx-assets.fm.intel.com/artifactory/gfx-cobalt-assets-fm/Cobalt/Windows',
        'xesim': 'https://gfx-assets.fm.intel.com/artifactory/gfx-cobalt-assets-fm/XeSim/Windows'
    }

    LINUX_RELEASE_PATHS = {
        'ATS': '/nfs/site/disks/cobalt_ats_release/ReleaseBinaries/Gen12GT/Gen12HPGT',
        'ADL': '/nfs/site/disks/fm_lkf_00001/ReleaseBinaries/Gen12GT/ADL',
        'PVC': '/nfs/site/disks/fm_lkf_00001/ReleaseBinaries/Gen12GT/PVC',
        'DG1': '/nfs/site/disks/fm_lkf_00001/ReleaseBinaries/Gen12GT/DG1',
        'DG2': '/nfs/site/disks/cobalt_dg2_release/ReleaseBinaries/Cobalt/DG2',
        'MTL': '/nfs/site/disks/cobalt_mtl_release/ReleaseBinaries/Cobalt/MTL',
        'ELG': '/nfs/site/disks/cobalt_elg_release/ReleaseBinaries/Cobalt/ELG',
        'LNL': '/nfs/site/disks/cobalt_lnl_release/ReleaseBinaries/Cobalt/LNL',
        'ACMR': '/nfs/site/disks/cobalt_acmr_sles11_release/ReleaseBinaries/Cobalt/ACMR',
        'CLS': '/nfs/site/disks/cobalt_cls_release/ReleaseBinaries/Cobalt/CLS',
        'FCS': '/nfs/site/disks/cobalt_fcs_release/ReleaseBinaries/Cobalt/FCS',
        'PTL': '/nfs/site/disks/cobalt_ptl_release/ReleaseBinaries/Cobalt/PTL',
        'NVL': '/nfs/site/disks/xesim_xe3p_v2_release/ReleaseBinaries/XeSim/XE3P_V2',
        'CRI': '/nfs/site/disks/xesim_xe3p_v2_release/ReleaseBinaries/XeSim/XE3P_V2_SLES15',
        'TTL': '/nfs/site/disks/xesim_release/XeSim/MAIN',
        'HML': '/nfs/site/disks/xesim_release/XeSim/MAIN'
    }

    #for Windows https://gfx-assets.fm.intel.com/artifactory/gfx-cobalt-assets-fm/XeSim/Windows/
    PROJECT_MAPPINGS = {
        'NVL': 'XE3P_V2',
        'XE3P_V2': 'XE3P_V2',
        'CRI': 'XE3P_V2_SLES15',
        'TTL': 'MAIN',
        'HML': 'MAIN'
    }

    MIN_REVISION_OVERRIDES = {
        'ATS': 10000,
        'ACMR': 53726
    }

    def __init__(self):
        self.username = ""
        self.password = ""
        self.utility = Util.Utility()
        self.release_set: List[ReleaseInfo] = []
        self.max_releases = 100
        self.min_revision_num = 40000

    def get_linux_aubload_path(self, release_name: str) -> Optional[str]:
        """Find and return the aubload path for a given release name."""
        print(f"Searching {release_name}", end="")

        for release in self.release_set:
            if release.release_name.strip() == release_name.strip():
                print(" ==> found")
                return release.release_link

        print(" ==> not found")
        return None

    def get_linux_grits_path(self, release_name: str) -> Optional[str]:
        """Get the grits path for a given release."""
        aubload_path = self.get_linux_aubload_path(release_name)
        return os.path.join(aubload_path, "grits") if aubload_path else None

    def print_release_set(self, release_set: List[ReleaseInfo]) -> None:
        """Print release set information for debugging."""
        for release in release_set:
            print("------------")
            print(f"Release name: {release.release_name}")
            print(f"Revision num: {release.revision_num}")
            print(f"Release date: {release.release_date}")

    def _parse_release_folder(self, folder_path: str, project_name: str, is_l1: bool) -> Optional[ReleaseInfo]:
        """Parse a single release folder and return ReleaseInfo if valid."""
        if not folder_path:
            return None

        release = ReleaseInfo()
        release.release_link = folder_path
        release.folder_name = release.release_name = os.path.basename(folder_path)

        split_elements = release.release_name.split("-")
        if len(split_elements) <= 1:
            return None

        try:
            release.revision_num = int(split_elements[1])
            release.release_date = split_elements[0]
            release.release_date_num = int(split_elements[0])
        except (ValueError, IndexError):
            return None

        if not release.revision_num:
            return None

        # Set release name with project prefix
        prefix = f"{project_name.lower()}_l1_" if is_l1 else f"{project_name.lower()}_"
        release.release_name = prefix + release.release_name

        return release

    def get_l2_or_l1_release_set(self, project_name: str, is_l1: bool, release_path: str) -> List[ReleaseInfo]:
        """Get L1 or L2 release set from the given path."""
        if not os.access(release_path, os.R_OK):
            print(f"Path not readable! {project_name}: {release_path}")
            return []

        try:
            folder_paths = self.utility.getSubfolderPathFromDir(release_path)
            release_set = []

            for folder_path in folder_paths:
                release = self._parse_release_folder(folder_path, project_name, is_l1)
                if release:
                    release_set.append(release)

            return release_set

        except Exception as e:
            print(f"Error processing releases: {e}")
            return []

    def get_linux_release_set(self, project_name: str) -> List[str]:
        """Get Linux release set for the specified project."""
        project_upper = project_name.upper()
        print("project_upper:",project_upper)
        if project_upper not in self.LINUX_RELEASE_PATHS:
            raise Exception(f"Project not supported: {project_upper}")

        linux_release_base = self.LINUX_RELEASE_PATHS[project_upper]
        self.min_revision_num = self.MIN_REVISION_OVERRIDES.get(project_upper, 40000)

        print(f"Scanning linux release base: {linux_release_base}")

        # Get L2 releases
        print("Looking for linux L2 releases...")
        l2_releases = self.get_l2_or_l1_release_set(project_name, False, linux_release_base)
        print(f"\t\t==> total: {len(l2_releases)}")

        # Get L1 releases
        print("Looking for linux L1 releases...")
        l1_path = os.path.join(linux_release_base, "L1")
        l1_releases = self.get_l2_or_l1_release_set(project_name, True, l1_path)
        print(f"\t\t==> total: {len(l1_releases)}")

        # Filter and combine releases
        self.release_set = [
            release for release in (l2_releases + l1_releases)
            if release.revision_num > self.min_revision_num
        ]

        print(f"Total releases: {len(self.release_set)}")

        if not self.release_set:
            return ["L1 and L2 releases are not accessible!"]

        # Sort by revision number (descending) and extract names
        self.release_set.sort(key=lambda x: x.revision_num, reverse=True)
        return [release.release_name for release in self.release_set]

    def get_user_info(self, username: str, password: str) -> None:
        """Set user credentials."""
        self.username = username
        self.password = password

    def _get_windows_config(self, project_name: str) -> tuple[str, str]:
        """Get Windows URL and project mapping for the given project."""
        project_upper = project_name.upper()

        if project_upper in ['MTL', 'PTL','CLS','FCS','LNL','ELG']:
            return self.WINDOWS_BASE_URLS['cobalt'], project_upper
        elif project_upper in self.PROJECT_MAPPINGS:
            mapped_project = self.PROJECT_MAPPINGS[project_upper]
            return self.WINDOWS_BASE_URLS['xesim'], mapped_project
        else:
            raise Exception(f"Project not supported: {project_upper}")

    def check_password(self, project_name: str, user_id: str, password: str) -> int:
        """Check if the provided credentials are valid. Returns 0 for success, 1 for auth failure, 2 for error."""
        try:
            base_url, mapped_project = self._get_windows_config(project_name)

            http = urllib3.PoolManager()
            url = f"{base_url}/{mapped_project.upper()}"
            headers = urllib3.make_headers(basic_auth=f"{user_id}:{password}")

            response = http.request('GET', url, headers=headers)
            return 0 if response.status == 200 else 1

        except Exception as e:
            print(f"Error checking password: {e}")
            return 2

    def get_windows_release_set(self, project_name: str) -> List[str]:
        """Get Windows release set for the specified project."""
        base_url, mapped_project = self._get_windows_config(project_name)

        http = urllib3.PoolManager()
        url = f"{base_url}/{mapped_project.upper()}"
        headers = urllib3.make_headers(basic_auth=f"{self.username}:{self.password}")

        response = http.request('GET', url, headers=headers)

        # Extract revision numbers from HTML response
        revisions = re.findall(r">(\d+)/", response.data.decode('utf-8'))
        revisions = sorted(revisions, key=int, reverse=True)

        self.release_set = []
        release_names = []

        for revision in revisions:
            release = ReleaseInfo()
            release.folder_name = revision
            release.release_name = f"{mapped_project.upper()}-{revision}-Windows"
            release.release_link = f"{url}/{revision}/{release.release_name}.zip"

            self.release_set.append(release)
            release_names.append(release.release_name)

        return release_names

    def download_and_unzip_release(self, release_name: str, destination_path: str) -> Optional[str]:
        """Download and unzip a release to the specified destination."""
        # Find release link
        release_link = None
        for release in self.release_set:
            if release.release_name == release_name:
                release_link = release.release_link
                break

        if not release_link:
            print(f"Release not found: {release_name}")
            return None

        dst_folder = Path(destination_path) / release_name
        print(f"Downloading release {release_name} to {dst_folder}")
        print(f"Release link: {release_link}")

        # Check if already exists
        if dst_folder.is_dir() and not self.utility.IsDirEmpty(str(dst_folder)):
            print(f"Release folder exists: {dst_folder}")
            return str(dst_folder)

        # Create destination directory
        dst_folder.mkdir(parents=True, exist_ok=True)

        # Download file
        try:
            response = requests.get(
                release_link,
                allow_redirects=True,
                stream=True,
                verify=False,
                auth=(self.username, self.password)
            )
            response.raise_for_status()

            zip_file_path = dst_folder / f"{release_name}.zip"
            with open(zip_file_path, "wb") as f:
                f.write(response.content)

            # Unzip file
            print(f"Unzipping {zip_file_path} to {dst_folder}", end='')
            import zipfile
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(dst_folder)
            print(" ==> done")

            return str(dst_folder)

        except Exception as e:
            print(f"Error downloading/unzipping release: {e}")
            return None