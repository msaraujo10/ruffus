from state_machine import State, World, DecisionEngine

world = World()
engine = DecisionEngine()
state = State.BOOT

while True:
    if state == State.BOOT:
        print("BOOT")
        state = State.SYNC

    elif state == State.SYNC:
        print("SYNC")
        state = State.IDLE

    elif state == State.IDLE:
        world.tick()
        decision = engine.scan(world)
        if decision:
            print("Oportunidade detectada")
            state = State.ENTERING

    elif state == State.ENTERING:
        print("Entrando em posição")
        world.has_position = True
        world.entry_price = world.price
        world.max_price = world.price
        state = State.IN_POSITION

    elif state == State.IN_POSITION:
        world.tick()
        print(f"Preço: {world.price}")
        # aqui depois entra stop, escudo, trailing
        if world.price < world.entry_price * 0.99:
            state = State.EXITING

    elif state == State.EXITING:
        print("Saindo da posição")
        world.has_position = False
        state = State.POST_TRADE

    elif state == State.POST_TRADE:
        print("Pós-trade")
        state = State.IDLE
