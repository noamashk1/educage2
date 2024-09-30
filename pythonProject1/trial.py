class Trial:
    def __init__(self, mouse_id: str, exp_data: dict):
        self.current_mouse = mouse_id
        self.exp_data = exp_data
        self.performance_data = []
        self.score = None

    def update_current_mouse(self, new_level: 'Level'):
        self.level = new_level

    def record_performance(self):
        pass

    def save_trial(self):
        pass

    def update_score(self, score): # hit\miss\fa\cr
        self.score = score

    def calculate_stim(self): #determine if the trial is go\nogo\catch using random
        pass

    def end_trial(self): # the trial is over - go to save it
        pass

"""זה לק שנמצא כרגע במחלקת מערכת עונש ותגמול"""
    # def evaluate_response(self, response):
    #     if response.lower() == 'correct':
    #         return 'reward'
    #     else:
    #         return 'punishment'
    #
    # def deliver_reward(self):
    #     print("Delivering reward.")
    #
    # def impose_punishment(self):
    #     print("Imposing punishment.")

