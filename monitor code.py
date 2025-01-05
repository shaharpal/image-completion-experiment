from psychopy import visual, core, event, data, monitors
import random
import csv
import os

# Define current directory
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Paths to image directories
realistic_correct_dir = 'C:/Users/ohadp/OneDrive/Desktop/completeingExperient/ready photos- knowm realistic/correct_cuts'
realistic_wrong_dir = 'C:/Users/ohadp/OneDrive/Desktop/completeingExperient/ready photos- knowm realistic/wrong_cuts'
realistic_minus_correct_dir = 'C:/Users/ohadp/OneDrive/Desktop/completeingExperient/ready photos- knowm realistic/original_minus_correct'
abstract_correct_dir = 'C:/Users/ohadp/OneDrive/Desktop/completeingExperient/unknown_images_processed/correct_cuts'
abstract_wrong_dir = 'C:/Users/ohadp/OneDrive/Desktop/completeingExperient/unknown_images_processed/wrong_cuts'
abstract_minus_correct_dir = 'C:/Users/ohadp/OneDrive/Desktop/completeingExperient/unknown_images_processed/original_minus_correct'

# Load the current participant ID
participant_id_file = "participant_id.txt"
if os.path.exists(participant_id_file):
    with open(participant_id_file, "r") as file:
        participant_id = int(file.read().strip())
else:
    participant_id = 1  # Default starting ID if file doesn't exist

# Increment the participant ID for the next use
next_participant_id = participant_id + 1
with open(participant_id_file, "w") as file:
    file.write(str(next_participant_id))

# Load image file paths
realistic_correct_images = [os.path.join(realistic_correct_dir, f) for f in os.listdir(realistic_correct_dir)]
realistic_wrong_images = [os.path.join(realistic_wrong_dir, f) for f in os.listdir(realistic_wrong_dir)]
realistic_minus_correct_images = [os.path.join(realistic_minus_correct_dir, f) for f in os.listdir(realistic_minus_correct_dir)]
abstract_correct_images = [os.path.join(abstract_correct_dir, f) for f in os.listdir(abstract_correct_dir)]
abstract_wrong_images = [os.path.join(abstract_wrong_dir, f) for f in os.listdir(abstract_wrong_dir)]
abstract_minus_correct_images = [os.path.join(abstract_minus_correct_dir, f) for f in os.listdir(abstract_minus_correct_dir)]

# Combine images into a trial list
trials = []
for correct, wrong, minus_correct in zip(realistic_correct_images, realistic_wrong_images, realistic_minus_correct_images):
    trials.append({"image_type": "familiar", "correct": correct, "wrong": wrong, "minus_correct": minus_correct})
for correct, wrong, minus_correct in zip(abstract_correct_images, abstract_wrong_images, abstract_minus_correct_images):
    trials.append({"image_type": "abstract", "correct": correct, "wrong": wrong, "minus_correct": minus_correct})

# Randomize trial order
random.shuffle(trials)

# Monitor setup
monitor = monitors.Monitor(name='default')
monitor.setSizePix((1920, 1080))
monitor.setWidth(52)  # Width in cm
monitor.setDistance(60)  # Distance in cm

# Window setup
win = visual.Window(size=(1920, 1080), color=(1, 1, 1), units="pix", fullscr=True, monitor=monitor)

# Display title screen
title = visual.TextStim(win, text="Welcome to the Image Completion Experiment", color=(-1, -1, -1), height=40)
title.draw()
win.flip()
core.wait(6)  # Extended to 6 seconds

# Instructions
instructions = visual.TextStim(win, text="In this task, you will see an incomplete image and two options to complete it.\n\nUse the keys 1 (left) and 2 (right) to select the correct piece.\n\nPress any key to start.", color=(-1, -1, -1))
instructions.draw()
win.flip()
event.waitKeys()

# Determine if participant is in warm-up group
warm_up = random.choice([True, False])
warm_up_message = "You are part of the warm-up group.\nPlease stop and call the experimenter." if warm_up else "You will proceed directly to the experiment.\nPress Enter to continue."
warm_up_text = visual.TextStim(win, text=warm_up_message, color=(-1, -1, -1))
warm_up_text.draw()
win.flip()
event.waitKeys(keyList=["return"])  # Wait for Enter key to proceed

# Trial setup
results = []
clock = core.Clock()

for trial in trials:
    # Randomize left/right positions for correct and wrong images
    positions = [(-300, -300), (300, -300)]  # Bottom left and bottom right
    random.shuffle(positions)

    correct_position = positions[0]
    wrong_position = positions[1]

    correct_image = visual.ImageStim(win, image=trial["correct"], pos=correct_position, size=(200, 200))
    wrong_image = visual.ImageStim(win, image=trial["wrong"], pos=wrong_position, size=(200, 200))
    minus_correct_image = visual.ImageStim(win, image=trial["minus_correct"], pos=(0, 200), size=(400, 400))  # Top center

    # Display images
    minus_correct_image.draw()
    correct_image.draw()
    wrong_image.draw()
    win.flip()

    # Record response
    clock.reset()
    keys = event.waitKeys(keyList=["1", "2"], timeStamped=clock)

    # Determine correctness
    response = keys[0][0]
    rt = keys[0][1]
    correct = (response == "1" and correct_position == (-300, -300)) or (response == "2" and correct_position == (300, -300))

    # Save trial data
    results.append({
        "participant_id": participant_id,  # Automatically assigned ID
        "warm_up": warm_up,
        "image_type": trial["image_type"],
        "correct_position": "left" if correct_position == (-300, -300) else "right",
        "response": response,
        "correct": correct,
        "reaction_time": rt
    })

    # Clear screen
    win.flip()
    core.wait(0.5)

# Calculate summary statistics
familiar_trials = [r for r in results if r["image_type"] == "familiar"]
abstract_trials = [r for r in results if r["image_type"] == "abstract"]

def calc_stats(trials):
    correct_trials = [t for t in trials if t["correct"]]
    accuracy = len(correct_trials) / len(trials) * 100
    reaction_times = [t["reaction_time"] for t in trials]
    avg_rt = sum(reaction_times) / len(reaction_times)
    std_rt = (sum((x - avg_rt) ** 2 for x in reaction_times) / len(reaction_times)) ** 0.5
    return accuracy, avg_rt, std_rt

familiar_acc, familiar_avg_rt, familiar_std_rt = calc_stats(familiar_trials)
abstract_acc, abstract_avg_rt, abstract_std_rt = calc_stats(abstract_trials)
gap_accuracy = familiar_acc - abstract_acc
gap_rt = familiar_avg_rt - abstract_avg_rt

# Save results to CSV
csv_file = "results.csv"
with open(csv_file, mode="a", newline="") as file:  # Use "a" to append data
    writer = csv.DictWriter(file, fieldnames=[
        "participant_id", "warm_up", "image_type", "correct_position", "response", "correct", "reaction_time"
    ])
    if os.stat(csv_file).st_size == 0:  # Write header only if file is empty
        writer.writeheader()
    writer.writerows(results)

    # Add summary statistics
    writer.writerow({})  # Blank row
    writer.writerow({
        "participant_id": participant_id,
        "warm_up": warm_up,
        "image_type": "Summary",
        "correct_position": "",
        "response": "",
        "correct": f"Familiar Accuracy: {familiar_acc:.2f}%",
        "reaction_time": f"Familiar Avg RT: {familiar_avg_rt:.2f} ms, Familiar Std RT: {familiar_std_rt:.2f} ms"
    })
    writer.writerow({
        "participant_id": participant_id,
        "warm_up": warm_up,
        "image_type": "Summary",
        "correct_position": "",
        "response": "",
        "correct": f"Abstract Accuracy: {abstract_acc:.2f}%",
        "reaction_time": f"Abstract Avg RT: {abstract_avg_rt:.2f} ms, Abstract Std RT: {abstract_std_rt:.2f} ms"
    })
    writer.writerow({
        "participant_id": participant_id,
        "warm_up": warm_up,
        "image_type": "Gap",
        "correct_position": "",
        "response": "",
        "correct": f"Accuracy Gap: {gap_accuracy:.2f}%",
        "reaction_time": f"RT Gap: {gap_rt:.2f} ms"
    })

# Display thank you screen
thank_you = visual.TextStim(win, text="Thank you for participating in the experiment! 😊", color=(-1, -1, -1), height=40)
thank_you.draw()
win.flip()
core.wait(5)

# Close window
win.close()
core.quit()
