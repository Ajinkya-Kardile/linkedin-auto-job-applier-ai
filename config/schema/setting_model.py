#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

from pydantic import BaseModel, Field


class SettingsModel(BaseModel):
    pause_before_submit: bool = True
    pause_at_failed_question: bool = True
    overwrite_previous_answers: bool = False
    pause_after_filters: bool = True

    close_tabs: bool = False
    follow_companies: bool = False
    run_non_stop: bool = False
    alternate_sortby: bool = True
    cycle_date_posted: bool = True
    stop_date_cycle_at_24hr: bool = True

    uploadNewResume: bool = True
    generated_resume_path: str = "all resumes/"

    file_name: str = "output/all_applied_applications_history.csv"
    failed_file_name: str = "output/all_failed_applications_history.csv"
    logs_folder_path: str = "logs/"

    click_gap: int = Field(default=3, ge=0)

    run_in_background: bool = False
    disable_extensions: bool = False
    safe_mode: bool = True
    smooth_scroll: bool = False
    keep_screen_awake: bool = True
    stealth_mode: bool = True
    showAiErrorAlerts: bool = False

