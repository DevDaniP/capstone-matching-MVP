# tests/test_main.py
import os
import sys
import types
import pandas as pd
import builtins

# Make 'src' importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import main  # your src/main.py file


def test_get_google_sheets_service_returns_none_when_no_credentials(monkeypatch):
    # Patch builtins.open to raise FileNotFoundError
    def fake_open(*args, **kwargs):
        raise FileNotFoundError()
    monkeypatch.setattr(builtins, "open", fake_open)

    svc = main.get_google_sheets_service()
    assert svc is None


def test_read_spreadsheet_data_returns_none_when_no_service(monkeypatch):
    monkeypatch.setattr(main, "get_google_sheets_service", lambda: None)
    out = main.read_spreadsheet_data("sheet_id", "A1:B2")
    assert out is None


def test_read_spreadsheet_data_success(monkeypatch):
    # Fake the chained client: service.spreadsheets().values().get(...).execute()
    class FakeGet:
        def execute(self):
            return {"values": [["H"], ["I"]]}

    class FakeValues:
        def get(self, **kwargs):
            return FakeGet()

    class FakeSpreadsheets:
        def values(self):
            return FakeValues()

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    monkeypatch.setattr(main, "get_google_sheets_service", lambda: FakeService())
    values = main.read_spreadsheet_data("sheet_id", "A1:B2")
    assert values == [["H"], ["I"]]


def test_transform_data_for_algorithm_basic():
    # Build a minimal DataFrame that matches the column patterns in your code
    df = pd.DataFrame(
        [
            {
                "Please Enter Your Name.": "Alice",
                "Rank the projects [Proj A]": "1",
                "Rank the projects [Proj B]": "3",
                "Rank the people you'd like to work with [Person 1]": "Bob",
                "Rank the people you'd like to work with [Person 2]": "Charlie",
                "Choose three people you don't want [1]": "Eve",      # ignored (not in people)
                "Choose three people you don't want [2]": "Bob",      # sets Bob to 1
            },
            {
                "Please Enter Your Name.": "Bob",
                "Rank the projects [Proj A]": "2",
                "Rank the projects [Proj B]": "1",
                "Rank the people you'd like to work with [Person 1]": "Alice",
                "Rank the people you'd like to work with [Person 2]": pd.NA,
                "Choose three people you don't want [1]": pd.NA,
                "Choose three people you don't want [2]": pd.NA,
            },
            {
                "Please Enter Your Name.": "Charlie",
                "Rank the projects [Proj A]": "5",
                "Rank the projects [Proj B]": "4",
                "Rank the people you'd like to work with [Person 1]": "Alice",
                "Rank the people you'd like to work with [Person 2]": "Bob",
                "Choose three people you don't want [1]": pd.NA,
                "Choose three people you don't want [2]": pd.NA,
            },
        ]
    )

    people, teammate_prefs, projects, project_prefs = main.transform_data_for_algorithm(df)

    # People parsed in order
    assert people == ["Alice", "Bob", "Charlie"]

    # Projects parsed from bracket names in order of columns
    assert projects == ["Proj A", "Proj B"]

    # Project prefs:  ranking r -> score (6 - r)
    assert project_prefs["Alice"] == {"Proj A": 5, "Proj B": 3}
    assert project_prefs["Bob"] == {"Proj A": 4, "Proj B": 5}
    assert project_prefs["Charlie"] == {"Proj A": 1, "Proj B": 2}

    # Teammate prefs:
    # Ranked: rank N -> score max(1, 11 - N). Avoided people forced to 1.
    # Alice ranked Bob as Person 1 (score 10) BUT also avoided Bob -> should end up 1
    # Alice ranked Charlie as Person 2 -> 9
    assert teammate_prefs["Alice"]["Bob"] == 1
    assert teammate_prefs["Alice"]["Charlie"] == 9

    # Bob ranked Alice as Person 1 -> 10
    assert teammate_prefs["Bob"]["Alice"] == 10
    # No entry for Charlie from Bob (not ranked/avoided)
    assert "Charlie" not in teammate_prefs["Bob"]

    # Charlie ranked Alice (10) and Bob (9)
    assert teammate_prefs["Charlie"]["Alice"] == 10
    assert teammate_prefs["Charlie"]["Bob"] == 9


def test_write_to_spreadsheet_success(monkeypatch):
    class FakeExecute:
        def execute(self):
            return {"updatedCells": 7}

    class FakeUpdate:
        def __init__(self, **kwargs):
            pass
        def execute(self):
            return {"updatedCells": 3}

    class FakeValues:
        def update(self, **kwargs):
            return FakeUpdate(**kwargs)

    class FakeSpreadsheets:
        def values(self):
            return FakeValues()

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    monkeypatch.setattr(main, "get_google_sheets_service", lambda: FakeService())
    ok = main.write_to_spreadsheet("sheet_id", "A1", [["x"]])
    assert ok is True


def test_write_to_spreadsheet_handles_http_error(monkeypatch):
    # Replace main.HttpError with a simple stand-in so we don't need the Google lib
    class DummyHttpError(Exception):
        pass

    class FakeValues:
        def update(self, **kwargs):
            def _raise():
                raise DummyHttpError("boom")
            return types.SimpleNamespace(execute=_raise)

    class FakeSpreadsheets:
        def values(self):
            return FakeValues()

    class FakeService:
        def spreadsheets(self):
            return FakeSpreadsheets()

    monkeypatch.setattr(main, "HttpError", DummyHttpError)
    monkeypatch.setattr(main, "get_google_sheets_service", lambda: FakeService())

    ok = main.write_to_spreadsheet("sheet_id", "A1", [["x"]])
    assert ok is False
