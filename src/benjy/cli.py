import click
import os
import shutil
from .utilities import compile_entity_graph, write_pickle, SourceRefs
from .schema import Schema


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


def prep_build_path(target):
    build_path = os.path.join(target, 'build')
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)
    return build_path


@cli.command("compile")
@click.argument("target", nargs=1, type=click.File('r'))
@click.pass_context
def compile(ctx, target):
    if not target:
        target = '.'
    build_path = prep_build_path(target)
    entities_path = os.path.join(build_path, 'entities.pickle')

    graph = compile_entity_graph(target)
    write_pickle(entities_path, graph)

    source_ref = SourceRefs(os.path.join(target, 'data'), build_path)
    source_ref.write_source_refs()


@cli.command("submit")
@click.option('-t', "target", type=str, default='.')
@click.pass_context
def submit(ctx, target):
    schema_path = os.path.join(target, 'schema.yaml')
    schema = Schema(schema_path)

    schema.execute()


if __name__ == "__main__":
    cli(obj={})
