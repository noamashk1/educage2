import level_1
class Mouse:
    def __init__(self, mouse_id: str, level: str):
        self.id = mouse_id
        self.level = level
        # self.performance_data = []

    def update_level(self, new_level: 'Level'):
        self.level = new_level

    def get_id(self):
        return self.id

    def get_level(self):
        return self.level


    # def record_performance(self, trial_data: Dict[str, Any]):
    #     self.performance_data.append(trial_data)