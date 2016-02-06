import sys, os.path

# We keep references to loaded modules so they don't get garbage collected.
loaded_modules = []

def load(path):
  basename = os.path.basename(path)
  module_name, extension = os.path.splitext(basename)
  plugin = load_module(module_name, path)
  loaded_modules.append(plugin)

if sys.version_info >= (3, 5):
  import importlib.util

  def load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
elif sys.version_info >= (3, 3):
  from importlib.machinery import SourceFileLoader

  def load_module(module_name, path):
    return SourceFileLoader(module_name, path).load_module()
else:
  import imp

  def load_module(module_name, path):
    return imp.load_source(module_name, path)
