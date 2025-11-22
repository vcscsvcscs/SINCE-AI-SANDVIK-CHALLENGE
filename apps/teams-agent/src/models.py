"""Pydantic models for Microsoft Teams Message Actions Payload"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Annotated


class MessageActionsPayloadUser(BaseModel):
    """Represents a user entity."""
    model_config = ConfigDict(extra="allow")
    
    user_identity_type: Optional[Annotated[
        str,
        Field(pattern=r"^(aadUser|onPremiseAadUser|anonymousGuest|federatedUser)$")
    ]] = None
    id: Optional[str] = None
    display_name: Optional[str] = None


class MessageActionsPayloadApp(BaseModel):
    """Represents an application entity."""
    model_config = ConfigDict(extra="allow")
    
    application_identity_type: Optional[Annotated[
        str,
        Field(pattern=r"^(aadApplication|bot|tenantBot|office365Connector|webhook)$")
    ]] = None
    id: Optional[str] = None
    display_name: Optional[str] = None


class MessageActionsPayloadConversation(BaseModel):
    """Represents a team or channel entity."""
    model_config = ConfigDict(extra="allow")
    
    conversation_identity_type: Optional[str] = None
    id: Optional[str] = None
    display_name: Optional[str] = None


class MessageActionsPayloadFrom(BaseModel):
    """Represents a user, application, or conversation type that either sent or was referenced in a message."""
    model_config = ConfigDict(extra="allow")
    
    user: Optional["MessageActionsPayloadUser"] = None
    application: Optional["MessageActionsPayloadApp"] = None
    conversation: Optional["MessageActionsPayloadConversation"] = None


class MessageActionsPayloadBody(BaseModel):
    """Plaintext/HTML representation of the content of the message."""
    model_config = ConfigDict(extra="allow")
    
    content_type: Optional[str] = None
    content: Optional[str] = None


class MessageActionsPayloadAttachment(BaseModel):
    """Represents the attachment in a message."""
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = None
    content_type: Optional[str] = None
    content_url: Optional[str] = None
    content: Optional[Any] = None
    name: Optional[str] = None
    thumbnail_url: Optional[str] = None


class MessageActionsPayloadMention(BaseModel):
    """Represents the entity that was mentioned in the message."""
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = None
    mention_text: Optional[str] = None
    mentioned: Optional["MessageActionsPayloadFrom"] = None


class MessageActionsPayloadReaction(BaseModel):
    """Represents the reaction of a user to a message."""
    model_config = ConfigDict(extra="allow")
    
    reaction_type: Optional[str] = None
    created_date_time: Optional[str] = None
    user: Optional["MessageActionsPayloadFrom"] = None


class MessageActionsPayload(BaseModel):
    """Represents the individual message within a chat or channel where a message action is taken."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    
    id: Optional[str] = None
    reply_to_id: Optional[str] = None
    message_type: Optional[str] = None
    created_date_time: Optional[str] = None
    last_modified_date_time: Optional[str] = None
    deleted: Optional[bool] = None
    subject: Optional[str] = None
    summary: Optional[str] = None
    importance: Optional[Annotated[str, Field(pattern=r"^(normal|high|urgent)$")]] = None
    locale: Optional[str] = None
    link_to_message: Optional[str] = None
    from_property: Optional[MessageActionsPayloadFrom] = Field(None, alias="from")
    body: Optional[MessageActionsPayloadBody] = None
    attachment_layout: Optional[str] = None
    attachments: Optional[List[MessageActionsPayloadAttachment]] = None
    mentions: Optional[List[MessageActionsPayloadMention]] = None
    reactions: Optional[List[MessageActionsPayloadReaction]] = None

