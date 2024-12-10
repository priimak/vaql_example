from typing import Protocol


class LinkedLLNode(Protocol):
    def link_to_node(self, node) -> None: ...
