from hardness_map import HardnessMap

hardness_map = HardnessMap("CCT_PM_0.1Cs-1.csv")
hardness_map.get_data()
hardness_map.create_hardness_map()
hardness_map.save_to_excel()
hardness_map.display_hardness_map()

# print(hardness_map.hardness_map)

