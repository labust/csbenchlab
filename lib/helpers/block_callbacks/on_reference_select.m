function on_reference_select
    pa = @BlockHelpers.path_append;
    handle = gcbh;

    env_name = gcs;

    env_path = fileparts(which(env_name));
   

    % if no config, this is not an environment
    if ~is_env(env_name)
        return
    end

    env_h = get_param(env_name, 'Handle');
    hws = get_param(env_h, 'modelworkspace');
    mo = get_param(handle, 'MaskObject');
    name = get_param(handle, 'Name');
    
    selector_name = pa(env_name, name, 'Reference');

    scenarios = hws.getVariable('Scenarios');

    old_active_scenario = hws.getVariable('ActiveScenario');
    
    scenario_name = mo.Parameters(1).Value;
    active_scenario_idx = 0;
    for i=1:length(scenarios)
        if strcmp(scenario_name, scenarios(i).Name)
            active_scenario_idx = i;
            break
        end
    end
    if active_scenario_idx == 0 % if not found, set first one
        active_scenario_idx = 1;
    end
    active_scenario = scenarios(active_scenario_idx);

    % if strcmp(old_active_scenario.Id, active_scenario.Id)
    %     return
    % end

    set_param(selector_name, 'ActiveScenario', fix_ref_name(active_scenario.Name));

    blocks = hws.getVariable('gen_blocks');
    sys_params = eval_component_params(blocks.systems.systems(1).Path);


    if ~isnumeric(sys_params) && ~isempty(fieldnames(sys_params))
        % override system parameters with scenario params
        f_names = fieldnames(active_scenario.Params);
        sys_params_names = fieldnames(sys_params);
        if ~isempty(f_names)
            for i=1:length(f_names)
                name = f_names{i};
                if strcmp(name, 'RefParams')
                    continue
                end
                has_name = sum(cellfun(@(x) strcmp(x, name), sys_params_names));
                if has_name
                    sys_params.(f_names{i}) = active_scenario.Params.(f_names{i});
                else
                    warning(strcat("Parameter ", name, " not defined for system."));
                end
            end
        end
    end
    if ~isfield(active_scenario.Params, 'RefParams')
        active_scenario.Params = sys_params;
    else
        ref_params = active_scenario.Params.RefParams;
        active_scenario.Params = sys_params;
        active_scenario.Params.RefParams = ref_params;
    end


    start_time = 0;
    if is_valid_field(active_scenario, 'StartTime')
        start_time = active_scenario.StartTime;
    end

    ref = load(pa(env_path, 'autogen', strcat(env_name, '_dataset_ref')));
    selected_reference = ref.(fix_ref_name(active_scenario.Name));
    selected_reference = selected_reference{1};
    if is_valid_field(active_scenario, 'EndTime')
        end_time = active_scenario.EndTime;
    else
        if isa(selected_reference, 'timeseries')
            end_time = selected_reference.Time(end) * 1.02;
        else
            end_time = selected_reference.Values.Time(end) * 1.02;
        end
    end

  
    set_param(env_name, 'StartTime', num2str(start_time), ...
        'StopTime', num2str(end_time));

    if isa(selected_reference, 'timeseries')
        global_reference = selected_reference.Data;
    else
        global_reference = selected_reference.Values.Data;
    end

    try
        hws.assignin('ActiveScenario', active_scenario);
        hws.assignin('GlobalReference', global_reference);
    catch e
    end

end


function n = fix_ref_name(n)
    n = replace(n, ' ', '_');
end