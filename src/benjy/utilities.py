import networkx as nx
import yaml
import os
import glob
import pickle
import itertools
from .entities import built_entity_id


def read_yaml(file):
    with open(file, 'r') as f:
        data = f.read()
        res = yaml.safe_load(data)
    return res


def write_pickle(file, obj):
    with open(file, 'wb') as f:
        pickle.dump(obj, f)


def read_pickle(file):
    with open(file, 'rb') as f:
        obj = pickle.load(f)
    return obj


def file_ref(file):
    name = os.path.splitext(os.path.basename(file))[0]
    return f"default.{name}"


class SourceRefs:
    def __init__(self, data_target, build_target):
        self.data_target = data_target
        self.file_name = 'source_ref.pickle'
        self.build_target = build_target
        self.source_refs = self.build_source_refs()

    def build_source_refs(self):
        data_target = os.path.join(self.data_target, 'data')
        base_queries = ["*.*"]
        path_queries = ['', '**']
        glob_queries = (os.path.join(self.data_target, path, base) for base in base_queries for path in path_queries)
        files = itertools.chain(*(glob.iglob(query) for query in glob_queries))
        source_refs = {file_ref(file): file for file in files}
        return source_refs

    @property
    def ref_file(self):
        return os.path.join(self.build_target, self.file_name)

    def write_source_refs(self):
        write_pickle(self.ref_file, self.source_refs)

    def load_source_ref(self):
        return read_pickle(self.ref_file)


def compile_entity_graph(folder):
    entity_files = glob.glob(os.path.join(folder, 'entities', '*.yaml'))

    nodes = [read_yaml(file) for file in entity_files]

    graph_dict = {}
    edge_data = {}
    node_data = {}
    for node in nodes:
        namespace = node.get('namespace', 'default')
        for entity in node['entities']:
            name = f"{namespace}.{entity['name']}"
            graph_dict.setdefault(name, {})
            node_data[name] = {'source': built_entity_id(entity['source']), 'column': entity['column']}
            for relation in entity.get('relations', []):
                rel_name = f"{relation.get('namespace', 'default')}.{relation['name']}"
                graph_dict[name] = {rel_name: rel_name}

                edge_key = (name, rel_name)
                edge_values = relation['crosswalk']
                if 'source' in edge_values:
                    edge_values['source'] = built_entity_id(edge_values['source'])
                edge_data[edge_key] = edge_values

    graph = nx.DiGraph(graph_dict)
    nx.set_edge_attributes(graph, edge_data)
    nx.set_node_attributes(graph, node_data)
    return graph


def process_source(source):
    if isinstance(source, str):
        s = f'default.{source}'
    elif isinstance(source, dict):
        s = f"{source['namespace']}.{source['name']}"
    else:
        raise Exception("Unrecognized source type")
    return s


