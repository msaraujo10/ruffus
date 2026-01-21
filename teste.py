from tools.feedback import FeedbackEngine

fb = FeedbackEngine("storage/events.jsonl")
summary = fb.summary()
insights = fb.interpret(summary)

print("RESUMO:", summary)
print("\nINSIGHTS:")
for line in insights:
    print("-", line)
