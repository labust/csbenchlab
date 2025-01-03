function m = load_env_metadata(env_path, check_path)
    if ~exist('check_path', 'var')
        check_path = 1;
    end
    if check_path && ~is_env_path(env_path)
        [env_path, ~, ~] = fileparts(which(env_path));
    end
    f = fullfile(env_path, 'config.json');
    if exist(f, "file")
        m = readstruct(f);
    else
        m = struct;
    end
end