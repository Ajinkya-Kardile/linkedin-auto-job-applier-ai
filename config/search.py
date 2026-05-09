from config.schema.search_model import SearchModel

# ==========================================
# INSTANTIATE YOUR DATA HERE
# ==========================================
search_data = SearchModel(
    search_terms=["Java Developer", "Java Backend Developer", "Spring Boot Developer"],
    search_location="Pune",
    switch_number=30,
    randomize_search_order=False,
    sort_by="",
    date_posted="Past 24 hours",
    salary="",
    easy_apply_only=True,
    experience_level=[],
    job_type=["Full-time"],
    on_site=[],
    companies=[],
    location=[],
    industry=[],
    job_function=[],
    job_titles=[],
    benefits=[],
    commitments=[],
    under_10_applicants=False,
    in_your_network=False,
    fair_chance_employer=False,
    job_title_bad_words=["Python", "Frontend", "Front", "Node.js", "Android", "Lead", "Next", "Salesforce", "devops",
                         "Data Engineer", "Forward", "sharepoint", "wordpress","UI", "Dotnet",
                         ".NET","Microsoft", "Web", "ios", "HubSpot", "ServiceNow", "security", "Generative",
                         "Machine", "Artificial", "AI", "ML", "Share", "Infios", "Embedded", "test",
                         "cyber","power", "php", "Ruby"],
    job_desc_bad_words=["US Citizen", "USA Citizen", "No C2C", "No Corp2Corp", ".NET", "Embedded Programming", "PHP",
                        "Ruby", "CNC"],
    about_company_bad_words=["Crossover"],
    about_company_good_words=[],
    security_clearance=False,
    did_masters=False,
    current_experience=3
)
