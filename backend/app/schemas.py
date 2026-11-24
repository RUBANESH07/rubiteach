from pydantic import BaseModel, ConfigDict, Field


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str
    role: str
    xp: int
    streak: int


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProgressOut(BaseModel):
    xp: int
    level: int
    streak: int
    completed: dict[int, int]
    badges: list[str]


class SubmissionIn(BaseModel):
    lesson_id: int = Field(ge=1)
    sql: str = Field(min_length=1, max_length=5000)


class SubmissionOut(BaseModel):
    passed: bool
    message: str
    xp_awarded: int
    new_badges: list[str]
    progress: ProgressOut


class RunIn(BaseModel):
    runtime: str = Field(max_length=20)
    code: str = Field(max_length=20000)
    stdin: str = Field("", max_length=10000)


class RunOut(BaseModel):
    stdout: str
    error: str | None
    timed_out: bool
    ms: int


class HintOut(BaseModel):
    level: int
    total: int
    hint: str
