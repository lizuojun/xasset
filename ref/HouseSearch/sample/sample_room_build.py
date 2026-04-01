from HouseSearch.sample.sample_base import SerializationBase, SerializationList
from HouseSearch.sample.sample_material_build import SampleRoomMaterialBuild
from functools import singledispatch


class SampleRoomSchemeBuild(SerializationBase):
    def __init__(self):
        self.code = 0
        self.score = 80
        self.style = "Contemporary"
        self.area = 0.0
        self.room_type = ""
        self.material = SampleRoomMaterialBuild()
        self.decorate = {}
        self.painting = {}
        self.group = []
        self.group_area = 0.0
        self.source_house = "diy_source_house"
        self.source_room = "diy_source_room"
        self.source_room_area = 0.0
        self.line_unit = []


class SampleRoomBuild(SerializationBase):
    def __init__(self):
        self.room_style = "Contemporary"
        self.room_type = "Other"
        self.room_area = 0.0
        self.room_height = 2.8
        self.layout_scheme = SerializationList()
        self.layout_mesh = SerializationList()

    def parse_json_class(self, room_info):
        pass


if __name__ == '__main__':
    a = SampleRoomBuild()

