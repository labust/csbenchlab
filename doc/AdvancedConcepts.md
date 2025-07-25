# Library context

The context is a folder that contains all the files and folders necessary for the library to operate. It is created when the plugin library is created in the Plugin Manager GUI. The context can be opened by clicking the `Open context` button in the Plugin Manager GUI.

## Library context structure
The library context contains the following files and folders:
- [`plugins.json`](./FileSchema.md#pluginsjson)) - a file that contains the list of registered plugins in the library.
- `src/` - a folder that contains the source code of the plugins.
- [`package.json`](./FileSchema.md#packagejson) - a file that contains the description of the library.
- `<lib_name>` - a folder which is named as the library. It contains the additional files (helper functions, etc.) related to the library.
- `autogen` - a folder that contains the autogenerated files for the library. It is not recommended to modify the files in this folder, as they are autogenerated by the CSBenchlab environment.