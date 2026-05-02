from pathlib import Path
import xml.etree.ElementTree as ET

from schema import Hotspot

from scanners import make_hotspot_id

KNOWN_VULNERABLE = {
    ("commons-collections", "commons-collections", "3.2.1"): {
        "cve": "CVE-2015-7501",
        "cvss": 9.8,
        "summary": "Remote code execution via deserialization gadget chain.",
    },
    ("commons-collections", "commons-collections", "3.2.0"): {
        "cve": "CVE-2015-6420",
        "cvss": 9.8,
        "summary": "Unsafe deserialization path allows remote code execution gadgets.",
    },
    ("log4j", "log4j", "1.2.17"): {
        "cve": "CVE-2021-4104",
        "cvss": 7.5,
        "summary": "JMSAppender can lead to remote code execution in exposed deployments.",
    },
    ("org.apache.logging.log4j", "log4j-core", "2.14.1"): {
        "cve": "CVE-2021-44228",
        "cvss": 10.0,
        "summary": "JNDI lookup handling can trigger remote code execution.",
    },
    ("com.fasterxml.jackson.core", "jackson-databind", "2.9.8"): {
        "cve": "CVE-2019-12384",
        "cvss": 8.1,
        "summary": "Polymorphic deserialization can expose gadget-based remote code execution.",
    },
}


def scan_dependencies(repo_path: Path) -> list[Hotspot]:
    pom_path = repo_path / "pom.xml"
    if not pom_path.exists():
        return []

    try:
        root = ET.parse(pom_path).getroot()
    except ET.ParseError:
        return []

    namespace = {}
    if root.tag.startswith("{"):
        namespace["m"] = root.tag.split("}", 1)[0][1:]
        dependency_path = ".//m:dependency"
        group_path = "m:groupId"
        artifact_path = "m:artifactId"
        version_path = "m:version"
    else:
        dependency_path = ".//dependency"
        group_path = "groupId"
        artifact_path = "artifactId"
        version_path = "version"

    hotspots: list[Hotspot] = []
    for dependency in root.findall(dependency_path, namespace):
        group_id = _text(dependency.find(group_path, namespace))
        artifact_id = _text(dependency.find(artifact_path, namespace))
        version = _text(dependency.find(version_path, namespace))

        if not group_id or not artifact_id or not version:
            continue

        vulnerability = KNOWN_VULNERABLE.get((group_id, artifact_id, version))
        if vulnerability is None:
            continue

        title = f"Critical CVE in {artifact_id}:{version}"
        summary = (
            f"{group_id}:{artifact_id}:{version} matches {vulnerability['cve']} "
            f"(CVSS {vulnerability['cvss']}). {vulnerability['summary']}"
        )
        recommended_action = (
            f"Upgrade or remove {group_id}:{artifact_id}:{version}, confirm {vulnerability['cve']} "
            f"is no longer resolved, and rerun the application smoke tests."
        )
        hotspots.append(
            Hotspot(
                id=make_hotspot_id("runtime", title),
                title=title,
                severity="Critical",
                category="runtime",
                summary=summary,
                affected_files=["pom.xml"],
                recommended_action=recommended_action,
                cve_id=vulnerability["cve"],
                cvss_score=vulnerability["cvss"],
            )
        )

    return hotspots


def _text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    return element.text.strip() or None
