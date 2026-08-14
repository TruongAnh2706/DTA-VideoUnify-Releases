"""
DTA VideoUnify Pro - Smart Multi-Level Hierarchy Regex Engine
Phát triển bởi DTA Studio - Chủ quản: Đức Trường
Email: ductruong.onl@gmail.com | Zalo/SĐT: 0962775506
Website: https://dta-studio.vercel.app/
Advanced Multi-Series Mixed Folder Traversal & Universal Title-Episode Extractor Algorithm!
"""

import os
import re
from typing import Dict, List, Tuple
from config import SUPPORTED_VIDEO_EXTS


class SeriesRegexParser:
    """
    Universal Regex Engine capable of extracting Drama/Series Titles
    and integer Episode Numbers even when MULTIPLE DIFFERENT SERIES
    are mixed together inside a single folder (e.g. '3. Video Part').
    Handles '_E01', '_E02', '_Ep01', '_Tập 01', '_01' patterns perfectly.
    """

    PURE_EPISODE_PATTERNS = [
        r'^[eE][pP]?[\.\_\s\-]*(?P<ep>\d+)$',
        r'^[第tT]â?p?[\.\_\s\-]*(?P<ep>\d+)[ tập集]?$',
        r'^(?P<ep>\d{1,4})$',
    ]

    # Universal Title + Episode Number Extraction Patterns
    PATTERNS = [
        # Match 'I Kissed a Vampire Queen_E01', 'Movie_E02', 'Series-E10', 'Title.E05', 'Title_Ep01'
        r'^(?P<title>.+?)[_\s\-\.][eE][pP]?[_\s\-\.]*(?P<ep>\d+).*$',
        
        # Match 'Title_Tập 01', 'Title_Tap_02', 'Title Tập03'
        r'^(?P<title>.+?)[_\s\-\.][第tT]â?p?[_\s\-\.]*(?P<ep>\d+)[ tập集]?.*$',
        
        # Match Chinese/Japanese episode syntax 'Title 第01集'
        r'^(?P<title>.+?)[第](?P<ep>\d+)[集話].*$',
        
        # Match Season & Episode syntax 'Title_S01E01'
        r'^(?P<title>.+?)[_\s\-\.][sS](?P<season>\d+)[eE](?P<ep>\d+).*$',
        
        # Match 'Title_01', 'Title-01', 'Title.01'
        r'^(?P<title>.+?)[_\s\-\.]+(?P<ep>\d{1,4})$',
        
        # Match 'Title 01'
        r'^(?P<title>.+?)\s+(?P<ep>\d{1,4})$',
    ]

    GENERIC_SUBFOLDERS = {
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
        "episodes", "episode", "video", "videos", "tập phim", "tap phim", "tập", "tap",
        "promotions", "promotion", "promo", "promos", "extras", "extra", "bonus", "trailer", "trailers",
        "video part", "3. video part", "4. video qc", "video qc", "thumbnail", "2. thumbnail", "log", "1. log",
        "thong tin phim", "5. thong tin phim", "input", "output", "test", "temp", "tmp"
    }

    @classmethod
    def clean_series_title(cls, raw_title: str) -> str:
        if not raw_title:
            return "Bộ Phim Chưa Đặt Tên"

        clean = raw_title.strip()
        # Remove bracketed prefixes like [2073307367864205313] or (2024)
        clean = re.sub(r'^[\[\(]\d+[\]\)]\s*[\-\_\s]*', '', clean)
        clean = re.sub(r'\s*[\-\_\s]*[\[\(]\d+[\]\)]$', '', clean)
        # Clean trailing separators
        clean = re.sub(r'[\_\-\.]+$', '', clean).strip()
        clean = clean.replace('_', ' ').replace('.', ' ')
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean.title() if clean else raw_title.title()

    @classmethod
    def resolve_series_title_from_path(cls, file_full_path: str, scan_root_folder: str) -> str:
        abs_file = os.path.abspath(file_full_path)
        abs_root = os.path.abspath(scan_root_folder)

        curr_dir = os.path.dirname(abs_file)
        candidate_title = ""

        while curr_dir and curr_dir != abs_root and os.path.dirname(curr_dir) != curr_dir:
            folder_name = os.path.basename(curr_dir).strip()
            if folder_name.lower() not in cls.GENERIC_SUBFOLDERS:
                candidate_title = folder_name
                break

            parent_dir = os.path.dirname(curr_dir)
            if parent_dir == abs_root or not parent_dir:
                break
            curr_dir = parent_dir

        if not candidate_title:
            direct_parent = os.path.basename(os.path.dirname(abs_file))
            if direct_parent.lower() in cls.GENERIC_SUBFOLDERS:
                candidate_title = os.path.basename(abs_root)
            else:
                candidate_title = direct_parent

        return cls.clean_series_title(candidate_title)

    @classmethod
    def parse_file(cls, filename: str, file_full_path: str, scan_root_folder: str) -> Tuple[str, int]:
        name_without_ext = os.path.splitext(filename)[0].strip()

        # 1. First test if filename contains BOTH Title and Episode Number (e.g. 'I Kissed a Vampire Queen_E01')
        for pattern in cls.PATTERNS:
            match = re.match(pattern, name_without_ext, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                title = groups.get('title', '').strip()
                clean_title = cls.clean_series_title(title)

                try:
                    ep_num = int(groups.get('ep', 1))
                    # Ensure title is meaningful (not just a single number)
                    if clean_title and not clean_title.isdigit() and len(clean_title) > 1:
                        return clean_title, ep_num
                except (ValueError, TypeError):
                    continue

        # 2. Test for pure episode number patterns (e.g. 'E01.mp4', '01.mp4', 'Tập 1.mp4')
        for p_ep in cls.PURE_EPISODE_PATTERNS:
            m_ep = re.match(p_ep, name_without_ext, re.IGNORECASE)
            if m_ep:
                try:
                    ep_num = int(m_ep.group('ep'))
                    title = cls.resolve_series_title_from_path(file_full_path, scan_root_folder)
                    return title, ep_num
                except (ValueError, TypeError):
                    pass

        # 3. Fallback: Parse title from parent folder path and trailing number from filename
        smart_title = cls.resolve_series_title_from_path(file_full_path, scan_root_folder)
        trailing_num_match = re.search(r'(\d+)', name_without_ext)
        ep_num = int(trailing_num_match.group(1)) if trailing_num_match else 1

        return smart_title, ep_num

    @classmethod
    def scan_directory(cls, folder_path: str) -> Dict[str, List[Tuple[int, str]]]:
        series_dict: Dict[str, List[Tuple[int, str]]] = {}

        if not os.path.exists(folder_path):
            return series_dict

        abs_root = os.path.abspath(folder_path)

        for root, dirs, files in os.walk(abs_root):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_VIDEO_EXTS:
                    # Skip previously merged result files like _FULL.mp4 or _Merged.mp4 or TEST_MERGE
                    file_lower = file.lower()
                    if "_full" in file_lower or "_merged" in file_lower or "test_merge" in file_lower:
                        continue

                    full_path = os.path.join(root, file)

                    rel_dir = os.path.relpath(root, abs_root).lower()
                    if "promotion" in rel_dir or "promo" in rel_dir:
                        continue

                    title, ep_num = cls.parse_file(file, full_path, abs_root)

                    if title not in series_dict:
                        series_dict[title] = []

                    series_dict[title].append((ep_num, full_path))

        sorted_series_dict = {}
        for title, ep_list in series_dict.items():
            # Sort episodes by episode number, then file path
            sorted_episodes = sorted(ep_list, key=lambda x: (x[0], x[1]))
            sorted_series_dict[title] = sorted_episodes

        return sorted_series_dict
