""" Container Details """

import docker
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from utils.constants import *  # pylint: disable=wildcard-import


class ContainerDetailsView(object):
    """ Show container details """

    def __init__(self, extension):
        self.extension = extension

    def execute(self, container_id):
        """ Show container details """

        try:
            container = self.extension.docker_client.containers.get(
                container_id)
        except docker.errors.NotFound:
            return RenderResultListAction([ExtensionResultItem(
                icon='images/icon.png',
                name="No container found with id %s" % container_id,
                highlightable=False,
                on_enter=HideWindowAction()
            )])

        items = []

        attrs = container.attrs

        ports = container.attrs['NetworkSettings']['Ports']

        ports_list = []
        for container_port, host_mapping in ports.iteritems():
            if host_mapping is not None:
                ports_str = "%s -> %s" % (container_port,  "%s:%s" % (
                    host_mapping[0]['HostIp'], host_mapping[0]['HostPort']))
                ports_list.append(ports_str)

        ip_address = container.attrs['NetworkSettings']['IPAddress']

        if not ip_address:
            ip_address = attrs['NetworkSettings']['Networks'].values()[
                0]['IPAddress']

        items.append(ExtensionResultItem(
            icon='images/icon.png',
            name=container.name,
            description=attrs['Config']['Image'],
            highlightable=False,
            on_enter=HideWindowAction()
        ))

        if container.status != 'running':
            items.append(ExtensionResultItem(
                icon='images/icon_start.png',
                name="Start",
                description="Start the specified container",
                highlightable=False,
                on_enter=ExtensionCustomAction(
                    {'action': ACTION_START_CONTAINER, 'id': container.short_id})
            ))

        if container.status == 'running':
            items.append(ExtensionResultItem(
                icon='images/icon_ip.png',
                name="IP Address",
                description=ip_address,
                highlightable=False,
                on_enter=OpenUrlAction(ip_address),
                on_alt_enter=CopyToClipboardAction(ip_address)
            ))

            items.append(ExtensionResultItem(
                icon='images/icon_ip.png',
                name="Ports",
                description='\n'.join(ports_list),
                highlightable=False,
                on_enter=HideWindowAction(),
            ))

            items.append(ExtensionResultItem(
                icon='images/icon_terminal.png',
                name="Open container shell",
                description="Opens a new sh shell in the container",
                highlightable=False,
                on_enter=RunScriptAction(
                    "x-terminal-emulator -e docker exec -it %s sh" % container.short_id, [])
            ))

            items.append(ExtensionResultItem(
                icon='images/icon_stop.png',
                name="Stop",
                description="Stops The container",
                highlightable=False,
                on_enter=ExtensionCustomAction(
                    {'action': ACTION_STOP_CONTAINER, 'id': container.short_id})
            ))

            items.append(ExtensionResultItem(
                icon='images/icon_restart.png',
                name="Restart",
                description="Restarts the container",
                highlightable=False,
                on_enter=ExtensionCustomAction(
                    {'action': ACTION_RESTART_CONTAINER, 'id': container.short_id})
            ))

            items.append(ExtensionResultItem(
                icon='images/icon_logs.png',
                name="Logs",
                description="Show logs of the container",
                highlightable=False,
                on_enter=RunScriptAction(
                    "x-terminal-emulator -e docker logs -f %s" % container.short_id, [])
            ))

        return RenderResultListAction(items)
