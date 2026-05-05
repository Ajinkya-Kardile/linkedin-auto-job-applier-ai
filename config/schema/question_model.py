from pydantic import BaseModel, Field
from typing import Literal


class QuestionsModel(BaseModel):
    default_resume_path: str = "resume/resume.pdf"
    years_of_experience: int = Field(default=0, ge=0)
    additional_months_of_experience: int = Field(default=0, ge=0, le=11)
    require_visa: Literal["Yes", "No"] = "No"
    website: str = ""
    linkedIn: str = "https://www.linkedin.com/in/ajinkya-kardile/"
    github: str = "NA"

    us_citizenship: Literal[
        "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident", "Other", ""] = "Other"

    # Must be strictly greater than 0
    desired_salary: int = Field(..., gt=0)
    current_ctc: int = Field(..., gt=0)

    # Must be 0 or greater
    notice_period: int = Field(..., ge=0)

    linkedin_headline: str = ""
    linkedin_summary: str = ""
    cover_letter: str = ""
    user_information_all: str = ""
    recent_employer: str = ""
    confidence_level: str = Field(default="8", pattern=r"^(10|[1-9])$")  # Regex ensures it is "1" to "10"

