function logs = get_m_component_log_description(class_name)
    logs = {};
    try
        eval(strcat("logs = ", class_name, ".log_description;"));
    catch ME
    end
end
