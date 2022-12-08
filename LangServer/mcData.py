from typing import (
    TypedDict, List, Literal, Dict, Any
)


MCID = int
"""
ID of block or item
"""


MCName = str
"""
Name of block or item
"""


class MCStates(TypedDict):
    type: Literal['bool', 'enum', 'int']
    values: List[str]
    name: str
    num_values: int


class MCBlock(TypedDict):
    id: MCID
    name: MCName
    displayName: str
    hardness: float
    resistance: float
    stackSize: int
    diggable: bool
    material: Literal[
        'plant;mineable/axe', 'gourd;mineable/axe', 'mineable/shovel',
        'default', 'vine_or_glow_lichen;plant;mineable/axe', 'mineable/axe',
        'plant', 'mineable/pickaxe', 'leaves;mineable/hoe', 'mineable/hoe', 'coweb', 'wool'
    ]
    transparent: bool
    emitLight: int
    filterLight: int
    defaultState: int
    minStateId: int
    maxStateId: int
    states: List[MCStates]
    drops: List[MCID]
    boundingBox: Literal['block', 'empty']


MCNoun = MCBlock


class MCData:
    _MCData: ...
    _Criteria: dict
    _Criterias: List[str]

    def __init__(self, version: str):
        import minecraft_data
        from json import load
        version = '.'.join(version.split('.')[:2])
        self._MCData = minecraft_data(version)
        self._Criteria = load(open('assets/criteria.json'))
        self._Criterias = load(open('assets/criterias.json'))['criterias']

    def blocks(self) -> List[MCBlock]:
        return self._MCData.blocks.values()

    def blocks_dict(self) -> Dict[MCName, MCBlock]:
        return self._MCData.blocks_name

    def blocks_keys(self) -> List[MCName]:
        return list(self._MCData.blocks_name.keys())

    def criterias(self) -> Dict[str, Any]:
        return self._Criteria

    def criterias_keys(self) -> List[str]:
        return self._Criterias

    def getByID(self, value: MCID | MCName) -> MCNoun:
        return self._MCData.find_item_or_block(value)


def values(x):
    if isinstance(x, str):
        return [x]
    result = list()
    for value in x.values():
        result.extend(values(value))
    return result
