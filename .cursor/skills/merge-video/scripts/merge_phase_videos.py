#!/usr/bin/env python3
"""
Merge phase videos for phase-test (two adjacent phases) or section-test (all phases).
Uses ffmpeg concat filter with re-encode so duration and playback are correct
(concat demuxer + -c copy can produce wrong duration / stuck frame when timebases differ).
Requires: ffmpeg on PATH.
"""

import argparse
import os
import subprocess
import sys
from typing import Optional, Tuple


def get_project_root(args) -> str:
    root = os.path.abspath(args.project_root or os.getcwd())
    if not os.path.isdir(root):
        print(f"Error: project root not found: {root}", file=sys.stderr)
        sys.exit(1)
    return root


def phase_video_path(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name, f"{name}.mp4")


def transition_video_path(project_root: str, section: str, from_num: int, to_num: int) -> str:
    """Path to transition clip between phase from_num and to_num (e.g. transition_02_03/transition_02_03.mp4)."""
    trans_name = f"transition_{from_num:02d}_{to_num:02d}"
    return os.path.join(project_root, section, "phases", trans_name, f"{trans_name}.mp4")


def phase_dir(project_root: str, section: str, phase_num: int) -> str:
    name = f"phase{phase_num:02d}"
    return os.path.join(project_root, section, "phases", name)


def phase_readme_path(project_root: str, section: str, phase_num: int) -> str:
    return os.path.join(phase_dir(project_root, section, phase_num), "README.md")


def phase_has_tail_transition(project_root: str, section: str, phase_num: int) -> bool:
    """True if this phase's README records 尾部拼接过渡 (transition already baked onto video)."""
    readme = phase_readme_path(project_root, section, phase_num)
    if not os.path.isfile(readme):
        return False
    try:
        with open(readme, "r", encoding="utf-8") as f:
            return "尾部拼接" in f.read()
    except OSError:
        return False


def write_tail_transition_readme(project_root: str, section: str, phase_num: int, duration_s: float, note: str) -> None:
    """Append or create README in phase folder recording tail transition duration."""
    readme = phase_readme_path(project_root, section, phase_num)
    os.makedirs(os.path.dirname(readme), exist_ok=True)
    line = f"- 尾部拼接过渡 {duration_s:.0f}s（{note}）\n"
    if os.path.isfile(readme):
        with open(readme, "r", encoding="utf-8") as f:
            content = f.read()
        if "尾部拼接" in content:
            return  # already recorded
        with open(readme, "a", encoding="utf-8") as f:
            f.write("\n" + line)
    else:
        with open(readme, "w", encoding="utf-8") as f:
            f.write("# Phase 说明\n\n" + line)
    print(f"Recorded in {readme}: {line.strip()}", file=sys.stderr)


def cross_section_transition_path(project_root: str, section1: str, section2: str) -> str:
    """Path to cross-section transition clip: story_dir/transition_s01_s02/transition_s01_s02.mp4."""
    story_dir = os.path.dirname(os.path.join(project_root, section1))
    return os.path.join(story_dir, "transition_s01_s02", "transition_s01_s02.mp4")


def ensure_phase_transition(
    project_root: str,
    section: str,
    from_num: int,
    to_num: int,
) -> Optional[str]:
    """Return path to phase-to-phase transition video (ffmpeg fade); generate via cross-section-transition script if missing. Same-section only (to_num == from_num + 1)."""
    trans_path = transition_video_path(project_root, section, from_num, to_num)
    if os.path.isfile(trans_path):
        return trans_path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.join(script_dir, "..", "..", "cross-section-transition")
    make_script = os.path.join(skill_root, "scripts", "make_cross_section_transition.py")
    if not os.path.isfile(make_script):
        print(f"Warning: cross-section-transition script not found: {make_script}", file=sys.stderr)
        return None
    try:
        subprocess.run(
            [
                sys.executable,
                make_script,
                "--project-root", os.path.abspath(project_root),
                "--section1", section,
                "--phase1", str(from_num),
                "--section2", section,
                "--phase2", str(to_num),
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        return trans_path if os.path.isfile(trans_path) else None
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def ensure_cross_section_transition(
    project_root: str,
    section1: str,
    phase1: int,
    section2: str,
    phase2: int,
) -> Optional[str]:
    """Return path to cross-section transition video; generate it if missing. Returns None on failure."""
    trans_path = cross_section_transition_path(project_root, section1, section2)
    if os.path.isfile(trans_path):
        return trans_path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.join(script_dir, "..", "..", "cross-section-transition")
    make_script = os.path.join(skill_root, "scripts", "make_cross_section_transition.py")
    if not os.path.isfile(make_script):
        print(f"Warning: cross-section-transition script not found: {make_script}", file=sys.stderr)
        return None
    try:
        subprocess.run(
            [
                sys.executable,
                make_script,
                "--project-root", os.path.abspath(project_root),
                "--section1", section1,
                "--phase1", str(phase1),
                "--section2", section2,
                "--phase2", str(phase2),
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        return trans_path if os.path.isfile(trans_path) else None
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _has_audio(path: str) -> bool:
    """Return True if the file has at least one audio stream."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", path],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.returncode == 0 and (r.stdout or "").strip() != ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _get_duration_seconds(path: str) -> Optional[float]:
    """Return duration of media file in seconds, or None."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "csv=p=0:nokey=1", path,
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0 or not r.stdout:
            return None
        return float(r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return None


def _get_video_size(path: str) -> Optional[Tuple[int, int]]:
    """Return (width, height) of first video stream, or None on failure."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "csv=p=0:nokey=1",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0 or not r.stdout:
            return None
        w, h = r.stdout.strip().split(",")
        return int(w), int(h)
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        return None


def run_ffmpeg_concat(project_root: str, video_paths: list[str], out_path: str) -> bool:
    """Concat using filter + re-encode; scale all to first video size when resolutions differ."""
    if not video_paths:
        print("Error: no video files to merge", file=sys.stderr)
        return False
    for p in video_paths:
        if not os.path.isfile(p):
            print(f"Error: video not found: {p}", file=sys.stderr)
            return False

    n = len(video_paths)
    with_audio = all(_has_audio(p) for p in video_paths)
    target_size = _get_video_size(video_paths[0])
    if not target_size:
        print("Error: could not get video size of first input", file=sys.stderr)
        return False
    w, h = target_size

    cmd = ["ffmpeg", "-y"]
    for p in video_paths:
        cmd.extend(["-i", os.path.abspath(p)])

    # Scale each stream to target size so concat accepts (resolutions may differ between phases)
    scale_filters = "".join(
        f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2[v{i}];"
        for i in range(n)
    )
    if with_audio:
        in_parts = "".join(f"[v{i}][{i}:a]" for i in range(n))
        filter_complex = f"{scale_filters}{in_parts}concat=n={n}:v=1:a=1[outv][outa]"
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            out_path,
        ])
    else:
        in_parts = "".join(f"[v{i}]" for i in range(n))
        filter_complex = f"{scale_filters}{in_parts}concat=n={n}:v=1:a=0[outv]"
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-an", out_path,
        ])

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return os.path.isfile(out_path)
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(f"Error: ffmpeg failed: {e.stderr.decode()}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install ffmpeg and ensure it is on PATH.", file=sys.stderr)
        return False


def append_transition_to_phase(project_root: str, phase_mp4_path: str, trans_path: str) -> bool:
    """Concat phase video + transition and overwrite phase_mp4_path. Returns True on success."""
    d = os.path.dirname(phase_mp4_path)
    tmp = os.path.join(d, ".merge_tail_tmp.mp4")
    try:
        if not run_ffmpeg_concat(project_root, [phase_mp4_path, trans_path], tmp):
            return False
        os.replace(tmp, phase_mp4_path)
        return True
    except OSError:
        if os.path.isfile(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        return False
    finally:
        if os.path.isfile(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def mode_phase_test(
    project_root: str, section: str, from_num: int, to_num: int, with_transition: bool = False
) -> None:
    if to_num != from_num + 1:
        print("Error: phase-test requires two adjacent phases (--to must be --from + 1)", file=sys.stderr)
        sys.exit(1)
    p1 = phase_video_path(project_root, section, from_num)
    p2 = phase_video_path(project_root, section, to_num)
    out_name = f"phase_test_{from_num:02d}_{to_num:02d}.mp4"
    out_dir = os.path.join(project_root, section, "phases")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)

    if with_transition:
        trans_path = ensure_phase_transition(project_root, section, from_num, to_num)
        if trans_path:
            if not append_transition_to_phase(project_root, p1, trans_path):
                sys.exit(1)
            dur = _get_duration_seconds(trans_path)
            write_tail_transition_readme(
                project_root, section, from_num,
                duration_s=dur if dur is not None else 2,
                note=f"至 phase{to_num:02d}",
            )
            if not run_ffmpeg_concat(project_root, [p1, p2], out_path):
                sys.exit(1)
        else:
            print(f"Warning: --with-transition used but transition video not found: {trans_path}", file=sys.stderr)
            if not run_ffmpeg_concat(project_root, [p1, p2], out_path):
                sys.exit(1)
    else:
        if not run_ffmpeg_concat(project_root, [p1, p2], out_path):
            sys.exit(1)
    print(f"Phase-test merged: {out_path}")


def mode_cross_section(
    project_root: str,
    section1: str,
    phase1: int,
    section2: str,
    phase2: int,
    with_transition: bool = False,
) -> None:
    """Merge last phase of section1 with first phase of section2. With transition: append transition directly to first segment (overwrite phase mp4), record in that phase's README, then merge."""
    p1 = phase_video_path(project_root, section1, phase1)
    p2 = phase_video_path(project_root, section2, phase2)
    story_dir = os.path.dirname(os.path.join(project_root, section1))
    os.makedirs(story_dir, exist_ok=True)
    out_name = f"section01_{phase1:02d}_to_section02_{phase2:02d}.mp4"
    out_path = os.path.join(story_dir, out_name)

    if with_transition:
        trans_path = ensure_cross_section_transition(project_root, section1, phase1, section2, phase2)
        if trans_path:
            if not append_transition_to_phase(project_root, p1, trans_path):
                sys.exit(1)
            write_tail_transition_readme(
                project_root, section1, phase1,
                duration_s=1,
                note=f"跨 section 至 {section2} phase{phase2:02d}",
            )
            if not run_ffmpeg_concat(project_root, [p1, p2], out_path):
                sys.exit(1)
        else:
            print("Warning: cross-section transition not available, merging without transition", file=sys.stderr)
            if not run_ffmpeg_concat(project_root, [p1, p2], out_path):
                sys.exit(1)
    else:
        if not run_ffmpeg_concat(project_root, [p1, p2], out_path):
            sys.exit(1)
    print(f"Cross-section merged: {out_path}")


def mode_section_test(project_root: str, section: str) -> None:
    section_dir = os.path.join(project_root, section)
    if not os.path.isdir(section_dir):
        print(f"Error: section directory not found: {section_dir}", file=sys.stderr)
        sys.exit(1)
    phases_dir = os.path.join(section_dir, "phases")
    if not os.path.isdir(phases_dir):
        print(f"Error: phases directory not found: {phases_dir}", file=sys.stderr)
        sys.exit(1)

    video_paths = []
    for n in range(1, 20):
        path = phase_video_path(project_root, section, n)
        if not os.path.isfile(path):
            if n > 1:
                break
            continue
        video_paths.append(path)
        # 若本段尾部已拼过渡（README 有记录），不再插入独立过渡段
        if not phase_has_tail_transition(project_root, section, n):
            trans_path = transition_video_path(project_root, section, n, n + 1)
            if os.path.isfile(trans_path):
                video_paths.append(trans_path)
    if not video_paths:
        print("Error: no phase videos found (phase01/phase01.mp4, ...)", file=sys.stderr)
        sys.exit(1)

    section_basename = os.path.basename(section.rstrip(os.sep))
    out_name = f"{section_basename}_merged.mp4"
    out_path = os.path.join(section_dir, out_name)
    if run_ffmpeg_concat(project_root, video_paths, out_path):
        print(f"Section-test merged ({len(video_paths)} segments): {out_path}")
    else:
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge phase videos (phase-test, section-test, or cross-section).")
    ap.add_argument("--mode", choices=["phase-test", "section-test", "cross-section"], required=True, help="phase-test: two adjacent phases; section-test: all phases in section; cross-section: last phase of section1 + first phase of section2")
    ap.add_argument("--section", type=str, default=None, help="Section name for phase-test/section-test (e.g. section02)")
    ap.add_argument("--from", dest="from_num", type=int, default=None, help="First phase number for phase-test (e.g. 11)")
    ap.add_argument("--to", dest="to_num", type=int, default=None, help="Second phase number (must be --from + 1) for phase-test (e.g. 12)")
    ap.add_argument("--with-transition", action="store_true", help="Phase-test: insert transition_XX_YY.mp4 if exists. Cross-section: insert/generate ≤1s fade transition (tail→first frame).")
    ap.add_argument("--section1", type=str, default=None, help="First section for cross-section (e.g. section01)")
    ap.add_argument("--phase1", type=int, default=None, help="Last phase number of section1 for cross-section (e.g. 8)")
    ap.add_argument("--section2", type=str, default=None, help="Second section for cross-section (e.g. section02)")
    ap.add_argument("--phase2", type=int, default=None, help="First phase number of section2 for cross-section (e.g. 1)")
    ap.add_argument("--project-root", type=str, default=None, help="Project root (default: cwd)")
    args = ap.parse_args()

    project_root = get_project_root(args)

    if args.mode == "phase-test":
        if args.section is None or args.from_num is None or args.to_num is None:
            print("Error: phase-test requires --section, --from and --to", file=sys.stderr)
            sys.exit(1)
        mode_phase_test(
            project_root, args.section, args.from_num, args.to_num,
            with_transition=args.with_transition,
        )
    elif args.mode == "cross-section":
        if not all([args.section1, args.phase1 is not None, args.section2, args.phase2 is not None]):
            print("Error: cross-section requires --section1, --phase1, --section2, --phase2", file=sys.stderr)
            sys.exit(1)
        mode_cross_section(
            project_root, args.section1, args.phase1, args.section2, args.phase2,
            with_transition=args.with_transition,
        )
    else:
        if args.section is None:
            print("Error: section-test requires --section", file=sys.stderr)
            sys.exit(1)
        mode_section_test(project_root, args.section)


if __name__ == "__main__":
    main()
