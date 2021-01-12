# yadmark_runner.py
class YadmarkRunner(ParentRunner):
    pass


# ============
# obs_card.py
obs = {
    0: {"obs_list": ["F2light"], "kins": default_kins},
    1: {"obs_list": ["F2light", "F2charm"], "kins": default_kins},
}

default_kins = [{"x": 0.1, "Q2": 90}]
default_card = {"interpolation_xgrid": [0.1, 1]}


def built_obs(o, base=default_card):
    cards = []
    card = copy.deepcopy(base)
    for obs in o["obs_list"]:
        card[obs] = o["kins"]
    cards.append(card)


# =================
# apfel.py
class BenchmarkPlain(YadmarkRunner):
    theories = {}

    pdfs = ["CT14llo_NF6"]

    def benchmark_lo(self):
        return self.run(theory_update={"PTO": 0}, observables=obs_card.obs_lo)

    def benchmark_nlo(self):
        return self.run(theory_update={"PTO": 1})


class BenchmarkTMC(YadmarkRunner):
    theories = {
        "TMC": [
            1,
        ],
    }

    pdfs = ["CT14llo_NF6"]

    def observables():
        return {}

    def benchmark_lo():
        def obs():
            o = self.default_obs()
            o["F2light"] = [{"x": 0.1, "Q2": 90}]
            return [o]

        return self.run(theory_update={"PTO": 0}, observables=obs())
