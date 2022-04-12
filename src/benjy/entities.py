import networkx as nx
from functools import singledispatch
from typing import Any


def get_edges(G, a, b):
    path = nx.shortest_path(G, a, b)
    return zip(path[0:-1], path[1:])


def find_node(G, attrs):
    for node in G.nodes:
        if all(G.nodes[node][k] == v for k, v in attrs.items()):
            return node

    raise Exception(f"No matching node for {attrs}")


@singledispatch
def build_entity_id(entity: Any):
    raise Exception(
        f"No implementation of build_entity_id for arguments of type {type(entity)}"
    )


@build_entity_id.register
def _(entity: dict):
    return f"{entity.get('namespace', 'default')}.{entity['name']}"


@build_entity_id.register
def _(entity: str):
    return f"default.{entity}"


def entity_node_id(entity):
    return build_entity_id(entity["entity"])


def crosswalk(driver, source_ref, graph):
    def traverse_edge(edge, table, merge_on):
        needed_values = [edge[target] for target in ["from", "to"]]
        cross_walk = driver.load(source_ref[edge["source"]], usecols=needed_values)

        # not using driver
        table = table.merge(
            cross_walk, how="left", left_on=merge_on, right_on=edge["from"]
        )
        table = table.drop(columns=[edge["from"], merge_on])
        return table, edge["to"]

    def inner(table, target_node, source, source_column):
        source_node = find_node(graph, {"source": source, "column": source_column})
        edges = get_edges(graph, source_node, target_node)
        edge = next(edges)
        table, source_column = traverse_edge(graph.edges[edge], table, source_column)
        for edge in edges:
            table, source_column = traverse_edge(
                graph.edges[edge], table, source_column
            )
        return table

    return inner


def crosswalk_entities(driver, source_ref, graph, entities):
    crosswalk_fn = crosswalk(driver, source_ref, graph)

    def inner(table, source):
        for entity in entities:
            target_node = entity_node_id(entity)
            source_column = entity["origin"][source]
            table = crosswalk_fn(table, target_node, source, source_column)
        return table

    return inner
