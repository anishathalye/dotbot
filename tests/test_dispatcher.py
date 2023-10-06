import dotbot.dispatcher


def test_dispatcher_instantiation(home, dotfiles, run_dotbot):
    """Verify that the dispatcher caches itself as a singleton."""

    assert dotbot.dispatcher.current_dispatcher is None

    dotfiles.write_config([])
    run_dotbot()

    # Verify the dispatcher has been cached.
    assert dotbot.dispatcher.current_dispatcher is not None

    existing_id = id(dotbot.dispatcher.current_dispatcher)
    new_instance = dotbot.dispatcher.Dispatcher("bogus")

    # Verify the new and existing instances are the same.
    assert existing_id == id(new_instance)

    # Verify the singleton was not overridden.
    assert existing_id == id(dotbot.dispatcher.current_dispatcher)
