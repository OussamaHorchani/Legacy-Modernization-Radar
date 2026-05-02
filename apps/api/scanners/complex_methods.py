from pathlib import Path
import re

from schema import Hotspot

from scanners import make_hotspot_id

METHOD_PATTERN = re.compile(
    r"^\s*(?:public|private|protected|@\w+\s+)*\s*(?:static\s+)?"
    r"(?:[\w<>,\[\]\s]+)\s+(\w+)\s*\([^)]*\)\s*\{"
)


def scan_complex_methods(repo_path: Path) -> list[Hotspot]:
    main_root = repo_path / "src" / "main" / "java"
    test_root = repo_path / "src" / "test" / "java"
    if not main_root.exists():
        return []

    test_method_names = _collect_test_method_names(test_root)
    hotspots: list[Hotspot] = []

    for source_path in sorted(main_root.rglob("*Service*.java")):
        methods = _extract_methods(source_path)
        for method_name, body in methods:
            branch_count = _count_branches(body)
            if branch_count < 5:
                continue
            if _has_similar_test_method(method_name, test_method_names):
                continue

            title = f"Untested complex method: {method_name}"
            hotspots.append(
                Hotspot(
                    id=make_hotspot_id("architecture", title),
                    title=title,
                    severity="High",
                    category="architecture",
                    summary=(
                        f"{method_name} contains {branch_count} branch points in a service-class "
                        "method body, but no similarly named test method was found under src/test/java."
                    ),
                    affected_files=[_to_repo_path(source_path, repo_path)],
                    recommended_action=(
                        f"Add focused coverage for {method_name} before refactoring the method, "
                        "then consider extracting smaller units to reduce branch complexity."
                    ),
                )
            )

    return hotspots


def _collect_test_method_names(test_root: Path) -> set[str]:
    if not test_root.exists():
        return set()

    method_names: set[str] = set()
    for test_file in test_root.rglob("*.java"):
        for method_name, _ in _extract_methods(test_file):
            method_names.add(method_name)
    return method_names


def _extract_methods(path: Path) -> list[tuple[str, str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []

    methods: list[tuple[str, str]] = []
    line_index = 0
    while line_index < len(lines):
        line = lines[line_index]
        match = METHOD_PATTERN.match(line)
        if match is None:
            line_index += 1
            continue

        method_name = match.group(1)
        brace_depth = line.count("{") - line.count("}")
        body_lines = [line]
        line_index += 1

        while line_index < len(lines) and brace_depth > 0:
            body_line = lines[line_index]
            body_lines.append(body_line)
            brace_depth += body_line.count("{") - body_line.count("}")
            line_index += 1

        methods.append((method_name, "\n".join(body_lines)))

    return methods


def _count_branches(method_body: str) -> int:
    else_if_count = len(re.findall(r"\belse\s+if\s*\(", method_body))
    if_count = len(re.findall(r"\bif\s*\(", method_body))
    for_count = len(re.findall(r"\bfor\s*\(", method_body))
    while_count = len(re.findall(r"\bwhile\s*\(", method_body))
    return (if_count - else_if_count) + else_if_count + for_count + while_count


def _has_similar_test_method(method_name: str, test_method_names: set[str]) -> bool:
    normalized_method = _normalize(method_name)
    for test_name in test_method_names:
        normalized_test = _normalize(test_name)
        if normalized_method in normalized_test or normalized_test in normalized_method:
            return True
    return False


def _normalize(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _to_repo_path(path: Path, repo_path: Path) -> str:
    return str(path.relative_to(repo_path))
