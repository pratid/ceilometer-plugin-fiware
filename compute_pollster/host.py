#
# Copyright 2015 CREATE-NET <abroglio AT create-net DOT org>
#
# Author: Attilio Broglio <abroglio AT create-net DOT org>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ceilometer
from ceilometer.openstack.common import log
from ceilometer.compute import pollsters
from ceilometer.compute.pollsters import util
from ceilometer.compute.virt import inspector as virt_inspector
from ceilometer.i18n import _, _LW
from ceilometer import sample
from oslo.utils import timeutils
from oslo.config import cfg
from novaclient import client

LOG = log.getLogger(__name__)


class HostPollster(pollsters.BaseComputePollster):

    @staticmethod
    def get_samples(manager, cache, resources):
        nt = client.Client(
            version=2,
            username=cfg.CONF.service_credentials.os_username,
            api_key=cfg.CONF.service_credentials.os_password,
            project_id=cfg.CONF.service_credentials.os_tenant_name,
            auth_url=cfg.CONF.service_credentials.os_auth_url,
            region_name=cfg.CONF.service_credentials.os_region_name)

        LOG.debug(_('checking host %s'), cfg.CONF.host)
        try:
            hostInfo = nt.hosts.get(cfg.CONF.host)
            hostArray = []
            if len(hostInfo)>=3:
                #total
                hostArray.append({ 'name':'ram.tot','unit':'MB','value':(hostInfo[0].memory_mb if hostInfo[0].memory_mb else 0)})
                hostArray.append({ 'name':'disk.tot','unit':'GB','value':(hostInfo[0].disk_gb  if hostInfo[0].disk_gb  else 0)})
                hostArray.append({ 'name':'cpu.tot','unit':'cpu','value':(hostInfo[0].cpu if hostInfo[0].cpu else 0)})
                #now
                hostArray.append({ 'name':'ram.now','unit':'MB','value':(hostInfo[1].memory_mb if hostInfo[1].memory_mb else 0)})
                hostArray.append({ 'name':'disk.now','unit':'GB','value':(hostInfo[1].disk_gb if hostInfo[1].disk_gb else 0)})
                hostArray.append({ 'name':'cpu.now','unit':'cpu','value':(hostInfo[1].cpu if hostInfo[1].cpu else 0)})
                #max
                hostArray.append({ 'name':'ram.max','unit':'MB','value':(hostInfo[2].memory_mb if hostInfo[2].memory_mb else 0)})
                hostArray.append({ 'name':'disk.max','unit':'GB','value':(hostInfo[2].disk_gb  if hostInfo[2].disk_gb  else 0)})
                hostArray.append({ 'name':'cpu.max','unit':'cpu','value':(hostInfo[2].cpu if hostInfo[2].cpu else 0)})

            for host in hostArray:
                yield sample.Sample(
                    name="compute.node."+host['name'],
                    type="gauge",
                    unit=host['unit'],
                    volume=host['value'],
                    user_id=None,
                    project_id=None,
                    resource_id=cfg.CONF.host+'_'+cfg.CONF.host,
                    timestamp=timeutils.isotime(),
                    resource_metadata={}
                )

        except Exception as err:
            LOG.exception(_('could not get info for host %(host)s: %(e)s'),
                {'host': cfg.CONF.host, 'e': err})
