function resolved = make_slx_component_params(comp_name, comp_type, lib)
    

    if ~exist('param_values', 'var')
        param_values = struct;
    end
    
    if comp_type == 1
        e = 'sys';
    elseif comp_type == 2
        e = 'ctl';
    elseif comp_type == 3
        e = 'est';
    elseif comp_type == 4
        e = 'dist';
    end
    
    reg = get_app_registry_path();
    model_name = strcat(lib, '_', e);
    slx_path = fullfile(reg, lib, model_name);
    load_system(slx_path);

    h = getSimulinkBlockHandle(fullfile(model_name, comp_name));
    
    mo = get_param(h, 'MaskObject');
    
    resolved = struct;
    for i=1:length(mo.Parameters)
        p = mo.Parameters(i);
        if strcmp(p.Visible, 'on')
            resolved.(p.Name) = p.Value;
        end
    end
    close_system(slx_path);

end