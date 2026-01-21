from tools.feedback import FeedbackEngine

fb = FeedbackEngine("storage/events.jsonl")
print(fb.summary())
