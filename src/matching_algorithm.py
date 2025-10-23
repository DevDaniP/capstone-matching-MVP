import itertools

"""
Creates teams of 2-3 people for capstone projects based on compatibility factors.

Compatibility ratings involve each person providing teammate preference ratings on 
a scale from 1-10 and also factors in project preference given a rating of 1-5

This is done deterministically so that the output is repeatable
Uses a greedy algorithm as well for the sake of efficiency

Input Parameters
~~~~~~~~~~~~~~~~~

    people : list[str]
        list of all names

    teammate_prefs : dict[str, dict[str, int]]
        list of teammate preference ratings for associated person (1-10)

    projects : list[str]
        list of all project titles

    project_prefs : dict[str, dict[str, int]]
        list of project preference ratings for associated person (1-5)

    min_size, max_size : int
        team size range
        Note: This is currently hard-coded

    teammate_weight, project_weight : float
        How much each preference type matters for the final score
        Note: This is currently hard-coded
"""

def create_capstone_teams(
        people,
        teammate_prefs,
        projects,
        project_prefs,
        min_size=2,
        max_size=3,
        teammate_weight=0.7,
        project_weight=0.3
):
    print("DEBUG inside function:", type(project_prefs))
    
    def calc_pair_compatibility_score(p1, p2):
        """
        Helper function
        Calculates compatibility scores for pairs specifically
        """
        return ((teammate_prefs.get(p1, {}).get(p2, 5) # Defaults to preference value of 5 if p1 does not have a preference for p2
                + teammate_prefs.get(p2, {}).get(p1, 5)) / 2) 

    def calc_team_compatibility_score(team):
        """
        Helper function
        Calculates teammate compatibility scores between each teammate
        """
        # Ensure that an error is not thrown if a team of only one person exists for some reason
        if len(team) < 2:
            return 5
        pairs = list(itertools.combinations(team, 2))
        return sum(calc_pair_compatibility_score(a, b) for a, b in pairs) / len(pairs) 

    
    def calc_project_compatibility_score(team, project):
        """
        Helper function
        Calculates collective project preference score for a given team
        """
        # Add together preference scores for a particular project for each person on a potential team
        total = sum(project_prefs.get(p, {}).get(project, 3) for p in team) # Default score is 3 if there was no project preference given
        # Average the project preference scores
        return total / len(team)
    
    # Sort everyone deterministically
    people = sorted(people)
    remaining = set(people)
    teams = []

    # Form teams using a greedy but balanced algorithm
    while remaining:
        # Chose the person with the greatest number of potential partners that selected them
        current = max(
            remaining,
            key=lambda p: sum(teammate_prefs.get(p, {}).get(other, 5) for other in remaining if other != p)
        )
        remaining.remove(current)

        # Find the most compatible teammates for this person
        candidates = sorted(
            remaining,
            key=lambda x: teammate_prefs.get(current, {}).get(x, 5)
                        + teammate_prefs.get(x, {}).get(current, 5),
            reverse=True
        )

        # Team size logic
        if len(remaining) == 0:
            team = [current]
        else:
            # Predict if making a max-size team would leave a leftover smaller than min_size
            remainder = (len(remaining) - (max_size - 1)) % max_size

            if remainder < min_size and len(remaining) >= min_size:
                # Form smaller team to balance group sizes later
                team_size = min(min_size - 1, len(candidates))
            else:
                # Safe to form a full-size team
                team_size = min(max_size - 1, len(candidates))

            team = [current] + candidates[:team_size]
            remaining.difference_update(candidates[:team_size])

        teams.append(team)


    teams_sorted = sorted(teams, key=lambda t: calc_team_compatibility_score(t), reverse=True)
    projects_sorted = sorted(projects)

    results = []
    raw_score = []

    # Possible score ranges
    min_possible = teammate_weight * 1 + project_weight * 1
    max_possible = teammate_weight * 10 + project_weight * 5

    def normalize(value):
        """Convert a raw score to 1–100 range, clamped to avoid overflow."""
        norm = ((value - min_possible) / (max_possible - min_possible)) * 99 + 1
        return round(max(1, min(100, norm)), 2)

    for team, project in zip(teams_sorted, projects_sorted):
        t_score = calc_team_compatibility_score(team)
        p_score = calc_project_compatibility_score(team, project)
        combined = teammate_weight * t_score + project_weight * p_score
        raw_score.append(combined)

        team_normalized = normalize(combined)
        results.append((team, project, int(round(team_normalized))))

    # Overall normalized score
    if raw_score:
        avg_raw = sum(raw_score) / len(raw_score)
        normalized_total = normalize(avg_raw)
    else:
        normalized_total = 0

    return results, int(round(normalized_total))
# ~~~ Examples ~~~

"""
# NOTE: These examples do not demonstrate any scalability
people = ["Alice", "Bob", "Charlie", "Dana", "Eli", "Fiona"]
projects = ["Project X", "Project Y", "Project Z"]

teammate_prefs = {
    "Alice": {"Bob": 9, "Charlie": 7, "Dana": 8, "Eli": 6, "Fiona": 4},
    "Bob": {"Alice": 10, "Charlie": 5, "Dana": 6, "Eli": 5, "Fiona": 8},
    "Charlie": {"Alice": 7, "Bob": 6, "Dana": 9, "Eli": 5, "Fiona": 5},
    "Dana": {"Alice": 8, "Bob": 6, "Charlie": 10, "Eli": 5, "Fiona": 7},
    "Eli": {"Alice": 5, "Bob": 4, "Charlie": 8, "Dana": 6, "Fiona": 10},
    "Fiona": {"Alice": 4, "Bob": 8, "Charlie": 6, "Dana": 6, "Eli": 9},
}
project_prefs = {
    "Alice": {"Project X": 4, "Project Y": 5, "Project Z": 3},
    "Bob": {"Project X": 5, "Project Y": 4, "Project Z": 3},
    "Charlie": {"Project X": 3, "Project Y": 5, "Project Z": 4},
    "Dana": {"Project X": 2, "Project Y": 5, "Project Z": 3},
    "Eli": {"Project X": 3, "Project Y": 4, "Project Z": 5},
    "Fiona": {"Project X": 5, "Project Y": 4, "Project Z": 3},
}

results, total = create_capstone_teams(
    people, teammate_prefs, projects, project_prefs
)

print("\n=== Normalized Team Results (1–100) ===")
for team, project, score in results:
    print(f"Team: {team} → {project} (Score: {score}/100)")

print("\nOverall Total Score:", total, "/100")
"""