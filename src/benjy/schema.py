from typing import Any
from functools import cached_property, cache, singledispatch
import os
from .utilities import read_yaml, process_source, read_pickle
from .drivers.main import get_driver
from .utilities import build_entity_id
from .entities import crosswalk_entities
from .datatypes import get_data_type


@singledispatch
def column_origin(origin: Any, source: str):
    raise Exception(f"No implementation for type {type(origin)} on columns.origin")


@column_origin.register
def _(origin: str, source: str):
    return origin


@column_origin.register
def _(origin: dict, source: str):
    return origin[source]


class Schema:
    def __init__(self, schema_file):
        schema = read_yaml(schema_file)
        self.build_directory = os.path.join(os.path.dirname(schema_file), "build")
        self.driver_id = schema.get("driver")
        self.driver = get_driver(self.driver_id)
        self.sources = [process_source(s) for s in schema.get("sources")]
        self.table_name = schema.get("name")
        self.columns = schema.get("columns")
        for obj in self.columns:
            if "type" in obj:
                obj["type"] = get_data_type(**obj["type"])

            if isinstance(obj["origin"], list):
                obj["origin"] = {
                    build_entity_id(source): source["value"] for source in obj["origin"]
                }
            elif isinstance(obj["origin"], str):
                obj["origin"] = {source: obj["origin"] for source in self.sources}

            else:
                raise Exception(
                    f"Unsupported values definition for 'origin' in {schema_file}"
                )
        self.output_destination = schema.get("target")

        assert not any({"type", "entity"}.isdisjoint(x.keys()) for x in self.columns)

    @cached_property
    def entity_graph(self):
        return read_pickle(os.path.join(self.build_directory, "entities.pickle"))

    @cached_property
    def source_refs(self):
        return read_pickle(os.path.join(self.build_directory, "source_ref.pickle"))

    @cache
    def needed_columns(self, source):
        return [column_origin(obj["origin"], source) for obj in self.columns]

    @cache
    def column_names(self, source):
        return {
            obj["origin"][source]: obj["name"]
            for obj in self.columns
            if "entity" not in obj
        }

    def requires_aggregation(self):
        agg_keys = {"keyed"}
        if any(not agg_keys.isdisjoint(obj.keys()) for obj in self.columns):
            return True

    def execute(self):
        """
        1. Load source data & rename
        2. Build entities
        3. Validate types
        4. Aggregate
        5. Merge
        """
        entities = [entity for entity in self.columns if "entity" in entity]
        data = (
            (self.driver.load(self.source_refs.get(source_id)), source_id)
            for source_id in self.sources
        )
        data = (
            (
                self.driver.select(
                    table, self.needed_columns(source_id), self.column_names(source_id)
                ),
                source_id,
            )
            for table, source_id in data
        )

        if len(entities) > 0:
            crosswalker = crosswalk_entities(
                self.driver, self.source_refs, self.entity_graph, entities
            )
            data = (
                (crosswalker(table, source_id), source_id) for table, source_id in data
            )

        data = self.driver.concat((data for data, _ in data))

        for obj in self.columns:
            if "type" in obj:
                data = self.driver.assign_type(data, obj["name"], obj["type"])

        agg_keys = []
        aggregates = {}
        for obj in self.columns:
            name = obj["name"]
            if "keyed" in obj:
                agg_keys.append(name)
            elif "type" in obj and obj["type"].aggregates_on:
                agg_keys.append(name)
            else:
                aggregates[name] = sum
        if len(agg_keys) > 0:
            data = self.driver.aggregate(data, agg_keys, aggregates)

        data = data[[obj["name"] for obj in self.columns]]
        self.driver.write(data, self.output_destination)
