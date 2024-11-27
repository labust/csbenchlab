function edit_references(env_path)
    [~, name, ~] = fileparts(env_path);
    mat_path = fullfile(env_path, 'autogen', strcat(name, '_refs.mat'));
    signalEditor('DataSource', mat_path);
end