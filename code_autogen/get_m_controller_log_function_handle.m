function fh = get_m_controller_log_function_handle(class_name)
    if strcmp(class_name, "ATDeePC")
        fh = @gen_create_logs__ATDeePC;
    elseif strcmp(class_name, "ATDeePC_tune")
        fh = @gen_create_logs__ATDeePC_tune;
    elseif strcmp(class_name, "DeePC")
        fh = @gen_create_logs__DeePC;
    elseif strcmp(class_name, "DeePCPI")
        fh = @gen_create_logs__DeePCPI;
    elseif strcmp(class_name, "PID")
        fh = @gen_create_logs__PID;
    else
        error("Unknown class type")
    end
end