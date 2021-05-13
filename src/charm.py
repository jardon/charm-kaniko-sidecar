#!/usr/bin/env python3
# Copyright 2021 jarred
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class CharmKanikoSidecarCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.executor_pebble_ready, self._on_executor_pebble_ready)

    def _on_executor_pebble_ready(self, event):
        """Define and start a workload using the Pebble API"""
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Define an initial Pebble layer configuration
        pebble_layer = {
            "summary": "kaniko layer",
            "description": "pebble config layer for kaniko",
            "services": {
                "kaniko": {
                    "override": "replace",
                    "summary": "kaniko",
                    "command": "/kaniko/executor",
                    "startup": "enabled",
                    "environment": {

                    },
                }
            },
        }
        # Add intial Pebble config layer using the Pebble API
        container.add_layer("kaniko", pebble_layer, combine=True)
        # Autostart any services that were defined with startup: enabled
        container.autostart()
        # Learn more about statuses in the SDK docs:
        # https://juju.is/docs/sdk/constructs#heading--statuses
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(CharmKanikoSidecarCharm)
