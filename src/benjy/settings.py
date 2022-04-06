import confuse
import os

from dataclasses import dataclass
from diskcache import Cache


@dataclass
class DefaultContext:
    name: str = "default"


remote_config = {"repository_url": str}


local_config = {"directory": confuse.Path()}


config_template = {
    "contexts": confuse.MappingValues(confuse.OneOf([remote_config, local_config]))
}


def new_context(context, repo_url):
    return {context: {"repository_url": repo_url}}


config = confuse.LazyConfig("benjy", __name__)
config.get(config_template)

cache = Cache(os.path.join(config.config_dir(), "cache"))
