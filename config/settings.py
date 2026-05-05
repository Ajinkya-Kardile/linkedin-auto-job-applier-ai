from config.schema.setting_model import SettingsModel

# ==========================================
# INSTANTIATE YOUR DATA HERE
# ==========================================
settings_data = SettingsModel(
    pause_before_submit=True,
    pause_at_failed_question=True,
    overwrite_previous_answers=False,
    pause_after_filters=True,
    close_tabs=False,
    follow_companies=False,
    run_non_stop=False,
    alternate_sortby=True,
    cycle_date_posted=True,
    stop_date_cycle_at_24hr=True,
    uploadNewResume=True,
    generated_resume_path="all resumes/",
    file_name="output/all_applied_applications_history.csv",
    failed_file_name="output/all_failed_applications_history.csv",
    logs_folder_path="logs/",
    click_gap=3,
    run_in_background=False,
    disable_extensions=False,
    safe_mode=True,
    smooth_scroll=False,
    keep_screen_awake=True,
    stealth_mode=True,
    showAiErrorAlerts=False
)