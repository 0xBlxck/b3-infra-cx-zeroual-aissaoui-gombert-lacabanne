from typing import Any, Dict, List, Tuple
import math
import random

def has_tag(recipe: Dict[str, Any], tag: str) -> bool:
    return "tags" in recipe and any(t.lower() == tag.lower() for t in recipe["tags"])

def fits_time(recipe: Dict[str, Any], max_time: int | None) -> bool:
    if max_time is None:
        return True
    return int(recipe.get("time_min", 9999)) <= max_time

def within_budget_avg(selected: List[Dict[str, Any]], avg_target: float, tolerance: float = 0.2) -> bool:
    if not selected:
        return True
    cur_avg = sum(float(r.get("budget_eur", 0.0)) for r in selected) / len(selected)
    return (avg_target * (1 - tolerance)) <= cur_avg <= (avg_target * (1 + tolerance))

def select_menu(
    recipes: List[Dict[str, Any]],
    days: int = 7,
    min_vege: int = 2,
    min_fish: int = 0,
    max_meat: int | None = None,
    max_time: int | None = None,
    excluded_ingredients: List[str] | None = None,
    no_duplicates: bool = False,
    max_weekly_budget: float | None = None,
    avg_budget: float | None = None,
    tolerance: float = 0.2,
    seed: int | None = 42,
) -> List[Dict[str, Any]]:
    """
    Sélection simple et déterministe (via seed) :
    - Filtre par temps.
    - Tire au sort jusqu'à avoir 'days' recettes.
    - Vérifie min_vege et budget moyen (si fourni). Réessaie quelques fois.
    """
    pool = [r for r in recipes if fits_time(r, max_time) and (
        excluded_ingredients is None or all(
            ing.get("name").lower() not in [e.lower() for e in excluded_ingredients]
            for ing in r.get("ingredients", [])
        )
    )]
    if seed is not None:
        random.seed(seed)
    attempts = 200
    best: List[Dict[str, Any]] = []
    for _ in range(attempts):
        cand: List[Dict[str, Any]] = []
        used_recipes = set()  # Ensemble pour suivre les recettes utilisées

        if no_duplicates and len(pool) >= days:  
            while len(cand) < days:
                #Tant qu'on n'a pas assez de recettes
                available_recipes = [r for r in pool if r["id"] not in used_recipes]
                if not available_recipes:
                    break  # Plus de recettes disponibles
                recipe = random.choice(available_recipes)
                cand.append(recipe)
                used_recipes.add(recipe["id"])
        else:
            # Sélection avec doublons autorisés (comportement par défaut)
            cand = random.choices(pool, k=days) if pool else []

        # Contraintes
        vege_count = sum(1 for r in cand if has_tag(r, "vege"))

        if vege_count < min_vege:
            continue

        fish_count = sum(1 for r in cand if has_tag(r, "poisson"))
        meat_count = sum(1 for r in cand if has_tag(r, "viande"))

        if fish_count < min_fish or (max_meat is not None and meat_count > max_meat):
           continue

        if avg_budget is not None and not within_budget_avg(cand, avg_budget, tolerance): 
            continue
        
        if max_weekly_budget is not None and sum(r.get("budget_eur", 0.0) for r in cand) > max_weekly_budget:

            continue
        best = cand
        break
    if not best:
        # Dernier recours: si aucune combinaison ne marche, on prend ce qu'on peut
        if pool:
            while len(best) < days:
                best.extend(pool)

            best = best[:days]
    return best

def consolidate_shopping_list(menu: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Agrège par (name, unit). Ne gère pas la conversion d’unités (simple au départ).
    """
    agg: Dict[Tuple[str, str], float] = {}
    for r in menu:
        for ing in r.get("ingredients", []):
            key = (ing["name"].strip().lower(), ing.get("unit", "").strip().lower())
            agg[key] = agg.get(key, 0.0) + float(ing.get("qty", 0.0))
    items = [
        {"name": name, "qty": round(qty, 2), "unit": unit}
        for (name, unit), qty in sorted(agg.items())
    ]
    return items

def plan_menu(
    recipes: List[Dict[str, Any]],
    days: int = 7,
    min_vege: int = 2,
    min_fish: int = 0,
    max_meat: int | None = None,
    max_time: int | None = None,
    avg_budget: float | None = None,
    excluded_ingredients: List[str] | None = None,
    no_duplicates: bool = False,
    max_weekly_budget: float | None = None,
    tolerance: float = 0.2,
    seed: int | None = 42,
) -> Dict[str, Any]:
    menu = select_menu(
        recipes, days=days, min_vege=min_vege,
        min_fish=min_fish, max_meat=max_meat,
        max_time=max_time,
        excluded_ingredients=excluded_ingredients,
        no_duplicates=no_duplicates,
        max_weekly_budget=max_weekly_budget,
        avg_budget=avg_budget, tolerance=tolerance, seed=seed
    )
    shopping = consolidate_shopping_list(menu)
    return {"days": days, "menu": menu, "shopping_list": shopping}