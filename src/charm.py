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
from charms.nginx_ingress_integrator.v0.ingress import IngressRequires

logger = logging.getLogger(__name__)


class KaniqueueCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.kaniqueue_pebble_ready, self._on_kaniqueue_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

        self.ingress = IngressRequires(self, {
            "service-hostname": "kaniqueue.juju",
            "service-name": self.app.name,
            "service-port": 10000
        })

    def _on_kaniqueue_pebble_ready(self, event):
        """Define and start a workload using the Pebble API"""
        # Get a reference the container attribute on the PebbleReadyEvent
        container = event.workload
        # Define an initial Pebble layer configuration
        pebble_layer = self._kaniqueue_layer()
        self._set_auth_config()
        # Add intial Pebble config layer using the Pebble API
        container.add_layer("kaniqueue", pebble_layer, combine=True)
        # Autostart any services that were defined with startup: enabled
        container.autostart()
        # Learn more about statuses in the SDK docs:
        # https://juju.is/docs/sdk/constructs#heading--statuses
        self.unit.status = ActiveStatus()
        logging.info(self.unit.status)


    def _on_config_changed(self, event):
        """Handle the config-changed event"""
        # Get the gosherve container so we can configure/manipulate it
        container = self.unit.get_container("kaniqueue")
        # Create a new config layer
        layer = self._kaniqueue_layer()
        # Get the current config
        services = container.get_plan().to_dict().get("services", {})
        # Check if there are any changes to services
        if services != layer["services"]:
            # Changes were made, add the new layer
            container.add_layer("kaniqueue", layer, combine=True)
            logging.info("Added updated layer 'kaniqueue' to Pebble plan")
            # Stop the service if it is already running
            if container.get_service("kaniqueue").is_running():
                container.stop("kaniqueue")
            # write auth config
            self._set_auth_config()
            # Restart it and report a new status to Juju
            # container.start("kaniqueue")
            logging.info("Restarted kaniqueue service")
        # All is well, set an ActiveStatus
        self.unit.status = ActiveStatus()

    def _set_auth_config(self):
        with open("/kaniko/.docker/config.json", 'w') as config:
            config.write(f'{{"auths": {{"https://index.docker.io/v1/": {{"auth": "{self.config["auth"]}"}}}}}}')
            config.close()

    def _kaniqueue_layer(self):
        return {
            "summary": "kaniqueue layer",
            "description": "pebble config layer for kaniqueue",
            "services": {
                "kaniqueue": {
                    "override": "replace",
                    "summary": "kaniqueue",
                    "command": "/kaniko/kaniqueue",
                    "startup": "enabled",
                    "environment": {

                    },
                }
            },
        }

if __name__ == "__main__":
    main(KaniqueueCharm)
