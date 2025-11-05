import json, subprocess, sys

def test_cli_smoke(tmp_path):
    recipes_path = tmp_path / "recipes.json"
    data = [
        {"id":"x","name":"X","tags":["vege"],"time_min":10,"budget_eur":2.0,
         "ingredients":[{"name":"pâtes","qty":100,"unit":"g"}]}
    ]
    with open(recipes_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    out_path = tmp_path / "out.json"
    cmd = [sys.executable, "-m", "mealmaker.cli", "--recipes", str(recipes_path), "--days", "1", "--output", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_path.exists()
    out = json.loads(out_path.read_text(encoding="utf-8"))

    assert out["days"] == 1
    assert len(out["menu"]) == 1

def test_cli_fish_meat(tmp_path):
    recipes_path = tmp_path / "recipes.json"
    data = [
        {"id": "x", "name": "X", "tags": ["vege"], "time_min": 10, "budget_eur": 2.0,
         "ingredients": [{"name": "pâtes", "qty": 100, "unit": "g"}]},
        {"id": "y", "name": "Y", "tags": ["poisson"], "time_min": 10, "budget_eur": 2.0,
         "ingredients": [{"name": "thon", "qty": 100, "unit": "g"}]},
        {"id": "z", "name": "Z", "tags": ["viande"], "time_min": 10, "budget_eur": 2.0,
         "ingredients": [{"name": "boeuf", "qty": 100, "unit": "g"}]},
    ]
    with open(recipes_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    out_path = tmp_path / "out.json"
    cmd = [sys.executable, "-m", "mealmaker.cli",
           "--recipes", str(recipes_path), "--days", "3",
           "--min-fish", "1", "--max-meat", "1",
           "--output", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_path.exists()
    out = json.loads(out_path.read_text(encoding="utf-8"))
    assert out["days"] == 3
    assert sum(1 for r in out["menu"] if "poisson" in r["tags"]) >= 1
    assert sum(1 for r in out["menu"] if "viande" in r["tags"]) <= 1

def test_cli_exclude_ingredients(tmp_path):
    recipes_path = tmp_path / "recipes.json"
    data = [
        {"id": "x", "name": "X", "tags": ["vege"], "time_min": 10, "budget_eur": 2.0,
         "ingredients": [{"name": "pâtes", "qty": 100, "unit": "g"}]},
        {"id": "y", "name": "Y", "tags": ["poisson"], "time_min": 10, "budget_eur": 2.0,
         "ingredients": [{"name": "thon", "qty": 100, "unit": "g"}]},
    ]
    with open(recipes_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    out_path = tmp_path / "out.json"
    cmd = [sys.executable, "-m", "mealmaker.cli",
           "--recipes", str(recipes_path), "--days", "2",
           "--exclude-ingredients", "pâtes",
           "--output", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_path.exists()
    out = json.loads(out_path.read_text(encoding="utf-8"))
    assert all("pâtes" not in r["ingredients"][0]["name"] for r in out["menu"])

def test_cli_no_duplicates(tmp_path):
    recipes_path = tmp_path / "recipes.json"
    data = [
        {"id": "r1", "name": "A", "ingredients": []},
        {"id": "r2", "name": "B", "ingredients": []},
        {"id": "r3", "name": "C", "ingredients": []},
    ]
    with open(recipes_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    out_path = tmp_path / "out.json"
    cmd = [sys.executable, "-m", "mealmaker.cli",
           "--recipes", str(recipes_path), "--days", "3",
           "--no-duplicates",
           "--output", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_path.exists()
    out = json.loads(out_path.read_text(encoding="utf-8"))
    ids = [r["id"] for r in out["menu"]]
    assert len(ids) == 3
    assert len(ids) == len(set(ids))

def test_cli_max_weekly_budget(tmp_path):
    recipes_path = tmp_path / "recipes.json"
    data = [
        {"id": "r1", "name": "A", "budget_eur": 2.0, "ingredients": []},
        {"id": "r2", "name": "B", "budget_eur": 2.0, "ingredients": []},
        {"id": "r3", "name": "C", "budget_eur": 10.0, "ingredients": []},
    ]
    with open(recipes_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    out_path = tmp_path / "out.json"
    cmd = [sys.executable, "-m", "mealmaker.cli",
           "--recipes", str(recipes_path), "--days", "2",
           "--max-weekly-budget", "5.0",
           "--output", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_path.exists()
    out = json.loads(out_path.read_text(encoding="utf-8"))
    assert sum(r.get("budget_eur", 0.0) for r in out["menu"]) <= 5.0

def test_cli_max_weekly_budget(tmp_path):
    recipes_path = tmp_path / "recipes.json"
    data = [
        {"id": "r1", "name": "A", "budget_eur": 2.0, "ingredients": []},
        {"id": "r2", "name": "B", "budget_eur": 2.0, "ingredients": []},
        {"id": "r3", "name": "C", "budget_eur": 10.0, "ingredients": []},
    ]
    with open(recipes_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    out_path = tmp_path / "out.json"
    cmd = [sys.executable, "-m", "mealmaker.cli",
           "--recipes", str(recipes_path), "--days", "2",
           "--max-weekly-budget", "5.0",
           "--output", str(out_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert out_path.exists()
    out = json.loads(out_path.read_text(encoding="utf-8"))
    assert sum(r.get("budget_eur", 0.0) for r in out["menu"]) <= 5.0