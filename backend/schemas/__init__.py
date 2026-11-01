from datetime import date, datetime, time
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

Name = Annotated[str, Field(min_length=2, max_length=100)]
Password = Annotated[str, Field(min_length=8, max_length=72)]

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)

    @field_validator('*', mode='before')
    @classmethod
    def trim_text(cls, value, info):
        if isinstance(value, str) and info.field_name not in {'password', 'confirm_password'}:
            return value.strip()
        return value

def password_bytes(value):
    if value is not None and len(value.encode('utf-8')) > 72:
        raise ValueError('Kata sandi maksimal 72 byte UTF-8.')
    return value

class RegisterIn(Input):
    name: Name
    email: EmailStr = Field(max_length=254)
    password: Password
    confirm_password: str
    _bytes = field_validator('password')(password_bytes)

    @field_validator('name')
    @classmethod
    def trim_name(cls, value):
        if len(value.strip()) < 2:
            raise ValueError('Nama minimal 2 karakter.')
        return value.strip()

    @field_validator('email')
    @classmethod
    def normalize(cls, value):
        return str(value).lower()

    @model_validator(mode='after')
    def matches(self):
        if self.password != self.confirm_password:
            raise ValueError('Konfirmasi kata sandi tidak cocok.')
        return self

class LoginIn(Input):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=72)
    _bytes = field_validator('password')(password_bytes)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: Literal['user', 'admin']
    is_active: bool
    created_at: datetime

class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserOut

class UserCreate(RegisterIn):
    role: Literal['user', 'admin'] = 'user'
    is_active: bool = True

class UserPatch(Input):
    name: Name | None = None
    email: EmailStr | None = Field(default=None, max_length=254)
    role: Literal['user', 'admin'] | None = None
    is_active: bool | None = None
    password: Password | None = None
    _bytes = field_validator('password')(password_bytes)

class FacilityIn(Input):
    name: Annotated[str, Field(min_length=2, max_length=80)]

class FacilityOut(FacilityIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

class RoomIn(Input):
    name: Name
    capacity: int = Field(ge=1, le=100)
    description: str = Field(min_length=10, max_length=3000)
    thumbnail: str = Field(pattern=r'^/images/rooms/[a-z0-9-]+\.(webp|jpg|svg)$', max_length=255)
    is_active: bool = True
    facility_ids: list[int] = Field(default_factory=list, max_length=30)

class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    capacity: int
    description: str
    thumbnail: str
    is_active: bool
    facilities: list[FacilityOut]

class SlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    start_time: time
    end_time: time

class HolidayIn(Input):
    holiday_date: date
    name: str = Field(min_length=3, max_length=150)

class HolidayOut(HolidayIn):
    model_config = ConfigDict(from_attributes=True)

class BookingIn(Input):
    room_id: int = Field(gt=0)
    usage_date: date
    time_slot_id: int = Field(ge=1, le=5)

class AdminBookingIn(BookingIn):
    user_id: int = Field(gt=0)

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    room_id: int
    time_slot_id: int
    usage_date: date
    status: str
    created_at: datetime
    cancelled_at: datetime | None
    room: RoomOut
    time_slot: SlotOut
    operational_conflicts: list[str] = Field(default_factory=list)

class AdminBookingOut(BookingOut):
    user: UserOut

class AvailabilitySlot(SlotOut):
    available: bool
    reason: str | None

class AvailabilityOut(BaseModel):
    date: date
    calendar_verified: bool
    slots: list[AvailabilitySlot]

class SummaryOut(BaseModel):
    active_rooms: int
    active_users: int
    upcoming: int
    cancelled: int
    operational_conflicts: int

class Message(BaseModel):
    message: str
