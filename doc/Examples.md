# Getting started with CSBenchlab

This document describes how to get started with CSBenchlab, a framework for control system benchmarking. It provides a step-by-step guide on how to create a library, register components, create an environment, run simulations and share
developed plugins and environments.

# Getting started from scratch

In this example, we will assume that none of the code exists. We begin by creating a new library.

In the GUI, select `Plugin manager`. Create a new library called `test_lib`. This will create a new library,
already available within the CSBenchlab environment. Next, we will create a few plugins. For completenes,
one will be developed in Matlab, one in Simulink and one in Python.

Developed plugins and supporting code can be included in the library usind the `Add file` or `Add folder`, which
inserts the selected items to the library context. To make things easier, by clicking the `Open context` button,
the code can be manually inserted to the library. More on library context can be read [`here`](./AdvancedConcepts.md#librarycontext).

Let's start by extracting the component source code from `demos/getting_started.zip` to the `src` folder in the library context.
Inside, there is the following:

- A Simulink component of the system (`system.slx`) - it is a Simulink Subsystem block with specified inputs and outputs, which enable the
  CSBenchlab interpreter to treat it as a System component.
- A first Controller component, which is implemented in `controller1.m` - a Matlab `*.m` script that implements a [`Controller.m`](../lib/classes/Controller.m) base class.
  It implements required abstract methods that define its behavior
- A second Controller component, which is implemented in `controller2.py` - finally, a `*.py` controller, that also implements a Python [`Controller.py`](../csbenchlab_py/plugin/Controller.py) base class

## Component registration
CSBenchlab requires components to be registered before usage. There are two ways to register a component:

- Plugin Manager GUI (recommended)- after selecting the library, by clicking on `Register new component` the file selector is opened. You select the file that contains the implemented plugin. In addition, if it is a `.slx` component, you have to enter the
simulink block path of the component.
- Manually - the plugin can be registered manually by selecting the library and clicking `Open context` button. Inside, there is a file named `plugins.json` which lists all the components to be registered from the selected library. Its format is further explained in [`Plugin file`](./FileSchema.md#pluginsjson)


For this example, we will register `system.slx`, `controller1.m` and `controller2.py` components.
The library context should look like this:

```
test_lib/
├── plugins.json
├── package.json
├── src/
│   ├── controller1.m
│   ├── controller2.py
│   └── system.slx
└── test_lib/
```

After registering the components (enter `demo_double_integrator` when prompted for path while registering `system.slx`), the `plugins.json` file should look like this:

```json
{
    "library": "test_lib",
    "version": "...",
    "description": "...",
    "authors": "...",
    "plugins": [
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
            "type": "file",
            "path": "src/System.slx:demo_double_integrator",
            "name": "demo_double_integrator"
        }
    ]
}
```
The registered components are then available in the CSBenchlab environment and are displayed in the GUI.
You can now close the Plugin Manager GUI.


## Environment creation
Now that we have the components registered, we can create an ['Environment'](./Concepts.md#environment).
In the GUI, click on `New control environment`. This will open a dialog where you can input the name of the environment and select the path where the environment will be created.
For this example, we will name the environment `test_env` and create it in the arbitrary path on your computer.


The Environment Manager GUI will open. First, we will add the System component. Click on the `System` node in the tree view on the left side of the GUI. Click on the `Select system` button and select the `demo_double_integrator` component defined in the `test_lib`. This will add the System component to the Environment. By clicking on `Save changes`, the system configuration will be saved to the Environment.


Now click on the `Controllers` node in the tree view. Click on the `Add controller` button. By clicking on the `Select controller` button, you can select the `Controller1` component from the `test_lib`. This will add the Controller component to the Environment. The controller parameters with their default values will be displayed in the bottom part of the GUI. You can modify the parameters as needed. To modify the controller parameters, click on the `Save to workspace` button, which will save the parameters to the matlab workspace. You can then modify the parameters in the workspace and click on the `Load from workspace` (or `Refresh parameters`) button to load the modified parameters back to the Environment. Finally, click on the `Save changes` button to save the controller configuration to the Environment.

To add the second controller, click on the `Controllers` node in the tree view and `Add controller` button again and select the `Controller2` component from the `test_lib`. The same procedure as for the first controller can be followed to configure the second controller.


Now, we define the environment experiments. Click on the `Experiments` node in the tree view. Click on the `Add experiment` button. This will create a new experiment with the default name `New_experiment`. In this example, we will leave it as `Experiment1`. The ['Experiment'](./Concepts.md#experiment) is described by the system initial conditions, system parameters and the reference signals. Insert `[0, 0]` as the system initial condition, which means that the system starts at rest. By default, the reference signals include `Zero` and `Step` references. Click on the `Select reference` and select the `Step` reference, which can be parametrized as described [here](./MatlabModel.md#stepreferenceparams). The reference parameters are stored as the `RefParams` field of the `Experiment` parameters. By clicking the `Save to workspace` button, the parameters will be saved to the matlab workspace. You can modify the parameters in the workspace and click on the `Load from workspace` (or `Refresh parameters`) button to load the modified parameters back to the Environment. Finally, click on the `Save changes` button to save the experiment configuration to the Environment.

Finally, we add the Metric (Plot) to be generated after successful simulation. Select `Metrics` and click on the `Add metric` button. Select `out_with_ref.m` file which is the plot that displays reference values with system output of each controller in the simulation.


After adding both controllers, the Environment tree should look like this:

```
Environment:
├── System: demo_double_integrator
├── Experiments:
│   ├── New_experiment
├── Metrics:
│   ├── New_metric
├── Controllers:
│   ├── Controller1
│   ├── Controller2
```

Finally, click on the `Environment` node in the tree view and set the `Step time` to `0.1` seconds. The simulation time is independently set for each experiment. Click on the `Save changes` button to save the Environment configuration.

## Running the Environment
Now that we have the Environment configured, we can run it. In the GUI, click on the `Generate environment` button. This will generate the Environment and create the necessary files in the Environment folder. From the opened dialog, select the list of controllers to be used in the Environment. In this example, we will select both `Controller1` and `Controller2`. Click on the `Save` button to generate the Environment. When you want to change the list of controllers, you can click on the `Generator options` button and select a different list of controllers. The Environment will be regenerated with the new list of controllers.

The simulink model of the Environment will be generated in the `test_env` folder. The model will contain the System block, which is replicated for each controller, and the Controller blocks, which are connected to the System block. The model will also contain the references and the initial conditions defined in the Environment.

Click on the `Run simulation` button in the Simulink model to run the Environment and enjoy the results and generated plots :). The evaluated metrics will be saved in the matlab workspace as the `sim_result` variable.


# Sharing components, libraries and environments

In this section, we will describe how to share the developed components, libraries and environments with other users. This is useful for collaboration and sharing the results of the experiments.

## Sharing libraries


### Exporting libraries

Open the Plugin Manager GUI and select the library you want to share. Click on the `Export library` button. This will create the `export` directory in the current Matlab working directory with the exported library files, necessary for the library to be used in other CSBenchlab environments.

### Importing libraries

Library can be imported in two ways:
- If the library is stable and ready for use, it can be registered in the Plugin Manager GUI by clicking on the `Import library` button. This will create a hard copy of the library in the CSBenchlab environment and register it for use.
- If the library is still under development, it can be imported by clicking on the `Link library` button. This will create a symbolic link to the library in the CSBenchlab environment. The library can be modified and the changes will be reflected in the CSBenchlab environment. This is useful for development and testing of the library. If new components are added to the library, by clicking on the `Refresh library` button, the new components will be registered in the CSBenchlab environment.


## Sharing components

Sharing individual component source files is not supported in CSBenchlab. Instead, components are shared as part of the library. In this context, a component is an instance of the implemented plugin (a link to the component implementation in the library), together with its parameters and configuration. The component is registered in the CSBenchlab environment and can be used in the Environment.

### Exporting components

In the Environment Manager GUI, select the component (System, Controller, etc.) you want to share. Click on the `Export <component-name>` button. This will create the `export` directory in the current Matlab working directory with the exported component files.


### Importing components

Similar to exporting components, by clicking on the `Import <component-name>` button, the component can be imported from the selected `.cdf` file, located in the exported component folder.


## Sharing environments

The entirety of the Environment information is stored in the environment folder, which is created when the Environment is generated. Sharing the Environment is done by simply sharing the environment folder.

### Exporting environments

In the Environment Manager GUI, click on the `Export environment` button. This will create the `export` directory in the current Matlab working directory with the exported environment files.

### Importing environments

In the Startup GUI, click on the `Open control environment` button. This will open a file selector dialog where you can select the `.cse` file containing the exported environment. After selecting the file, the Environment will be imported and registered in the CSBenchlab environment.
