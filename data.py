from typing import List, TypedDict


class Participant(TypedDict):
    user_id: str
    quantity: int
    ready: bool


class ChatMessage(TypedDict):
    chat_id: str
    message_id: str


class Group(TypedDict):
    main_user: str
# TODO: change it for DICT!
    participants: List[Participant] 
    sent_messages: List[ChatMessage]
    color: str
    notification_msg: str


ParticipantGroups = List[Group]


'''
{
  main_user: str
  color: str
  notification_msg: str
  participants: {
    user_id: str;
    quantity: int;
    ready: bool;
  }[]
  sent_messages:   {
    chat_id: str
    message_id: str
  }[]
}
'''
groups_washing: ParticipantGroups = []

users_laundry = {}

groups_by_main_user = {}
