from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from src.data.csv_manager import CSVManager
from src.utils.logger import logger

app = Flask(__name__)
CORS(app)

# Initialize our centralized data manager
csv_manager = CSVManager()


@app.route('/')
def home():
    """Displays the home page of the application (Dashboard)."""
    return render_template('index.html')


@app.route('/applied-jobs', methods=['GET'])
def get_applied_jobs():
    """
    Retrieves a list of applied jobs from the applications history CSV file
    via the safe CSVManager.
    """
    try:
        jobs = csv_manager.get_all_applied_jobs_for_ui()
        if not jobs:
            return jsonify({"error": "No applications history found"}), 404

        # Clean up the output to match the format expected by your UI
        formatted_jobs = []
        for row in jobs:
            formatted_jobs.append({
                'Job_ID': row.get('Job ID', ''),
                'Title': row.get('Title', ''),
                'Company': row.get('Company', ''),
                'HR_Name': row.get('HR Name', ''),
                'HR_Link': row.get('HR Link', ''),
                'Job_Link': row.get('Job Link', ''),
                'External_Job_link': row.get('External Job link', ''),
                'Date_Applied': row.get('Date Applied', '')
            })

        return jsonify(formatted_jobs)
    except Exception as e:
        logger.error(f"Error fetching applied jobs for UI: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/applied-jobs/<job_id>', methods=['PUT'])
def update_applied_job(job_id):
    """
    Placeholder for any updates you want to send from the UI back to the CSV.
    (e.g., manually changing a status)
    """
    try:
        data = request.json
        # TODO: Add an 'update_job' method to CSVManager if you want the UI
        # to be able to edit records.
        return jsonify({"message": f"Job {job_id} update endpoint active", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Web Server Dashboard on http://127.0.0.1:5000")
    # Run the Flask app
    app.run(debug=True, port=5000)