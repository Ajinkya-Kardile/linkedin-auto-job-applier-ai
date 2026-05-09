#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

from config.schema.personal_model import PersonalModel

# ==========================================
# INSTANTIATE YOUR DATA HERE
# ==========================================
personal_data = PersonalModel(
    first_name="Ajinkya",
    middle_name="Shivaji",
    last_name="Kardile",
    phone_number="9876543210",
    current_city="Pune District, Maharashtra, India",
    street="A8-406 ABC Society, Survey No. 125, opposite Tech world, Tathawade, Pune",
    state="Maharashtra",
    zipcode="411033",
    country="India",
    ethnicity="Asian",
    gender="Male",
    disability_status="No",
    veteran_status="No"
)
