# tests/test_matching_algorithm.py
import os
import sys

# Make 'src' importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from matching_algorithm import create_capstone_teams


def test_deterministic_output():
    people = ["Alice", "Bob", "Cara", "Dan", "Eve"]
    projects = ["Zeta", "Alpha", "Beta"]  # intentionally unsorted
    teammate_prefs = {
        "Alice": {"Bob": 10, "Cara": 6, "Dan": 6, "Eve": 5},
        "Bob":   {"Alice": 10, "Cara": 5, "Dan": 6, "Eve": 5},
        "Cara":  {"Dan": 9, "Alice": 6, "Bob": 5, "Eve": 5},
        "Dan":   {"Cara": 9, "Alice": 6, "Bob": 5, "Eve": 5},
        "Eve":   {},  # neutral/defaults
    }
    project_prefs = {p: {} for p in people}  # all defaults (3)

    r1, total1 = create_capstone_teams(people, teammate_prefs, projects, project_prefs)
    r2, total2 = create_capstone_teams(people, teammate_prefs, projects, project_prefs)

    assert r1 == r2
    assert total1 == total2


def test_team_sizes_and_no_solo_for_five():
    people = ["Alice", "Bob", "Cara", "Dan", "Eve"]
    projects = ["A", "B", "C"]
    teammate_prefs = {p: {} for p in people}  # defaults (5)
    project_prefs = {p: {} for p in people}

    results, total = create_capstone_teams(people, teammate_prefs, projects, project_prefs)
    teams = [team for team, _, _ in results]

    # For 5 people with min=2, max=3 we expect a 3+2 split
    sizes = sorted(len(t) for t in teams)
    assert sizes == [2, 3]
    # Score bounds (normalized 1..100)
    assert 1 <= total <= 100
    for _, _, s in results:
        assert 1 <= s <= 100


def test_projects_assigned_in_alpha_order_to_best_teams():
    # Make one clearly better pair (Alice+Bob) than the others
    people = ["Alice", "Bob", "Cara", "Dan", "Eve", "Fay"]
    projects = ["Zebra", "Alpha"]  # sorted -> ["Alpha", "Zebra"]
    teammate_prefs = {
        "Alice": {"Bob": 10},
        "Bob":   {"Alice": 10},
        "Cara":  {"Dan": 7},
        "Dan":   {"Cara": 7},
        "Eve":   {},
        "Fay":   {},
    }
    project_prefs = {p: {} for p in people}

    results, _ = create_capstone_teams(people, teammate_prefs, projects, project_prefs)

    # Teams are sorted by team compatibility score (desc); projects sorted alpha
    # So the top team should get "Alpha"
    top_team, top_project, _ = results[0]
    assert top_project == "Alpha"
    # And the top team should contain Alice & Bob (the strongest pair)
    assert ("Alice" in top_team) and ("Bob" in top_team)


def test_defaults_drive_expected_score_for_blank_prefs():
    # Two people, one project, no prefs -> teammate avg=5, project avg=3
    # combined = 0.7*5 + 0.3*3 = 4.4 -> normalized ≈ 46
    people = ["A", "B"]
    projects = ["OnlyProj"]
    teammate_prefs = {"A": {}, "B": {}}
    project_prefs = {"A": {}, "B": {}}

    results, total = create_capstone_teams(people, teammate_prefs, projects, project_prefs)
    assert len(results) == 1
    team, proj, score = results[0]
    assert set(team) == {"A", "B"}
    assert proj == "OnlyProj"
    assert score == 46
    assert total == 46


def test_handles_empty_inputs_gracefully():
    results, total = create_capstone_teams([], {}, [], {})
    assert results == []
    assert total == 0


def test_team_partition_for_seven_people_is_3_2_2():
    people = ["A", "B", "C", "D", "E", "F", "G"]
    projects = ["P1", "P2", "P3"]
    t = {p: {} for p in people}
    pp = {p: {} for p in people}
    res, _ = create_capstone_teams(people, t, projects, pp)
    sizes = sorted(len(team) for team, _, _ in res)
    assert sizes == [2, 2, 3]


def test_more_teams_than_projects_truncates_output_to_projects():
    # 6 people -> 3 teams (3,3) after sorting, but only 2 projects -> 2 result rows
    people = ["A", "B", "C", "D", "E", "F"]
    projects = ["Alpha", "Zebra"]  # 2 projects only
    t = {p: {} for p in people}
    pp = {p: {} for p in people}
    res, _ = create_capstone_teams(people, t, projects, pp)
    assert len(res) == len(projects)  # zip truncation behavior is explicit
