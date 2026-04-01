# target_room
def generate_new_armoire_room_data(armoire_size):
    base_size = [4.792, 0.0, 3.966]
    base_pos = [8.00614275, 0, 16.9070885]
    floor_a = [10.104591, 14.420349000000002]
    floor_b = [0.9970649999999999, 14.420349000000002]
    floor_c = [0.9970649999999999, 19.393828000000006]
    floor_d = [10.104591, 19.393828000000006]
    floor_data = floor_a + floor_b + floor_c + floor_d + floor_a

    y_add = armoire_size[0] - base_size[0]
    x_add = armoire_size[2] - base_size[2]

    floor_a[0] += x_add
    floor_d[0] += x_add

    floor_data = floor_a + floor_b + floor_c + floor_d + floor_a
    # floor_c[1] += y_add
    # floor_d[1] += y_add

    # door_info = {
    #                 "pts": [
    #                     4.888915980419931,
    #                     19.513828,
    #                     5.811124752562124,
    #                     19.513828,
    #                     5.811124752562124,
    #                     19.393828000000003,
    #                     4.888915980419931,
    #                     19.393828000000003
    #                 ],
    #                 "to": "none-56067",
    #                 "width": 0.125951,
    #                 "wall_idx": 2,
    #                 "main_pts": [
    #                     [
    #                         4.888915980419931,
    #                         -19.453828
    #                     ],
    #                     [
    #                         5.811124752562124,
    #                         -19.453828
    #                     ]
    #                 ],
    #                 "link": "Bedroom",
    #                 "height": 0,
    #                 "to_type": "Bedroom"
    #             }
    # door_info["pts"][1] += y_add
    # door_info["pts"][3] += y_add
    # door_info["pts"][5] += y_add
    # door_info["pts"][7] += y_add

    region_work = {"position": [3.035389628503067, 0, 18.7641422806903]}
    region_armoire = {"size": armoire_size.copy(), "position": [base_pos[0] + 0.5 * x_add, base_pos[1],
                                                                base_pos[2] + 0.5 * y_add]}

    return {"floor": floor_data, "door_info": []}, region_armoire, region_work
