# EnvironmentOptions
- Id: string
- Path: string
- Ts: double
- SystemParams: struct
- SystemParamsStructName: string
- SystemName: string
- SystemType: string
- SystemLib: string
- Controllers: (ControllerOptions)[#controlleroptions]
- Scenarios: (ScenarioOptions)[#scenarioptions]
- References: (ReferenceOptions)[#referenceoptions]
- Plots: (PlotOptions)[#plotoptions]
- Override: bool


# ControllerOptions
- Id: string
- Name: string
- IsComposable: bool
- Components: ComponentOptions[]
- Estimator: (EstimatorOptions)[#estimatoroptions]
- Disturbance: (DisturbanceOptions)[#disturbanceoptions]
- Params: struct
- ParamsStructName: string
- Type: string
- Lib: string
- Mux: struct
- RefHorizon: int



# EstimatorOptions
- Id: string
- Name: string
- Params: struct
- ParamsStructName: string
- Type: string
- Lib: string

# DisturbanceOptions
- Id: string
- Name: string
- Params: struct
- ParamsStructName: string
- Type: string
- Lib: string


# StepReferenceParams
- t_sim: double
- dim: int
- amplitude: double