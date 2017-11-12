import copy

from ansible.module_utils.basic import AnsibleModule, return_values


napalm_found = False
try:
    from napalm import get_network_driver
    napalm_found = True
except ImportError:
    pass

# Legacy for pre-reunification napalm (remove in future)
if not napalm_found:
    try:
        from napalm_base import get_network_driver     # noqa
        napalm_found = True
    except ImportError:
        pass

napalm_base_spec = {
    'hostname': dict(type='str', required=False, aliases=['host']),
    'username': dict(type='str', required=False),
    'password': dict(type='str', required=False, no_log=True),
    'dev_os': dict(type='str', required=False),
    'timeout': dict(type='int', required=False, default=60),
    'optional_args': dict(type='dict', required=False, default={}),
    'provider': dict(type='dict', required=False),
}


def create_module(module_specific_spec):
    spec = copy.deepcopy(napalm_base_spec)
    spec.update(module_specific_spec)

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if not napalm_found:
        module.fail_json(msg="the python module napalm is required")

    provider = module.params['provider'] or {}

    no_log = ['password', 'secret']
    for param in no_log:
        if provider.get(param):
            module.no_log_values.update(return_values(provider[param]))
        if provider.get('optional_args') and provider['optional_args'].get(param):
            module.no_log_values.update(return_values(provider['optional_args'].get(param)))
        if module.params.get('optional_args') and module.params['optional_args'].get(param):
            module.no_log_values.update(return_values(module.params['optional_args'].get(param)))

    # allow host or hostname
    provider['hostname'] = provider.get('hostname', None) or provider.get('host', None)
    # allow local params to override provider
    for param, pvalue in provider.items():
        if module.params.get(param) is not False:
            module.params[param] = module.params.get(param) or pvalue

    argument_check = ['hostname', 'username', 'dev_os', 'password']
    for key in argument_check:
        if module.params.get(key) is None:
            module.fail_json(msg=str(key) + " is required")

    return module


def get_connection(module):
    # open device connection
    try:
        network_driver = get_network_driver(module.params['dev_os'])
        device = network_driver(hostname=module.params['hostname'],
                                username=module.params['username'],
                                password=module.params['password'],
                                timeout=module.params['timeout'],
                                optional_args=module.params['optional_args'])
        device.open()
    except Exception as e:
        module.fail_json(msg="cannot connect to device: " + str(e))

    return device
