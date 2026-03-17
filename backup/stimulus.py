
class Stimulus:
    def __init__(self, stimulus_id: int, stimulus_type: str, duration: float):
        self.stimulus_id = stimulus_id
        self.type = stimulus_type
        self.duration = duration

    def play(self):
        print(f"Playing stimulus: {self.type} for {self.duration} seconds.")