from config.schema.question_model import QuestionsModel

# ==========================================
# INSTANTIATE YOUR DATA HERE
# ==========================================
questions_data = QuestionsModel(
    default_resume_path="resume/resume.pdf",
    years_of_experience=2,
    additional_months_of_experience=5,
    require_visa="No",
    website="",
    linkedIn="https://www.linkedin.com/in/ajinkya-kardile/",
    github="https://github.com/Ajinkya-Kardile",
    us_citizenship="Other",
    desired_salary=1500000,
    current_ctc=1000000,
    notice_period=30,
    linkedin_headline="Full Stack Developer with B.Tech in Information Technology and 3.5 years of experience",
    linkedin_summary="I'm a Java Developer with 3.5 years of experience at ABC Technologies, working across backend and frontend stacks. Skilled in Java, Spring Boot, Microservices and React.js, with experience in relational and NoSQL databases like MySQL, BigQuery, and Aerospike.",
    cover_letter="""Dear Hiring Manager,

I am writing to express my interest in the Java Developer position at your organization. With over 3.5 years of hands-on experience in building scalable backend systems using Java, Spring Boot, and microservices architecture, I am confident in my ability to contribute effectively to your engineering team.

In my current role, I have designed and developed high-performance RESTful APIs, optimized database queries, and implemented scalable microservices that improved system performance and reliability. I have strong experience working with Java 17, Spring Boot, MySQL, and REST API development, along with exposure to React for frontend integration. My work has resulted in measurable improvements, including increased API response speed and enhanced system scalability.

I am well-versed in Agile/Scrum methodologies and have collaborated closely with cross-functional teams to deliver robust, production-ready solutions. I am particularly interested in this opportunity because of your organization’s focus on innovation and building impactful technology solutions.

I am eager to bring my problem-solving skills, technical expertise, and passion for backend development to your team. I would welcome the opportunity to discuss how my experience aligns with your requirements.

Thank you for your time and consideration.

Sincerely,
Ajinkya Kardile
[Your Contact Number]
[Your Email Address]
[LinkedIn Profile]""",
    user_information_all="",
    recent_employer="ABC Technologies",
    confidence_level="8"
)
