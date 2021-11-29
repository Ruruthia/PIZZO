import json
import sys

# testing: echo path_to_test_file | python main.py | clasp -n 0


def parse_install_instance(install_instance):
    # parsed instance has packet names converted into indexes
    packet_to_idx = {}
    for i in range(len(install_instance["pakiety"])):
        packet_to_idx[install_instance["pakiety"][i]] = i + 1
    parsed_install_instance = {
        "packets": packet_to_idx.values(),
        "collisions": [
            (packet_to_idx[collision["pakiet"]],
             packet_to_idx[collision["koliduje_z"]])
            for collision in install_instance["kolizje"]
        ],
        "requirements": [
            (packet_to_idx[requirement["pakiet"]],
             [packet_to_idx[packet] for packet in requirement["wymaga"]])
            for requirement in install_instance["wymagania"]
        ],
        "to_install": [packet_to_idx[i] for i in install_instance["instalowane"]]
    }
    return parsed_install_instance


class Install:
    def __init__(self, install_instance):
        parsed_install_instance = parse_install_instance(install_instance)
        self._packets = parsed_install_instance["packets"]
        self._collisions = parsed_install_instance["collisions"]
        self._requirements = parsed_install_instance["requirements"]
        self._to_install = parsed_install_instance["to_install"]

    def to_sat(self):
        print(
            f'p cnf {len(self._packets)} {len(self._to_install) + len(self._collisions) + len(self._requirements)}')
        for p in self._to_install:
            # clauses representing packets required to be installed
            print(f'{p} 0')
        for p1, p2 in self._collisions:
            # clauses representing collisions
            # when packets collide then we need:
            # (p1 -> not p2) and (p2 -> not p1) ≡ not p1 or not p2
            print(f'{-p1} {-p2} 0')
        for p, ps in self._requirements:
            # clauses representing requirements
            # when packet p requires packets ps1, ps2, ... then we need:
            # p -> (ps1 or ps2 or ...) ≡ not p or ps1 or ps2 ...
            print(f'{-p} {" ".join([str(p) for p in ps])} 0')


def main():
    path = sys.stdin.readline().strip()
    with open(path, "r") as f:
        install_instance = Install(json.load(f))
    install_instance.to_sat()


main()
