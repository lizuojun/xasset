from HouseSearch.util import get_http_data_from_url


def get_furniture_rotation_check(jid):
    url = "http://calcifer-api.alibaba-inc.com/api/v1/models/" + jid + "/algorithm?keys=main_direction"
    data = get_http_data_from_url(url)
    rot_type = 0
    if data:
        if jid in data and 'main_direction' in data[jid]:
            data = data[jid]['main_direction']
            if len(data) > 0 and ',' in data:
                data = list(map(float, data.split(',')))
                if data[0] < -0.9:
                    rot_type = 1
                elif data[0] > 0.9:
                    rot_type = -1
                elif data[2] < -0.9:
                    rot_type = 2

        return rot_type
    else:
        return rot_type


get_furniture_rotation_check("06ab5013-8f86-48ec-a7eb-275f3a08c644")