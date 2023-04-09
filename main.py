from hardness_map import HardnessMap

hardness_map = HardnessMap("CCT_PM_0.1Cs-1.csv")
hardness_map.get_data()
hardness_map.get_hardness_map()

print(hardness_map.hardness_map)

