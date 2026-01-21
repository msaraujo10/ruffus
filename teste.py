from tools.feedback import FeedbackEngine

fb = FeedbackEngine("storage/events.jsonl")

diag = fb.diagnose()

print("\nDIAGNÓSTICO:")
print("Health:", diag["health"])
print("\nProblemas:")
for p in diag["problems"]:
    print("-", p)

print("\nSinais:")
for s in diag["signals"]:
    print("-", s)

print("\nRecomendações:")
for r in diag["recommendations"]:
    print("-", r)
