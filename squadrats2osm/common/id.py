class Id:
    id: int = -1

    def next_id(self) -> int:
        return --self.id