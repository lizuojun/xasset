from HouseSearch.sample.sample_base import SerializationBase
from HouseSearch.sample.sample_room_build import SampleRoomBuild


class SampleHouseBuild(SerializationBase):
    def __init__(self, house_sample):
        for room_id, room_info in house_sample.items():
            room_id = room_info["id"]
            setattr(self, room_id, SampleRoomBuild(room_info))

    def get_room(self, room_id):
        return getattr(self, room_id, None)
