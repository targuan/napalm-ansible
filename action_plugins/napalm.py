from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re
import time
import glob

from ansible.plugins.action.normal import ActionModule as _ActionModule

import ansible.constants as C

class ActionModule(_ActionModule):
    def run(self, tmp=None, task_vars=None):
        pc = self._play_context

        provider = self._task.args.get('provider', {})

        provider['hostname'] = provider.get('hostname', provider.get('host', pc.remote_addr))

        if hasattr(pc, 'connection_user'):
            provider['username'] = provider.get('username', pc.connection_user)
        else:
            # don't use pc.remote_user as this has been overwriten due to connection local
            provider['username'] = provider.get('username', C.DEFAULT_REMOTE_USER) or pc.remote_user
        provider['password'] = provider.get('password', pc.password)
        provider['timeout'] = provider.get('timeout', pc.timeout)

        self._task.args['provider'] = provider

        result = super(ActionModule, self).run(tmp, task_vars)
        return result
