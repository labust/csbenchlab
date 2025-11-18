### Implementation specifics

Matlab and Simulink require the types to be static while the simulation is running. To ensure that
and to speed up the compilation times, we define the struct named `data` that is required for every
Matlab Class Controller. This struct defines the controller data model. It contains and persists the data
over time and is accesible through `this.data`.

We require the implementation of the function `create_data_model` where the data struct is first initialized.
Make sure that you initialize all the values you plan to use in the controller with the correct types
and dimensions.


The Matlab Class Controller offeres four constant properties to be implemented:

1) param_description
    - defines the parameter set for this controller
2) registry_info
    - register this controller for Simulink autogeneration and give it a name
    - recommended is to use the same name as the Matlab Class name
3) log_description
    - define the names of the fields in the `data` struct you want to log
    - only logged data can be accessible when the simulation ends
    - listing names that are not present in the `data` struct after the
      `create_data_model` function is called will result in an error
4) io_description
    - if your controller requires additional inputs, you can specify them here

