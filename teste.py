from tools.replay_analyzer import ReplayAnalyzer

ra = ReplayAnalyzer("storage/state.json")

btc_blocked = ra.filter_events(symbol="BTCUSDT", result="BLOCKED_BY_RISK")
ra.pretty_print(btc_blocked)
