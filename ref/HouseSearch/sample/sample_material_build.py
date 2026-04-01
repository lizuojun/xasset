from HouseSearch.sample.sample_base import SerializationBase


class SampleRoomMaterialFloor(SerializationBase):
    def __init__(self):
        self.jid = ""
        self.texture_url = ""
        self.color = [255, 255, 255]
        self.colorMode = "texture"
        self.size = [1.0, 1.0]
        self.seam = {}
        self.material_id = ""
        self.a = []


class SampleRoomMaterialBuild(SerializationBase):
    def __init__(self):
        self.id = ""
        self.type = ""
        self.floor = []
        self.win_pocket = []
        self.door_pocket = []
        self.customized_ceiling = []
        self.background = []
        self.ceiling = []
        self.win = []
        self.door = []

    def add_new_floor(self):
        pass

