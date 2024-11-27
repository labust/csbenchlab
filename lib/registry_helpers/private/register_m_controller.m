function register_m_controller(info, lib_name)
    
    default_inputs = {'y_ref', 'y', 'dt'};
    default_outputs = {'u', 'log'};
    input_args = cellfun(@(x) string(x.Name), get_m_component_inputs(info.Name));
    output_args = cellfun(@(x) string(x.Name), get_m_component_outputs(info.Name));
    
    input_args_desc = create_argument_description([default_inputs, input_args, 'params', 'data']);
    output_args_desc = create_argument_description([default_outputs, output_args]);

    % params
    input_args_desc(end-1).DataType = 'ParamsType';
    input_args_desc(end-1).Scope = 'Parameter';
    input_args_desc(end).DataType = 'DataType';
    input_args_desc(end).Scope = 'Parameter';
    output_args_desc(2).DataType = 'LogEntryType';

    % set io types types
    for j=length(default_inputs):length(default_inputs)+length(input_args)-1
        input_args_desc(j).DataType = ...
            strcat(input_args_desc(j).Name, "_T");
    end
    for j=length(default_outputs):length(default_outputs)+length(output_args)-1
        output_args_desc(j).DataType = ...
            strcat(output_args_desc(j), "_T");
    end
   
    % set mask parameters
    if info.HasParameters
        params_visible = 'on';
    else
        params_visible = 'off';
    end
    mask_parameters = struct('Name', 'params', 'Prompt', 'Parameter struct:', ...
        'Value', '{block_name}_params', 'Visible', params_visible);
    mask_parameters(end+1) = struct('Name', 'data', ...
        'Value', '{block_name}_data', 'Visible', 'off', 'Prompt', '');
    mask_parameters(end+1) = struct('Name', 'ParamsType', ...
        'Value', '{block_name}_PT', 'Visible', 'off', 'Prompt', '');
    mask_parameters(end+1) = struct('Name', 'DataType', ...
        'Value', '{block_name}_DT', 'Visible', 'off', 'Prompt', '');
    mask_parameters(end+1) = struct('Name', 'LogEntryType', ...
        'Value', '{block_name}_LT', 'Visible', 'off', 'Prompt', '');
    for j=1:length(input_args)
        n = strcat(input_args{j}, '_T');
        v = strcat(info.Name, "_", input_args{j}, "_T");
        mask_parameters(end+1) = struct('Name', n, 'Value', v, 'Visible', 'off', 'Prompt', '');
    end
    for j=1:length(output_args)
        n = strcat(output_args{j}, '_T');
        v = strcat(info.Name, "_", output_args{j}, "_T");
        mask_parameters(end+1) = struct('Name', n, 'Value', v, 'Visible', 'off', 'Prompt', '');
    end

    create_m_component_simulink(info, lib_name, 'ctl', ...
        {"__cs_m_ctl"}, input_args_desc, output_args_desc, ...
        {'params', "'Data'", 'data'}, {'1', 'size(y)', 'size(y_ref)'}, [{'y_ref', 'y', 'dt'}, input_args], ...
        mask_parameters);

    generate_log_functions(info);
end


function generate_log_functions(info)

    log_desc = get_m_component_log_description(info.Name);
    autogen_path = get_app_code_autogen_path();

    f_name = strcat('gen_create_logs__', info.Name);
    
    f_path = fullfile(autogen_path, strcat(f_name, '.m'));
    if exist(f_path, 'file')
        delete(f_path);
    end

    src = "function log = " + f_name + "(data)" + newline;

    if ~isempty(log_desc) 
        for i=1:length(log_desc)
            d = log_desc{i};
            src = src + "    " + strcat('log.', d.Name, ' = data.', d.Name, ';') + newline;
        end
    else
        src = src + "    " + strcat('log = struct;') + newline;
    end

    src = src + 'end';
    fid = fopen(f_path, 'wt');
    fprintf(fid, src);
    fclose(fid);
    
end

