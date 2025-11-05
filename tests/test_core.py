from mealmaker.core import has_tag, fits_time, within_budget_avg, select_menu, consolidate_shopping_list

def sample_recipes():
    return [
        {"id": "r1", "name": "A", "tags": ["vege"], "time_min": 15, "budget_eur": 2.0,
         "ingredients": [{"name": "pâtes", "qty": 200, "unit": "g"}]},
        {"id": "r2", "name": "B", "tags": ["viande"], "time_min": 30, "budget_eur": 3.0,
         "ingredients": [{"name": "riz", "qty": 150, "unit": "g"}]},
        {"id": "r3", "name": "C", "tags": ["vege"], "time_min": 10, "budget_eur": 1.5,
         "ingredients": [{"name": "pâtes", "qty": 100, "unit": "g"}]},
    ]

def test_is_vege():
    r = {"tags": ["vege"]}
    assert has_tag(r, "vege") is True
    assert has_tag({"tags": ["viande"]}, "vege") is False

def test_fits_time():
    assert fits_time({"time_min": 20}, 30) is True
    assert fits_time({"time_min": 40}, 30) is False
    assert fits_time({"time_min": 40}, None) is True

def test_within_budget_avg():
    recs = [{"budget_eur": 2.0}, {"budget_eur": 4.0}]
    assert within_budget_avg(recs, 3.0, 0.2) is True
    assert within_budget_avg(recs, 2.0, 0.1) is False

def test_select_menu_constraints():
    recs = sample_recipes()
    menu = select_menu(recs, days=3, min_vege=2, max_time=30, avg_budget=2.0, tolerance=0.5, seed=1)
    assert len(menu) == 3
    assert sum(1 for r in menu if has_tag(r, "vege")) >= 2
    # Budget moyen dans la tolérance si avg_budget fourni
    if menu:
        avg = sum(r["budget_eur"] for r in menu) / len(menu)
        assert (2.0 * 0.5) <= avg <= (2.0 * 1.5)

def test_select_menu_fish_meat_constraints():
    recs = sample_recipes() + [
        {"id": "r4", "name": "D", "tags": ["poisson"], "time_min": 20, "budget_eur": 4.0,
         "ingredients": [{"name": "saumon", "qty": 150, "unit": "g"}]},
        {"id": "r5", "name": "E", "tags": ["viande"], "time_min": 25, "budget_eur": 5.0,
         "ingredients": [{"name": "boeuf", "qty": 200, "unit": "g"}]},
    ]
    menu = select_menu(recs, days=5, min_vege=1, min_fish=1, max_meat=1, max_time=30, seed=1)
    assert len(menu) == 5
    assert sum(1 for r in menu if has_tag(r, "vege")) >= 1
    assert sum(1 for r in menu if has_tag(r, "poisson")) >= 1
    assert sum(1 for r in menu if has_tag(r, "viande")) <= 1

def test_select_menu_exclude_ingredients():
    recs = sample_recipes()
    menu = select_menu(recs, days=3, excluded_ingredients=["pâtes"], seed=1)
    assert len(menu) == 3
    for r in menu:
        for ing in r.get("ingredients", []):
            assert ing["name"] != "pâtes"

def test_select_menu_no_duplicates():
    recs = sample_recipes() * 3  # Assurer qu'il y a assez de recettes pour piocher sans doublons
    menu = select_menu(recs, days=3, no_duplicates=True, seed=1)
    assert len(menu) == 3
    # Vérifier que les IDs des recettes sont uniques
    ids = [r["id"] for r in menu]
    assert len(ids) == len(set(ids))

def test_select_menu_max_weekly_budget():
    recs = sample_recipes()
    menu = select_menu(recs, days=3, max_weekly_budget=5.0, seed=1)
    assert len(menu) == 3
    assert sum(r.get("budget_eur", 0.0) for r in menu) <= 5.0

def test_consolidate_shopping_list():
    recs = sample_recipes()
    items = consolidate_shopping_list(recs[:2])  # A+B
    # pâtes 200g + riz 150g
    lookup = { (i["name"], i["unit"]): i["qty"] for i in items }
    assert lookup.get(("pâtes", "g")) == 200
    assert lookup.get(("riz", "g")) == 150