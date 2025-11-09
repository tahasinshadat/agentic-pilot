from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from datetime import datetime

def daylight_launch_site():
    
    daylight_url = "https://go.daylight-health.com/intake-lexmed" 

    driver = webdriver.Chrome()
    driver.get(daylight_url)

    #Start appointment scheduling process
    wait = WebDriverWait(driver, 15)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="primaryButton"]'))).click()
    return driver

def daylight_select_date(driver, date_str) -> bool:
    """
    Clicks the given date (YYYY-MM-DD) in a React Datepicker.
    Navigates between months if needed.
    Returns True if the date was successfully selected, False if unavailable or not found.
    """
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    target_month_year = target_date.strftime("%B %Y")  # e.g., "December 2025"
    target_day = str(target_date.day)  # e.g., "10"

    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "react-datepicker__month-container")))

    while True:
        current_month = driver.find_element(By.CLASS_NAME, "react-datepicker__current-month").text

        if current_month == target_month_year:
            # Find the day element for this date
            day_elems = driver.find_elements(
                By.XPATH,
                f"//div[contains(@class, 'react-datepicker__day') "
                f"and not(contains(@class, 'outside-month')) "
                f"and text()='{target_day}']"
            )

            if not day_elems:
                print(f"⚠️ No day element found for {target_month_year} {target_day}")
                return False

            day_elem = day_elems[0]
            aria_disabled = day_elem.get_attribute("aria-disabled")
            class_attr = day_elem.get_attribute("class")

            # Check if the date is unavailable
            if aria_disabled == "true" or ("--highlighted" not in class_attr and "--selected" not in class_attr):
                print(f"🚫 {target_month_year} {target_day} is unavailable.")
                return False

            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", day_elem)
                day_elem.click()
                print(f"✅ Selected {target_month_year} {target_day}")
                return True
            except Exception as e:
                print(f"⚠️ Could not click {target_month_year} {target_day}: {e}")
                return False
        else:
            # Navigate months until the correct one is found
            current_date = datetime.strptime(current_month, "%B %Y")
            if current_date < target_date:
                next_btn = driver.find_element(By.CLASS_NAME, "react-datepicker__navigation--next")
                next_btn.click()
            else:
                prev_btn = driver.find_element(By.CLASS_NAME, "react-datepicker__navigation--previous")
                prev_btn.click()
            time.sleep(0.5)

def daylight_get_available_times(driver, date_str):
    """
    Returns a list of available appointment times for the given date (YYYY-MM-DD).
    If the date is unavailable or has no times, returns an empty list.
    """
    wait = WebDriverWait(driver, 10)

    # Step 1: Try selecting the date first (using your previous function)
    if not daylight_select_date(driver, date_str):
        print(f"🚫 No availability for {date_str} (date is greyed out or not clickable).")
        return []

    # Step 2: Wait for availability container to appear
    time.sleep(0.75)
    try:
        container = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "embeddable-availability-container"))
        )
    except Exception:
        print(f"⚠️ No availability container found for {date_str}")
        return []

    # Step 3: Get all available time slot elements
    slots = container.find_elements(By.CSS_SELECTOR, "div.available-slot")

    available_times = []
    for slot in slots:
        # Check that slot is visible and not disabled
        aria_label = slot.get_attribute("aria-label") or slot.text
        if aria_label and slot.is_displayed():
            available_times.append(aria_label.strip())

    # Step 4: Return results
    if available_times:
        print(f"✅ Found {len(available_times)} available times for {date_str}: {available_times}")
    else:
        print(f"🚫 No time slots available for {date_str}")

    return available_times

def daylight_confirm_time(driver, date_str, time_str):
    """
    Selects a specific appointment time if it is available.
    After selecting the time, waits for and clicks the confirm button.
    If the time isn't available, prompts the user to choose a different time.
    Returns True if the time and confirmation are successfully selected.

    time_str should be in the format "X:XX PM".
    """
    available_times = daylight_get_available_times(driver, date_str)

    if not available_times:
        print(f"🚫 No available times for {date_str}.")
        return False

    if time_str not in available_times:
        return f"{time_str} is not available on {date_str}. Available options: {', '.join(available_times)}"

    # Select the desired time
    wait = WebDriverWait(driver, 15)
    container = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "embeddable-availability-container"))
    )

    # Find and click the slot matching the desired time
    try:
        slot = container.find_element(
            By.XPATH,
            f"//div[contains(@class, 'available-slot') and @aria-label='{time_str}']"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", slot)
        slot.click()
        print(f"✅ Selected {time_str} on {date_str}")
    except Exception as e:
        print(f"⚠️ Could not click time slot {time_str}: {e}")
        return False

    # Wait for the "Confirm Date and Time" button to become clickable, then click it
    try:
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="confirm-date-time"]'))
        )
        time.sleep(0.4)  # brief pause for any animation
        confirm_btn.click()
        print(f"✅ Confirmed {date_str} at {time_str}")
        return True
    except Exception as e:
        print(f"⚠️ Could not confirm time {time_str}: {e}")
        return False

def daylight_fill_contact_form(driver, first_name, last_name, email, phone):
    """
    Fills out the appointment contact form and clicks the 'Confirm Appointment' button.
    Arguments:
        first_name (str)
        last_name (str)
        email (str)
        phone (str) - formatted as xxx-xxx-xxxx
    Returns:
        True if the form was successfully submitted, False otherwise.
    """
    wait = WebDriverWait(driver, 15)

    try:
        # Wait for form to appear
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
        time.sleep(0.5)  # brief pause for animations

        # Fill First Name
        first_input = driver.find_element(By.ID, "first_name")
        first_input.clear()
        first_input.send_keys(first_name)

        # Fill Last Name
        last_input = driver.find_element(By.ID, "last_name")
        last_input.clear()
        last_input.send_keys(last_name)

        # Fill Email
        email_input = driver.find_element(By.ID, "email")
        email_input.clear()
        email_input.send_keys(email)

        # Fill Phone Number
        phone_input = driver.find_element(By.ID, "phone_number")
        phone_input.clear()
        phone_input.send_keys(phone)

        print(f"✅ Filled form for {first_name} {last_name}, {email}, {phone}")

        # Wait until the confirm button is enabled, then click it
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="primaryButton"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
        time.sleep(0.5)
        confirm_btn.click()
        print("✅ Confirm Appointment button clicked.")
        return True

    except Exception as e:
        print(f"⚠️ Could not complete form submission: {e}")
        return False

def daylight_press_confirm_button(driver):
    """
    Waits for and clicks the 'Confirm Appointment' button at the end of the form.
    Assumes the contact form has already been filled out successfully.
    Returns True if the button was clicked, False otherwise.
    """
    wait = WebDriverWait(driver, 15)

    try:
        # Wait for the Confirm Appointment button to become clickable
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="primaryButton"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
        time.sleep(0.5)  # short delay to ensure it’s visible and stable
        confirm_btn.click()
        print("✅ Confirm Appointment button clicked.")
        return True

    except Exception as e:
        print(f"⚠️ Could not click Confirm Appointment button: {e}")
        return False

if __name__ == "__main__":
    driver = daylight_launch_site()
    date = "2025-12-07"
    time_choice = "5:30 PM"

    if daylight_confirm_time(driver, date, time_choice):
        print("✅ Appointment time confirmed. Filling out contact info...")
        daylight_fill_contact_form(
            driver,
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@example.com",
            phone="333-333-3333"
        )
    else:
        print("❌ Could not confirm the requested time.")