from abc import ABC, abstractmethod


class EquipmentChoicesProvider(ABC):
    @abstractmethod
    def get_weapon1_choices(self):
        pass

    @abstractmethod
    def get_weapon2_choices(self):
        pass

    @abstractmethod
    def get_weapon3_choices(self):
        pass

    @abstractmethod
    def get_armor_choices(self):
        pass

    @abstractmethod
    def get_gear_choices(self):
        pass

    @abstractmethod
    def get_pack_choices(self):
        pass
