import argparse
import os
import re
import shutil
import uuid
from pathlib import Path



# ---------------------------
# Logging helper
# ---------------------------

def default_logger(msg: str):
    print(msg)


# ---------------------------
# Naming rules
# ---------------------------

def clean_number_suffix(text: str) -> str:
    """Remove trailing ' (number)' from a string."""
    return re.sub(r"\s+\(\d+\)$", "", text)


def folder_name_rule(name: str) -> str:
    """Folders: remove trailing (number), then ALL CAPS."""
    if not name:
        return name
    return clean_number_suffix(name).upper()


def file_name_rule(name: str) -> str:
    """
    Files:
    1) remove trailing ' (number)' from stem (before extension)
    2) lowercase stem
    3) uppercase only the first character of stem
    4) keep extension exactly as-is
    """
    if not name:
        return name

    p = Path(name)
    stem = p.stem
    suffix = p.suffix  # preserve extension casing

    if not stem:
        return name

    stem = clean_number_suffix(stem)
    stem = stem.lower()
    stem = stem[0].upper() + stem[1:] if stem else stem

    return stem + suffix


# ---------------------------
# Overwrite / merge helpers
# ---------------------------

def remove_path(target: Path):
    """Remove file or directory tree."""
    if not target.exists():
        return
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()


def merge_dirs(src_dir: Path, dst_dir: Path, dry_run: bool, log_callback=default_logger):
    """
    Merge src_dir into dst_dir, overwriting collisions.
    After merge, src_dir will be removed.
    """
    log_callback(f"      MERGE: {src_dir.name} -> {dst_dir.name}")

    if dry_run:
        log_callback("      DRY RUN: would merge directories (with overwrites)")
        return

    dst_dir.mkdir(exist_ok=True)

    for item in src_dir.iterdir():
        dst_item = dst_dir / item.name

        if item.is_dir():
            if dst_item.exists() and dst_item.is_file():
                log_callback(f"        OVERWRITE: removing file {dst_item.name} to replace with folder")
                remove_path(dst_item)
            dst_item.mkdir(exist_ok=True)
            merge_dirs(item, dst_item, dry_run=False, log_callback=log_callback)
            # item should be removed by recursion
        else:
            if dst_item.exists():
                log_callback(f"        OVERWRITE: {dst_item.name}")
                remove_path(dst_item)

            # Move file into destination
            shutil.move(str(item), str(dst_item))

    # Remove the now-empty source directory
    if src_dir.exists():
        try:
            src_dir.rmdir()
        except OSError:
            # If something is still there, force remove
            shutil.rmtree(src_dir)


def forced_temp_rename_with_overwrite(src: Path, final_dst: Path, dry_run: bool, kind: str, log_callback=default_logger) -> bool:
    """
    Always do:
      src -> __tmp__UUID__src -> final_dst
    If final_dst exists:
      - FILE: delete final_dst then rename
      - FOLDER: merge tmp_dir into final_dst (overwriting) then remove tmp_dir
    """
    if src.name == final_dst.name:
        # log_callback(f"      = No change needed ({kind})") # Optional: reduce noise
        return False

    tmp_name = f"__tmp__{uuid.uuid4().hex}__{src.name}"
    tmp_path = src.parent / tmp_name

    log_callback(f"      FROM: {src.name}")
    log_callback(f"      TMP:  {tmp_name}")
    log_callback(f"      TO:   {final_dst.name}")

    if dry_run:
        if final_dst.exists():
            log_callback(f"      NOTE: target exists -> would OVERWRITE ({kind})")
        log_callback(f"      DRY RUN: would rename {kind} via temp")
        return True

    try:
        # Step 1: src -> tmp
        src.rename(tmp_path)

        # Step 2: tmp -> final (with overwrite rules)
        if final_dst.exists():
            log_callback(f"      TARGET EXISTS -> OVERWRITE ({kind})")

            if tmp_path.is_dir():
                # Merge tmp folder into existing final folder
                if not final_dst.is_dir():
                    log_callback("      OVERWRITE: removing file to replace with folder")
                    remove_path(final_dst)
                    tmp_path.rename(final_dst)
                else:
                    merge_dirs(tmp_path, final_dst, dry_run=False, log_callback=log_callback)
            else:
                # File overwrite: remove existing and rename
                remove_path(final_dst)
                tmp_path.rename(final_dst)
        else:
            tmp_path.rename(final_dst)

        log_callback(f"      ✔ RENAMED {kind}")
        return True

    except PermissionError as e:
        log_callback(f"      ✖ PERMISSION ERROR: {e}")
        # attempt to rollback if tmp exists
        try:
            if tmp_path.exists() and not src.exists():
                tmp_path.rename(src)
        except Exception:
            pass
    except OSError as e:
        log_callback(f"      ✖ OS ERROR: {e}")
        # attempt to rollback if tmp exists
        try:
            if tmp_path.exists() and not src.exists():
                tmp_path.rename(src)
        except Exception:
            pass

    return False


# ---------------------------
# Core logic
# ---------------------------

def rename_tree(root: Path, dry_run: bool, log_callback=default_logger):
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    log_callback("=" * 78)
    log_callback(f"ROOT: {root}")
    log_callback(f"MODE: {'DRY RUN' if dry_run else 'APPLY (OVERWRITE ENABLED)'}")
    log_callback("RULES: folders -> ALL CAPS + remove ' (n)' | files -> clean '(n)', stem lower, first char upper")
    log_callback("NOTE: if target exists -> OVERWRITE (folders are MERGED with overwrites)")
    log_callback("=" * 78)

    visited_dirs = 0
    visited_files = 0
    actions = 0

    # Bottom-up traversal is critical for renaming folders safely
    for current_root, dirnames, filenames in os.walk(root, topdown=False):
        current_root = Path(current_root)
        visited_dirs += 1

        log_callback(f"\n📂 Visiting folder:")
        log_callback(f"   {current_root}")

        # Files first
        if filenames:
            log_callback("   📄 Files:")
        for fname in filenames:
            visited_files += 1
            src = current_root / fname
            desired = current_root / file_name_rule(fname)

            log_callback(f"    - Checking file: {fname}")
            if forced_temp_rename_with_overwrite(src, desired, dry_run, "FILE", log_callback):
                actions += 1

        # Then folders
        if dirnames:
            log_callback("   📁 Subfolders:")
        for dname in dirnames:
            src = current_root / dname
            desired = current_root / folder_name_rule(dname)

            log_callback(f"    - Checking folder: {dname}")
            if forced_temp_rename_with_overwrite(src, desired, dry_run, "FOLDER", log_callback):
                actions += 1

    log_callback("\n" + "=" * 78)
    log_callback(f"Visited folders: {visited_dirs}")
    log_callback(f"Visited files:   {visited_files}")
    log_callback(f"{'Planned' if dry_run else 'Completed'} operations: {actions}")
    log_callback("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="Recursive renamer: folders ALL CAPS, files first-char caps (rest lowercase), remove '(n)', overwrite enabled."
    )
    parser.add_argument("root", help="Root path (Z:\\... or \\\\server\\share\\...)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    args = parser.parse_args()

    rename_tree(Path(args.root), dry_run=not args.apply)


if __name__ == "__main__":
    main()
