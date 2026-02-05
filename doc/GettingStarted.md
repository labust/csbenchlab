## Getting started with CSBenchLab

This guide will help you get started with CSBenchLab. Follow the steps below to install the necessary dependencies and launch the GUI.


### Prerequisites
Make sure you have the following software installed on your system:
- **Python**: Version 3.8 or newer
- **Python Packages**: Install the following packages using pip:
  ```bash
  pip install PyQt6 numpy scipy matplotlib bdsim
  ```

In addition, for MATLAB/Simulink backend support, ensure you have:
- **MATLAB**: Version 2022b or newer
- **Simulink Coder**: Required for Simulink backend support
- **MATLAB Engine API for Python**: Follow the instructions in the [official documentation](https://www.mathworks.com/help/matlab/matlab-engine-for-python.html) to set up the MATLAB Engine API for Python.


## Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/labust/csbenchlab
    cd csbenchlab
    ```
2. **Install CsBenchLab using pip**:
    ```bash
    pip install -e .
    ```
3. **Run the GUI**:
    Start the app by running:
    ```
        csbenchlab
    ```
4. **Select backend**:
    In the GUI, select the desired backend (Python or MATLAB) from the settings menu.

5. **Load libraries**:
    Libraries for controllers and systems can be loaded using the Plugin Manager in the GUI.
    Common libraries are available in a separate repository [csbenchlab-gym/libs](https://github.com/labust/csbenchlab_gym).

6. a) **Start Benchmarking from scratch**:
    Follow the instructions in [Examples](doc/Examples.md), and start benchmarking your controllers against various dynamical systems.

    b) **Load an example project**:
    Control environments and scenarios can be loaded from example project files available in the [csbenchlab-gym/envs](https://github.com/labust/csbenchlab_gym).

## Additional Resources
- [Concepts](./Concepts.md): Learn about the core concepts of CSBenchLab.
- [Examples](doc/Examples.md): Explore example setups and use cases.