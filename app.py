from flask import Flask, render_template, request, redirect, url_for
from threading import Thread, Lock
import time
from plyer import notification
import platform
import os
import pygetwindow as gw
from queue import Queue
app = Flask(__name__)

# Global dictionary to store start times of applications
start_times = {}
# Global variable to store screen time limit
screen_time_limit = None
# Global variable to store the screen time limit thread
screen_time_thread = None
# Flag to track if the screen time limit has been set
screen_time_limit_set = False

def notify_error():
    notification.notify(
        title='Screen Time is already set',
        message='Screen time limit cannot be changed.',
        app_icon=None,
        timeout=10,
    )


def notify_on():
    notification.notify(
        title='Screen Time is enabled',
        message='Screen time limit is enabled.',
        app_icon=None,
        timeout=10,
    )


def notify_off():
    notification.notify(
        title='Screen Time is disabled',
        message='Screen time limit is disabled.',
        app_icon=None,
        timeout=10,
    )


def notify_time_limit_set(limit):
    notification.notify(
        title='Screen Time Limit Set',
        message=f'Screen time limit set for {limit} minutes.',
        app_icon=None,
        timeout=10,
    )


def notify_extra_time_added(extra_time_minutes):
    notification.notify(
        title='Extra Time Added',
        message=f'{extra_time_minutes} minutes have been added.',
        app_icon=None,
        timeout=10,
    )


def notify_time_remaining(remaining_minutes):
    notification.notify(
        title='Time Remaining',
        message=f'You have {remaining_minutes} minutes left of screen time.',
        app_icon=None,
        timeout=10,
    )


def notify_time_limit_reached():
    notification.notify(
        title='Time Limit Reached',
        message='You have reached your screen time limit. System will shut down.',
        app_icon=None,
        timeout=10,
    )


def log_out_and_shutdown():
    system_platform = platform.system()

    # Choose the appropriate shutdown command based on the operating system
    if system_platform == 'Windows':
        os.system('shutdown /s /t 1 /f')  # Windows shutdown command
    elif system_platform == 'Linux':
        os.system('shutdown now')  # Linux shutdown command
    elif system_platform == 'Darwin':
        os.system('shutdown -h now')  # macOS shutdown command
    else:
        print(f"Unsupported operating system: {system_platform}")


def get_running_applications():
    running_applications = {}

    # Get list of all open windows
    windows = gw.getAllWindows()

    for window in windows:
        title = window.title

        # Check if window title is not empty
        if title:
            if title not in start_times:
                start_times[title] = time.time()
            else:
                duration = int(time.time() - start_times[title])
                running_applications[title] = duration

    return running_applications


# Global variable to store remaining time
remaining_time = 0
remaining_time_lock = Lock()
extra_time = 0

# Initialize a shared queue
extra_time_queue = Queue()


def set_screen_time_limit_thread(limit_in_minutes):
    global extra_time
    total_time = limit_in_minutes
    end_time = time.time() + total_time * 60  # Adjust end time with initial time limit

    # Reminders for time left (adjust as needed)
    reminder_intervals = [0.25, 0.5, 0.75]  # Remind at 25%, 50%, and 75% of the time limit
    reminders_shown = set()

    while time.time() < end_time:
        with remaining_time_lock:
            remaining_time = end_time - time.time()
            #

        # Check for new extra time values in the queue
        if not extra_time_queue.empty():
            new_extra_time = extra_time_queue.get()
            extra_time += new_extra_time  # Update global extra_time
            total_time += new_extra_time  # Update total time
            end_time += new_extra_time * 60  # Update end time accordingly

            # Notify user about the added extra time
            notify_extra_time_added(new_extra_time)

        # Check and display reminders
        for interval in reminder_intervals:
            if remaining_time / 60 < total_time * interval and interval not in reminders_shown:
                notify_time_remaining(int(remaining_time / 60))
                reminders_shown.add(interval)

        # Get and display list of running applications with durations
        running_applications = get_running_applications()
        print("Currently running applications with durations:")
        for application, duration in running_applications.items():
            print(f"{application}: {duration} seconds")

        # Sleep for a short time to avoid high CPU usage
        time.sleep(60)

    with remaining_time_lock:
        remaining_time = 0

    notify_time_limit_reached()
    log_out_and_shutdown()


def set_screen_time_limit(limit_in_minutes):
    global extra_time, screen_time_limit, screen_time_thread
    # Start the screen time limit function in a separate thread
    screen_time_limit = limit_in_minutes
    total_time = limit_in_minutes + extra_time
    end_time = time.time() + total_time * 60

    # Start the screen time limit function in a separate thread
    screen_time_thread = Thread(target=set_screen_time_limit_thread, args=(limit_in_minutes,))
    screen_time_thread.start()


@app.route('/')
def loginpage():
    return render_template('login_register.html')


@app.route('/screentime', methods=['POST'])
def screentime():
    return redirect(url_for('screenlimit'))


@app.route('/screenlimit')
def screenlimit():
    return render_template('screenlimit.html')


@app.route('/login', methods=['POST'])
def login():
    global screen_time_limit_set
    limit = int(request.form['time_limit'])

    # Check if the screen time limit has already been set
    if screen_time_limit_set:
        notify_error()
        return redirect(url_for('index'))

    # Show a notification indicating that the screen time limit has been set
    notify_time_limit_set(limit)

    # Start the program to calculate the timing of the apps used
    set_screen_time_limit(limit)

    # Set the flag to indicate that the screen time limit has been set
    screen_time_limit_set = True

    return redirect(url_for('index'))


@app.route('/index')
def index():
    activities = get_running_applications()
    return render_template('index.html', activities=activities)


@app.route('/password', methods=['POST'])
def password():
    return redirect(url_for('requesttime'))


@app.route('/requesttime')
def requesttime():
    return render_template('requesttime.html')


# Flask route to add extra time
@app.route('/extratime', methods=['POST'])
def extratime():
    extra_time = int(request.form['request_time'])
    extra_time_queue.put(extra_time)  # Enqueue extra time value
    return redirect(url_for('third'))


@app.route('/toggle_screen_time', methods=['POST'])
def toggle_screen_time():
    global exit_flag
    toggle_on = request.form.get('toggle_screen_time') == 'on'

    if toggle_on:
        # Toggle is on, set the exit flag
        exit_flag = True
        # Exit the program gracefully
        os._exit(0)
    else:
        notify_on()
        return redirect(url_for('screenlimit'))


@app.route('/third')
def third():
    activities = get_running_applications()
    return render_template('index.html', activities=activities)


if __name__ == "__main__":
    app.run(debug=True)