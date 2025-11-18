# Plugins json
```json
{
    "library": "<lib-name>",
    "version": "<lib-versuin>",
    "description": "<lib-descriptino>",
    "authors": "<lub-author>",
    "plugins": [ // list of registered plugins
        // the type can be either 'file' or 'folder_scan'
        // type 'file' detects the single component defined in the given path
        // type 'folder_scan' searches all files (recursively) in the given folder
        // path and automatically registers all the defined plugins. The plugin name is
        // set to the file name.
        {
            "type": "file",
            "path": "src/Controller1.m",
            "name": "Controller1"
        },
        {
            "type": "file",
            "path": "src/Controller2.py",
            "name": "Controller2"
        },
        {
            // following the file path, the slx plugin has to define
            // a simulink block path inside the simulink model like bellow
            "type": "file",
            "path": "src/System.slx:demo_double_integrator",
            "name": "demo_double_integrator"
        }
        {
            "type": "folder_scan",
            "path": "src/folder_components,
        },
    ]
}
```

# Package json
```json
{
    "library": "<lib-name>",
    "version": "<lib-version>",
    "authors": "<lib-authors>",
    "description": "<lib-description>",
    "license": "<lib-license>",
    "dependencies": {
        // list of dependencies for the library
        // the key is the library name, the value is the version
        "CSBenchlab": ">=0.1.0"
    }
}
```