"""Pruebas para el módulo de ubicaciones."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.locations import LOCATIONS, ROUTES, get_location, get_all_unique_locations


def test_locations_exist():
    """Verifica que todas las ubicaciones estén definidas."""
    assert len(LOCATIONS) == 7
    assert "Msida" in LOCATIONS
    assert "Marsaskala" in LOCATIONS


def test_routes_exist():
    """Verifica que todas las rutas estén configuradas."""
    assert len(ROUTES) == 6


def test_get_location():
    """Verifica que se puede obtener una ubicación por nombre."""
    loc = get_location("Msida")
    assert loc.name == "Msida"
    assert loc.latitude == 35.8970
    assert loc.longitude == 14.4890


def test_get_all_unique_locations():
    """Verifica que se retornan todas las ubicaciones únicas."""
    unique = get_all_unique_locations()
    assert len(unique) >= 6


def test_invalid_location():
    """Verifica que se lanza error para ubicación inexistente."""
    try:
        get_location("NonExistent")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_locations_exist()
    test_routes_exist()
    test_get_location()
    test_get_all_unique_locations()
    test_invalid_location()
    print("✓ All location tests passed")
