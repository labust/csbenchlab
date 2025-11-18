

# ControllerOptions

Options class for defining a Controller in the Environment.

## Properties:
```
- Name : str - display name of the controlller
- Path : str - path to the controller simulink block
- Params : str - the name of the parameter structure in the workspace
- Mux : struct
    - Input : array[int] - Selection of Input dimensions from system output
    - Input : array[int] - Selection of Output dimensions to system input
- RegenerateEnv : 0/1 - Regenerate environment after controller add
- Components : array[struct]
    - Name : str - display name of the controlller
    - Path : str - path to the controller simulink block
    - Params : str - the name of the parameter structure in the workspace
    - Mux : struct
        - Input : array[int] - Selection of Input dimensions from system output
        - Input : array[int] - Selection of Output dimensions to system input
```

## Description


In general, a controller can control only the subset of the dynamical system DOFs or multiple controllers
can drive different DOFs. For this reason we classify Controllers as eather Simple or Complex.

If there is only one controller (1 type of the controller) driving the system (or any subset of the states)
we say that the Controller is Simple. Any other controller we call Complex.


### Simple Controller

In the definition of the Simple Controller, the `Components` struct can be omitted.
The rest of the properties are mandatory.

### Complex Controller

Complex Controller requires only the `Name` and `Components` to be set on the `ControllerOptions` object.
If `Components` field exists and is not empty, we treat Controller as Complex.

The Complex controller can have multiple subcontrollers, where each is defined the same way as the Simple Controller.
The Complex Controller cannot have a Complex Controller as a component, only a list of Simple Controllers.

Note: If Mux parameters of Complex Controller's components overlap, the Environment generation will result in an error.



# EnvironmentOptions

Options class for defining an Environment


## Properties

```
- Path : str - Folder path where to create the Environment
- Ts : double - Environment simulation sample time
- SystemParams : str - the name of the system parameter structure in the workspace
- SystemPath : str - Simulink model path of the system
- Controllers : array[ControllerOptions] - Controllers to use in the Environment
- Scenarios : array[Scenario] - Scenarios for the system
- References: Simulink.SimulationData.Dataset - Dataset containing scenario references
- Plots: array[Plot] - A list with ploting information
- Override: 0/1 - Override existing environment if it exists
```

# EvalParam

A class that represents the parameter to be evaluated on Environment construction

## Properties


```
- EvalFn: str - Function name to be evaluated. Result will be saved to the param value in the Controller
- EvalArgs: varargin - Additional parameters for the EvalFn to be called with
```

# Indexer

A helper class for indexing vector subspaces.

## Properties

```
- b : int - Begin index
- e : int - End index
- sz: int - Size of the vector subspace
- r: array[int] - Range of the vector
```


# IOArgument

A class that represents an Input-Output argument of the custom Matlab Class Controller

## Properties

```
- Type : 'input'/'output' - Type of the parameter
- Name : str - Parameter name
- Dim: int/struct - Dimension of the input parameter.
    If struct, a new type will be created for the input parameter.
    For every int field, create an empty array of that size
    Supports fields that are int/struct.
    Works recursively.
```

# LogEntry

A class that represents a log entry of the Matlab Class Controller

## Properties

```
- Name : str - Name of the field in data struct of the Controller. Check TODO: dodaj link
```







# ParameterDescriptor

A class that represents a parameter of the Controller or System

## Properties

```
- Name : str - Parameter name
- Required : 0/1 - Is the parameter value required or can the default be used
- DefaultValue (optional): any - Default value for the parameter. Required only if Required = 0
```


# ParameterSet

Class that describes the parameter set for the Controller or the System


## Properties

```
- Parameters : cell[ParameterDescriptor] - Parameter set
```



# RegistryInfo

Class that labels the Matlab Class Controller or System to be used with autogeneration


## Properties

```
- Name : str - Name with which to register Controller/System
- Visible: 0/1 - Skip Controller/System if set to 0
```