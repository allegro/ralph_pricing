from collections import defaultdict

from ralph_scrooge.models import PricingService, PricingServicePlugin


def _get_pricing_services_graph(date):
    """
    Edge in graph from A to B means that A charges B (in other words, some cost
    of A is allocated on services assigned to B)
    """
    graph = defaultdict(list)
    for ps in PricingService.objects.all():
        if ps.plugin_type == PricingServicePlugin.pricing_service_fixed_price_plugin:  # noqa: E501
            continue
        for dep in ps.get_dependent_services(date):
            graph[dep].append(ps)
    return dict(graph)


def _detect_cycles(node, graph, visited, ps_stack):
    """
    Perform DFS on PricingServices dependecy graph looking for cycles

    Params:
        node: PricingService
        graph: dict with adjacency list of PricingServices
        visited: set of already visited PricingServices during graph traversal
        ps_stack: stack of PricingServices in current traversal (top->down)
    Returns:
        list of lists of PricingServices (or empty list if there's no cycle)
    """
    try:
        index = ps_stack.index(node)
        cycle = ps_stack[index:] + [node]
        return [cycle]
    except ValueError:
        pass
    if node in visited:
        return []
    visited.add(node)
    ps_stack.append(node)
    cycles = []
    for dep in graph.get(node, []):
        dep_cycles = _detect_cycles(dep, graph, visited, ps_stack)
        cycles.extend(dep_cycles)
    ps_stack.pop()
    return cycles


def detect_cycles(date):
    """
    Detect if there is cycle in charging between PricingServices for given date

    Loop means, that PricingService A charges PricingService B (one or more)
    which, at the end, charge back PricingService A (precisely services from
    PricingService A).
    """
    graph = _get_pricing_services_graph(date)
    visited = set()
    ps_stack = []
    cycles = []
    # try to detect loop starting from every PricingService
    for node in graph.keys():
        cycles.extend(_detect_cycles(node, graph, visited, ps_stack))
    return cycles
