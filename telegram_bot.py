def send_feedback(feedback):
    with open("feedback.txt", "a") as file:
        file.write(f"Name: {feedback.name}\n")
        file.write(f"Surname: {feedback.surname}\n")
        file.write(f"Stars: {feedback.start}\n")
        file.write(f"Comment: {feedback.comment}\n")
        file.write("-" * 30 + "\n")

    return True
