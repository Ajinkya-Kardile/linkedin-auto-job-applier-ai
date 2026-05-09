from pydantic import BaseModel, Field
from typing import List, Literal


class SearchModel(BaseModel):
    # Must contain at least one search term
    search_terms: List[str] = Field(..., min_length=1)
    search_location: str = ""

    switch_number: int = Field(default=30, gt=0)
    randomize_search_order: bool = False

    sort_by: Literal["Most recent", "Most relevant", ""] = ""
    date_posted: Literal["Any time", "Past month", "Past week", "Past 24 hours", ""] = "Past week"
    salary: str = ""

    easy_apply_only: bool = True

    # List of Literal choices
    experience_level: List[
        Literal["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]] = []
    job_type: List[Literal["Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"]] = []
    on_site: List[Literal["On-site", "Remote", "Hybrid"]] = []

    companies: List[str] = []
    location: List[str] = []
    industry: List[str] = []
    job_function: List[str] = []
    job_titles: List[str] = []
    benefits: List[str] = []
    commitments: List[str] = []

    under_10_applicants: bool = False
    in_your_network: bool = False
    fair_chance_employer: bool = False

    job_title_bad_words: List[str] = []
    job_desc_bad_words: List[str] = []
    about_company_bad_words: List[str] = []
    about_company_good_words: List[str] = []

    security_clearance: bool = False
    did_masters: bool = False
    current_experience: int = Field(default=3, ge=-1)
