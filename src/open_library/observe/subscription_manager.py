#!/usr/bin/env python3


import asyncio
from collections import defaultdict
from open_library.observe.attribute_trie import AttributeTrie, AttributeProtocol
from open_library.observe.listener_spec import ListenerSpec


class SubscriptionManager:
    def __init__(self):
        self.attribute_trie = AttributeTrie()
        self.listeners = defaultdict(list)
        self.running_tasks = set()

    def subscribe(self, event_spec: AttributeProtocol, listener_spec: ListenerSpec):
        self.attribute_trie.insert(event_spec)
        self.listeners[hash(event_spec)].append(listener_spec)

    def unsubscribe(self, event_spec: AttributeProtocol, listener_spec: ListenerSpec):
        self.attribute_trie.remove(event_spec)
        self.listeners[hash(event_spec)].remove(listener_spec)

    async def notify_listeners(self, matching_event_specs, event):
        """
        Notify all listeners subscribed to the matching event specs.
        """
        for spec in matching_event_specs:
            for listener_spec in self.listeners[hash(spec)]:
                listener = listener_spec.get_listener()

                message_param_name = listener_spec.message_param_name

                listener_params = listener_spec.listener_params or {}
                if not message_param_name:
                    task = asyncio.create_task(listener(event))
                else:
                    task = asyncio.create_task(
                        listener(**listener_params, message_param_name=event)
                    )

                self.running_tasks.add(task)
                task.add_done_callback(lambda t: self.running_tasks.remove(t))

    async def publish(self, message: dict):
        """
        Publish an event.
        Finds all matching event specs and notifies the corresponding listeners.
        """

        event_spec: AttributeProtocol = message["event_spec"]
        matching_event_specs = self.attribute_trie.search(event_spec)
        await self.notify_listeners(matching_event_specs, message)
