from hashlib import sha1

from schema import Hotspot

SEVERITY_ORDER = {
    "Critical": 0,
    "High": 1,
    "Medium": 2,
    "Low": 3,
}


def make_hotspot_id(category: str, title: str) -> str:
    digest = sha1(f"{category}:{title}".encode("utf-8")).hexdigest()[:12]
    return f"hotspot-{category}-{digest}"


def sort_hotspots(hotspots: list[Hotspot]) -> list[Hotspot]:
    return sorted(
        hotspots,
        key=lambda hotspot: (
            SEVERITY_ORDER[hotspot.severity],
            hotspot.title.lower(),
            hotspot.id,
        ),
    )
