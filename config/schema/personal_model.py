#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

from pydantic import BaseModel, Field
from typing import Literal


class PersonalModel(BaseModel):
    first_name: str = Field(..., min_length=1, description="Your first name")
    middle_name: str = ""
    last_name: str = Field(..., min_length=1, description="Your last name")
    phone_number: str = Field(..., min_length=10, max_length=15)
    current_city: str = ""
    street: str = ""
    state: str = ""
    zipcode: str = ""
    country: str = "India"
    # Literal enforces ONLY these exact case-sensitive strings
    ethnicity: Literal[
        "Decline", "Hispanic/Latino", "American Indian or Alaska Native", "Asian", "Black or African American", "Native Hawaiian or Other Pacific Islander", "White", "Other", ""] = ""
    gender: Literal["Male", "Female", "Other", "Decline", ""] = ""
    disability_status: Literal["Yes", "No", "Decline", ""] = ""
    veteran_status: Literal["Yes", "No", "Decline", ""] = ""

    @property
    def full_name(self) -> str:
        """Dynamically generates the full name without extra spaces."""
        return " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))
