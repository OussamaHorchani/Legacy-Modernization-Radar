from pathlib import Path

from schema import Hotspot

from scanners import make_hotspot_id

CONTROLLER_SUFFIX = "Controller.java"
SERVICE_SUFFIX = "Service.java"
SERVICE_IMPL_SUFFIX = "ServiceImpl.java"

PRIORITY = {
    CONTROLLER_SUFFIX: 0,
    SERVICE_SUFFIX: 1,
    SERVICE_IMPL_SUFFIX: 2,
}


def scan_test_coverage(repo_path: Path) -> list[Hotspot]:
    main_root = repo_path / "src" / "main" / "java"
    test_root = repo_path / "src" / "test" / "java"
    if not main_root.exists() or not test_root.exists():
        return []

    missing: list[tuple[int, Hotspot]] = []
    for source_path in sorted(main_root.rglob("*.java")):
        file_name = source_path.name
        suffix = _matching_suffix(file_name)
        if suffix is None:
            continue

        relative_path = source_path.relative_to(main_root)
        if _has_corresponding_tests(relative_path, test_root):
            continue

        class_name = source_path.stem
        test_class_name = f"{class_name}Tests"
        title = f"Missing test class: {test_class_name}"
        if file_name.endswith(CONTROLLER_SUFFIX):
            summary = (
                f"{test_class_name}.java is missing for {class_name}. "
                "The controller does not have a mirrored test class in src/test/java. "
                "That leaves request mapping and validation paths exposed to regression."
            )
        else:
            summary = (
                f"{test_class_name}.java is missing for {class_name}. "
                "The service does not have a matching focused test class in src/test/java. "
                "That increases change risk around service behavior and contract drift."
            )

        hotspot = Hotspot(
            id=make_hotspot_id("quality", title),
            title=title,
            severity="Medium",
            category="quality",
            summary=summary,
            affected_files=[_to_repo_path(source_path, repo_path)],
            recommended_action=(
                f"Add {test_class_name} coverage for the primary execution path and the most "
                "important validation or edge-case behavior."
            ),
        )
        missing.append((PRIORITY[suffix], hotspot))

    missing.sort(key=lambda item: (item[0], item[1].title.lower()))
    return [hotspot for _, hotspot in missing[:3]]


def _matching_suffix(file_name: str) -> str | None:
    if file_name.endswith(CONTROLLER_SUFFIX):
        return CONTROLLER_SUFFIX
    if file_name.endswith(SERVICE_IMPL_SUFFIX):
        return SERVICE_IMPL_SUFFIX
    if file_name.endswith(SERVICE_SUFFIX):
        return SERVICE_SUFFIX
    return None


def _has_corresponding_tests(relative_path: Path, test_root: Path) -> bool:
    expected_path = test_root / relative_path.parent / f"{relative_path.stem}Tests.java"
    if expected_path.exists():
        return True

    stem = relative_path.stem
    if stem.endswith("ServiceImpl"):
        service_prefix = stem.removesuffix("Impl")
    elif stem.endswith("Service"):
        service_prefix = stem
    else:
        return False

    test_dir = test_root / relative_path.parent
    if not test_dir.exists():
        return False

    return any(
        candidate.name.startswith(service_prefix) and candidate.name.endswith("Tests.java")
        for candidate in test_dir.glob("*.java")
    )


def _to_repo_path(path: Path, repo_path: Path) -> str:
    return str(path.relative_to(repo_path))
