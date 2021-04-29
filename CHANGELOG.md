Note: this changelog only lists feature additions, not bugfixes. For details on
those, see the Git history.

* v1.19
    * Add `mode:` option for `create`
    * Add `exclude:` option for `link`
* v1.18
    * Add `--only` and `--except` flags
    * Add support to run with `python -m dotbot`
    * Add `--force-color` option
* v1.17
    * Add `canonicalize-path:` option for `link`
* v1.16
    * Add `create` plugin
* v1.15
    * Add `quiet:` option for `shell`
* v1.14
    * Add `if:` option for `link`
* v1.13
    * Add `--no-color` flag
* v1.12
    * Add globbing support to `link`
* v1.11
    * Add force option to `clean` to remove all broken symlinks
* v1.10
    * Update `link` to support shorthand syntax for links
* v1.9
    * Add support for default options for commands
* v1.8
    * Update `link` to be able to create relative links
* v1.7
    * Add support for plugins
* v1.6
    * Update `link` to expand environment variables in paths
* v1.5
    * Update `link` to be able to automatically overwrite broken symlinks
* v1.4
    * Update `shell` to allow for selectively enabling/disabling stdin, stdout,
      and stderr
* v1.3
    * Add support for YAML format configs
* v1.2
    * Update `link` to be able to force create links (deleting things that were
      previously there)
    * Update `link` to be able to create parent directories
* v1.1
    * Update `clean` to remove old broken symlinks
* v1.0
    * Initial commit
