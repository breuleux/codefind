from .registry import CodeRegistry, ConformException  # noqa: F401
from .version import version  # noqa: F401

code_registry = CodeRegistry()
code_registry.setup()

collect_all = code_registry.collect_all
conform = code_registry.conform
find_code = code_registry.find_code
get_functions = code_registry.get_functions
update_cache_entry = code_registry.update_cache_entry
