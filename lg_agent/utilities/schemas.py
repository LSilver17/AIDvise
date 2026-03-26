from pydantic import BaseModel, Field

class ReliventEventsObject(BaseModel):
    ID: int = Field(description="The unique identifier for the event."),
    UrgencyLevel: int = Field(description="The urgency level of the event, based on how much time/effort it may require and how much time is left before the event occurs.")

class RelevantEventsSchema(BaseModel):
    relivent_events: list[ReliventEventsObject] = Field(description="A list of relevant events, each with its ID and urgency level.")
