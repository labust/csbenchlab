function params = eval_component_params(block_path)

    params = struct;
    try
        params_struct = get_struct_name(block_path);
    catch
        return
    end

    if ~model_has_tag(block_path, '__cs_ctl')
        try
            params = evalin('base', params_struct);
        catch
            params = 0;
        end
        return
    end

    parent_path = get_parent_controller(block_path);

    % if parent block is already a m-controller
    if strcmp(parent_path, block_path) 
        params = evalin('base', params_struct);
    else
        parent_params_struct = get_struct_name(parent_path);
        indices = strfind(params_struct, '.');
        if isempty(indices)
            error(strcat('No parameters set for controller', getfullname(block_path)));
        end
        try
            eval_str = strcat(parent_params_struct, '.', params_struct(indices+1:end));
            params = evalin('base', eval_str);
        catch ME
            error(strcat('Cannot evaluate parameters for controller "', ...
                getfullname(block_path), '". Cannot evaluate string: "', eval_str, '".'));
        end
    end
end

function t = get_struct_name(block_path)
    if has_mask_parameter(block_path, 'params_struct_name')
        t = get_mask_value(block_path, 'params_struct_name');
        return
    end
    t = get_mask_value(block_path, 'params');
end

