# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# enable logging for Microsoft Agents library
import logging
ms_agents_logger = logging.getLogger("microsoft_agents")
ms_agents_logger.addHandler(logging.StreamHandler())
ms_agents_logger.setLevel(logging.INFO)

from microsoft_agents.hosting.core import AgentAuthConfiguration
from .agent import AGENT_APP
from .start_server import start_server

# Create a default auth configuration since we're not using MsalConnectionManager
# This allows the server to start without authentication
auth_configuration = AgentAuthConfiguration()

start_server(
    agent_application=AGENT_APP,
    auth_configuration=auth_configuration,
)

