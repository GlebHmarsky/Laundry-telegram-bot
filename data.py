from typing import List, TypedDict


class Participant(TypedDict):
    user_id: str
    quantity: int
    ready: bool


class Group(TypedDict):
    main_user: str
    participants: List[Participant]


ParticipantGroups = List[Group]


'''
{
  main_user: str
  participants: {
    user_id: str;
    quantity: int;
    ready: bool;
  }[]
}
'''
groups_washing: ParticipantGroups = []

users_laundry = {}

groups_by_main_user = {}