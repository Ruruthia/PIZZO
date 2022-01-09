import json

from z3 import *

DEBUG = True


class Diet:

    def __init__(self, diet):

        self._diet = diet
        self._solver = Solver()
        self._solvable = None
        self._variables = {
            f'{ingredient["nazwa"]}_{day}_{meal}': Int(f'{ingredient["nazwa"]}_{day}_{meal}')
            for ingredient in self._diet["składniki"] for day in range(7) for meal in range(5)
        }

    def _ingredients_not_negative(self):
        for _, ingredient in self._variables.items():
            self._solver.add(ingredient >= 0)

    def _add_meal_not_empty(self):
        for day in range(7):
            for meal in range(5):
                self._solver.add(
                    Sum([self._variables[f'{ingredient["nazwa"]}_{day}_{meal}'] for ingredient in
                         self._diet["składniki"]]) > 0)

    def _add_conflicts(self):
        for day in range(7):
            for meal in range(5):
                for conflict in self._diet["konflikty"]:
                    self._solver.add(Or(self._variables[f'{conflict["nazwa1"]}_{day}_{meal}'] == 0,
                                        self._variables[f'{conflict["nazwa2"]}_{day}_{meal}'] == 0
                                        ))

    def _add_daily_goals(self):
        for day in range(7):
            for nutrient in self._diet["cel"]:
                nutrient_values = []
                for ingredient in self._diet["składniki"]:
                    nutrient_values.append(
                        ToReal(Sum([self._variables[f'{ingredient["nazwa"]}_{day}_{meal}'] for meal in range(5)]))
                        * ingredient[nutrient]
                    )
                self._solver.add(Sum(nutrient_values) >= self._diet["cel"][nutrient]["min"])
                self._solver.add(Sum(nutrient_values) <= self._diet["cel"][nutrient]["max"])

    def _add_weekly_goals(self):
        for nutrient in self._diet["cel_tygodniowy"]:
            nutrient_values = []
            for ingredient in self._diet["składniki"]:
                nutrient_values.append(
                    ToReal(Sum([self._variables[f'{ingredient["nazwa"]}_{day}_{meal}'] for meal in range(5) for day in
                                range(7)]))
                    * ingredient[nutrient])
            self._solver.add(Sum(nutrient_values) >= self._diet["cel_tygodniowy"][nutrient]["min"])
            self._solver.add(Sum(nutrient_values) <= self._diet["cel_tygodniowy"][nutrient]["max"])

    def solve(self):
        self._ingredients_not_negative()
        self._add_meal_not_empty()
        self._add_conflicts()
        self._add_daily_goals()
        self._add_weekly_goals()
        self._solvable = self._solver.check() == sat
        print(self._solvable)

    def format_output(self):
        assert self._solvable is not None
        if self._solvable:
            output = [[[] for _ in range(5)] for _ in range(7)]
            model = self._solver.model()
            for var in model:
                day, meal = int(var.name()[-3]), int(var.name()[-1])
                output[day][meal].extend([str(var)[:-4]] * int(str(model[var])))
            for day_idx, day_name in zip(range(7),
                                         ["poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota",
                                          "niedziela"]):
                print(f'[{day_name}]')
                for meal_idx, meal_name in zip(range(5),
                                               ["śniadanie", "lunch", "obiad", "podwieczorek", "kolacja"]):
                    print(f'{meal_name}: {", ".join(output[day_idx][meal_idx])}')
                if DEBUG:
                    for nutrient in self._diet["cel"]:
                        nutrient_dict = {ingredient["nazwa"]: ingredient[nutrient] for ingredient in
                                         self._diet["składniki"]}
                        value = 0.0
                        for meals in output[day_idx]:
                            for ingredient in meals:
                                value += nutrient_dict[ingredient]
                        print(f'Daily {nutrient} : {value}')
            if DEBUG:
                for nutrient in self._diet["cel"]:
                    nutrient_dict = {ingredient["nazwa"]: ingredient[nutrient] for ingredient in
                                     self._diet["składniki"]}
                    value = 0.0
                    for day in output:
                        for meals in day:
                            for ingredient in meals:
                                value += nutrient_dict[ingredient]
                    print(f'Weekly {nutrient} : {value}')

        else:
            print("Nie można wygenerować diety.")


def main():
    # to use:
    # 1. python main.py
    # 2. paste the input
    # 3. ctrl+d to end input
    # OR
    # cat test | python main.py
    dieta = Diet(json.load(sys.stdin))
    dieta.solve()
    dieta.format_output()


main()
