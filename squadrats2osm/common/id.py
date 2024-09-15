class Id:
    id: int = -1

    def next_id(self) -> int:
        self.id -= 1
        return self.id