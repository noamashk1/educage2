class Level:
    def __init__(self, level_id: int, parameters: dict[str, Any]):
        self.level_id = level_id
        self.parameters = parameters

    def get_parameters(self) -> dict[str, Any]:
        return self.parameters
