from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String)

    interactions = relationship("InteractionLog", back_populates="hcp")


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"))
    date = Column(Date)
    time = Column(Time)
    attendees = Column(String)
    topics_discussed = Column(Text)
    sentiment = Column(String)
    materials_shared = Column(Text)
    key_outcomes = Column(String, nullable=True)
    follow_up_actions = Column(String, nullable=True)
    samples_distributed = Column(String, nullable=True)

    hcp = relationship("HCP", back_populates="interactions")
