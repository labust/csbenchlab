


def iterate_environment_components(env_info):
    for comp_type in ['systems', 'controllers', 'scenarios', 'metrics']:
        for comp in getattr(env_info, comp_type, []):
            yield comp


def iterate_environment_components_with_subcomponents(env_info):
    for c in iterate_environment_components(env_info):
        yield c
        if 'Subcomponents' in c:
            for sc_field in c['Subcomponents']:
                subc = c[sc_field]
                if isinstance(subc, list):
                    for sc in subc:
                        yield sc
                else:
                    if subc:
                        yield subc