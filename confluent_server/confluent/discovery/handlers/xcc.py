# Copyright 2017 Lenovo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import confluent.discovery.handlers.imm as immhandler
import pyghmi.exceptions as pygexc
import pyghmi.ipmi.oem.lenovo.imm as imm



class NodeHandler(immhandler.NodeHandler):
    devname = 'XCC'

    def preconfig(self):
        ff = self.info.get('attributes', {}).get('enclosure-form-factor', '')
        if ff not in ('dense-computing', [u'dense-computing']):
            return
        # attempt to enable SMM
        #it's normal to get a 'not supported' (193) for systems without an SMM
        ipmicmd = None
        try:
            ipmicmd = self._get_ipmicmd()
            ipmicmd.xraw_command(netfn=0x3a, command=0xf1, data=(1,))
        except pygexc.IpmiException as e:
            if (e.ipmicode != 193 and 'Unauthorized name' not in str(e) and
                    'Incorrect password' not in str(e)):
                # raise an issue if anything other than to be expected
                raise
        #TODO: decide how to clean out if important
        #as it stands, this can step on itself
        #if ipmicmd:
        #    ipmicmd.ipmi_session.logout()

    def config(self, nodename, reset=False):
        # TODO(jjohnson2): set ip parameters, user/pass, alert cfg maybe
        # In general, try to use https automation, to make it consistent
        # between hypothetical secure path and today.
        ic = self._bmcconfig(nodename)
        ff = self.info.get('attributes', {}).get('enclosure-form-factor', '')
        if ff not in ('dense-computing', [u'dense-computing']):
            return
        # Ok, we can get the enclosure uuid now..
        ic.oem_init()
        enclosureuuid = ic._oem.immhandler.get_property(
            '/v2/ibmc/smm/chassis/uuid')
        enclosureuuid = ic._oem.immhandler.get_property(
            '/v2/ibmc/smm/chassis/uuid')
        if enclosureuuid:
            enclosureuuid = imm.fixup_uuid(enclosureuuid).lower()
            em = self.configmanager.get_node_attributes(nodename,
                                                        'enclosure.manager')
            em = em.get(nodename, {}).get('enclosure.manager', {}).get(
                'value', None)
            # ok, set the uuid of the manager...
            if em:
                self.configmanager.set_node_attributes(
                    {em: {'id.uuid': enclosureuuid}})

# TODO(jjohnson2): web based init config for future prevalidated cert scheme
#    def config(self, nodename):
#        return

