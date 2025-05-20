class RewardAndPunishmentSystem:
    def evaluate_response(self, response: str) -> str:
        if response.lower() == 'correct':
            return 'reward'
        else:
            return 'punishment'

    def deliver_reward(self):
        print("Delivering reward.")

    def impose_punishment(self):
        print("Imposing punishment.")
