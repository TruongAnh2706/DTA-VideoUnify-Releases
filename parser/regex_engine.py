"""
DTA VideoUnify Pro - Smart Multi-Level Hierarchy Regex Engine
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
Advanced Multi-Level Folder Traversal & ID Stripping Algorithm!
"""

import os
import re
from typing import Dict, List, Tuple
from config import SUPPORTED_VIDEO_EXTS


class SeriesRegexParser:
    """
    Multi-pattern Regex Engine capable of extracting Drama/Series Titles
    and integer Episode Numbers from nested multi-level directory structures.
    Smartly resolves parent series folders (skipping 'Episodes', 'Promotions' subfolders)
    and strips brackets/ID prefixes like '[2073307367864205313] - Title'.
    """

    # Pure Episode Filename Patterns (e.g. E01, E02, EP01, Ep_02, Tập 01, Tap 1, 01...)
    PURE_EPISODE_PATTERNS = [
        r'^[eE][pP]?[\.\_\s\-]*(?P<ep>\d+)$',                # E01, EP01, Ep.01, E1
        r'^[第tT]â?p?[\.\_\s\-]*(?P<ep>\d+)[ tập集]?$',      # Tập 01, Tap01, 第01集
        r'^(?P<ep>\d{1,4})$',                                # 01, 02, 001
    ]

    # Full Series + Episode Patterns embedded in filename
    PATTERNS = [
        # Asian format: Title第01集 / Title Tập 01 / Title Tap 1
        r'^(?P<title>.+?)[_\s\-\.][第tT]â?p?[_\s\-\.]*(?P<ep>\d+)[ tập集]?.*$',
        r'^(?P<title>.+?)[第](?P<ep>\d+)[集話].*$',

        # Western Season/Episode format: Title S01E05 / Title s1e5
        r'^(?P<title>.+?)[_\s\-\.][sS](?P<season>\d+)[eE](?P<ep>\d+).*$',
        
        # Explicit Ep format: Title_EP01 / Title - Ep. 1 / Title EP_1
        r'^(?P<title>.+?)[_\s\-\.][eE][pP][\.\_\s\-]*(?P<ep>\d+).*$',

        # Delimited Number format: Title - 01 / Title_01 / Title.01
        r'^(?P<title>.+?)[_\s\-\.]+(?P<ep>\d{1,4})$',
        
        # Trailing Space/Underscore Number: Title 01 / Title_1
        r'^(?P<title>.+?)\s+(?P<ep>\d{1,4})$',
    ]

    # Generic subfolder names that should be bypassed to find true parent Drama Title
    GENERIC_SUBFOLDERS = {
        "episodes", "episode", "video", "videos", "tập phim", "tap phim", "tập", "tap",
        "promotions", "promotion", "promo", "promos", "extras", "extra", "bonus", "trailer", "trailers"
    }

    @classmethod
    def clean_series_title(cls, raw_title: str) -> str:
        """
        Cleans series title by stripping ID brackets like '[2073307367864205313] - My X-Ray...'
        and sanitizing punctuation.
        """
        if not raw_title:
            return "Bộ Phim Chưa Đặt Tên"

        clean = raw_title.strip()
        # Strip leading brackets with IDs like [123456789] or (123456789)
        clean = re.sub(r'^[\[\(]\d+[\]\)]\s*[\-\_\s]*', '', clean)
        # Strip trailing brackets with IDs
        clean = re.sub(r'\s*[\-\_\s]*[\[\(]\d+[\]\)]$', '', clean)
        # Replace underscores and dots with spaces
        clean = clean.replace('_', ' ').replace('.', ' ')
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean.title() if clean else raw_title.title()

    @classmethod
    def resolve_series_title_from_path(cls, file_full_path: str, scan_root_folder: str) -> str:
        """
        Smartly traverses upward from file_full_path to scan_root_folder to determine
        the actual Drama/Series folder title.
        Bypasses generic subfolders like 'Episodes', 'Promotions'.
        """
        abs_file = os.path.abspath(file_full_path)
        abs_root = os.path.abspath(scan_root_folder)

        curr_dir = os.path.dirname(abs_file)

        candidate_title = ""

        while curr_dir and curr_dir != abs_root and os.path.dirname(curr_dir) != curr_dir:
            folder_name = os.path.basename(curr_dir).strip()
            
            # If folder_name is not a generic subfolder like 'Episodes', this is our drama title!
            if folder_name.lower() not in cls.GENERIC_SUBFOLDERS:
                candidate_title = folder_name
                break
            
            # Walk up to parent directory
            parent_dir = os.path.dirname(curr_dir)
            if parent_dir == abs_root or not parent_dir:
                break
            curr_dir = parent_dir

        if not candidate_title:
            # Fallback to direct parent folder or root folder name
            direct_parent = os.path.basename(os.path.dirname(abs_file))
            if direct_parent.lower() in cls.GENERIC_SUBFOLDERS:
                candidate_title = os.path.basename(abs_root)
            else:
                candidate_title = direct_parent

        return cls.clean_series_title(candidate_title)

    @classmethod
    def parse_file(cls, filename: str, file_full_path: str, scan_root_folder: str) -> Tuple[str, int]:
        """
        Parses a file and its full path to accurately determine (Series Title, Episode Number).
        Handles nested 'Episodes' folders and strips ID prefixes like '[2073307367864205313] - '.
        """
        name_without_ext = os.path.splitext(filename)[0].strip()

        # 1. Check if filename is a bare episode (E01, E02, EP01, 01...)
        for p_ep in cls.PURE_EPISODE_PATTERNS:
            m_ep = re.match(p_ep, name_without_ext, re.IGNORECASE)
            if m_ep:
                try:
                    ep_num = int(m_ep.group('ep'))
                    title = cls.resolve_series_title_from_path(file_full_path, scan_root_folder)
                    return title, ep_num
                except (ValueError, TypeError):
                    pass

        # 2. Check embedded full series + episode patterns in filename
        for pattern in cls.PATTERNS:
            match = re.match(pattern, name_without_ext, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                title = groups.get('title', '').strip()
                title = cls.clean_series_title(title)

                try:
                    ep_num = int(groups.get('ep', 1))
                    if title and ep_num >= 0:
                        return title, ep_num
                except (ValueError, TypeError):
                    continue

        # 3. Fallback: Use smart parent folder for title, and try to extract trailing number from filename as ep
        smart_title = cls.resolve_series_title_from_path(file_full_path, scan_root_folder)
        trailing_num_match = re.search(r'(\d+)', name_without_ext)
        ep_num = int(trailing_num_match.group(1)) if trailing_num_match else 1

        return smart_title, ep_num

    @classmethod
    def scan_directory(cls, folder_path: str) -> Dict[str, List[Tuple[int, str]]]:
        """
        Recursively scans directory tree for video files, groups them by Series Title,
        and sorts episodes numerically in ascending order.
        Returns: { "Series Title": [ (Ep1, "path1"), (Ep2, "path2"), ... ] }
        """
        series_dict: Dict[str, List[Tuple[int, str]]] = {}

        if not os.path.exists(folder_path):
            return series_dict

        abs_root = os.path.abspath(folder_path)

        for root, dirs, files in os.walk(abs_root):
            # Skip scanning 'Promotions' or 'Trailers' subfolders if they only contain promo materials
            # (Keep scanning Episodes)
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_VIDEO_EXTS:
                    full_path = os.path.join(root, file)

                    # Determine if file is in a Promo subfolder (optional check, but still parse episode if valid)
                    rel_dir = os.path.relpath(root, abs_root).lower()
                    if "promotion" in rel_dir or "promo" in rel_dir:
                        # Skip trailers/promos from main episode merge queue
                        continue

                    title, ep_num = cls.parse_file(file, full_path, abs_root)

                    if title not in series_dict:
                        series_dict[title] = []
                    
                    series_dict[title].append((ep_num, full_path))

        # Sort episodes numerically for each series
        sorted_series_dict = {}
        for title, ep_list in series_dict.items():
            # Sort by episode number (int), then by file path
            sorted_episodes = sorted(ep_list, key=lambda x: (x[0], x[1]))
            sorted_series_dict[title] = sorted_episodes

        return sorted_series_dict
